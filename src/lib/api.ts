export class ApiError extends Error {
  code: string;
  details?: unknown;
  status?: number;

  constructor(message: string, code: string, details?: unknown, status?: number) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.details = details;
    this.status = status;
  }
}

class API {
  private port: string = '';
  private token: string = '';
  private activeHost: string | null = null; // Caches the working host (127.0.0.1 or localhost)

  setPort(port: string) {
    if (!port) {
      console.warn('API: Attempted to set empty port');
      return;
    }
    this.port = port;
    console.log('API: Connected to port:', port);
    // Reset active host when port changes to re-verify connectivity
    this.activeHost = null;
  }

  setToken(token: string) {
    if (!token) {
      console.warn('API: Attempted to set empty token');
      return;
    }
    this.token = token;
    console.log('API: Auth token set');
  }

  private getUrl(path: string, hostOverride?: string) {
    if (!this.port) {
      console.error('API: Attempted to construct URL before port was initialized');
      throw new Error('Connection Error: Sidecar port not initialized. Is the backend running?');
    }
    const host = hostOverride || this.activeHost || '127.0.0.1';
    return `http://${host}:${this.port}${path}`;
  }

  private getHeaders() {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (this.token) {
      headers['X-Sidecar-Token'] = this.token;
    }
    return headers;
  }

  // Core request executor with retry logic
  private async executeRequest(path: string, options: RequestInit): Promise<Response> {
    const tryFetch = async (host: string, attempt = 1, maxRetries = 3): Promise<Response> => {
      const url = this.getUrl(path, host);
      const response = await fetch(url, options);

      if (!response.ok) {
        // Handle 429 Too Many Requests with Exponential Backoff
        if (response.status === 429 && attempt <= maxRetries) {
          const delay = 1000 * Math.pow(2, attempt - 1);
          console.warn(
            `API: 429 Too Many Requests. Retrying in ${delay}ms... (Attempt ${attempt}/${maxRetries})`
          );
          await new Promise((resolve) => setTimeout(resolve, delay));
          return tryFetch(host, attempt + 1, maxRetries);
        }

        // Clone to read error body without consuming the main response stream (though we throw anyway)
        const errorBody = await response.clone().json().catch(() => ({}));

        if (errorBody.code) {
          throw new ApiError(
            errorBody.message || 'API Error',
            errorBody.code,
            errorBody.details,
            response.status
          );
        }

        // Fallback for legacy errors or generic 500s without our structure
        const message = errorBody.detail || errorBody.message || response.statusText;
        throw new ApiError(
          `API Error: ${response.status} ${message}`,
          'UNKNOWN_ERROR',
          errorBody,
          response.status
        );
      }
      return response;
    };

    // 1. Try activeHost if available
    if (this.activeHost) {
      try {
        return await tryFetch(this.activeHost);
      } catch (error) {
        // If it's a specific API Error (like 400 Bad Request), don't retry - just throw
        if (error instanceof ApiError) {
          throw error;
        }
        console.warn(`API: Request to activeHost ${this.activeHost} failed. Retrying with fallback...`);
        this.activeHost = null;
      }
    }

    // 2. Default attempt (127.0.0.1)
    try {
      const response = await tryFetch('127.0.0.1');
      this.activeHost = '127.0.0.1'; // Success! Cache it.
      return response;
    } catch (error: unknown) {
      // If it's a specific API Error, throw
      if (error instanceof ApiError) {
        throw error;
      }
      // If network error (e.g. Load failed), try fallback
      if (
        error instanceof TypeError &&
        (error.message.includes('Load failed') || error.message.includes('Failed to fetch'))
      ) {
        console.warn(`API: 127.0.0.1 failed, retrying with localhost...`);
        const response = await tryFetch('localhost');
        this.activeHost = 'localhost'; // Success! Cache it.
        return response;
      }
      throw error;
    }
  }

  // Helper for JSON requests
  private async fetchWithRetry<T>(path: string, options: RequestInit): Promise<T> {
    const response = await this.executeRequest(path, options);
    return response.json();
  }

  // GET request
  async get<T>(path: string): Promise<T> {
    try {
      return await this.fetchWithRetry<T>(path, {
        method: 'GET',
        headers: this.getHeaders(),
      });
    } catch (error) {
      console.error(`API Fetch Error GET ${path}:`, error);
      throw error;
    }
  }

  // POST request
  async post<T>(path: string, data: unknown): Promise<T> {
    try {
      return await this.fetchWithRetry<T>(path, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(data),
      });
    } catch (error) {
      console.error(`API Fetch Error POST ${path}:`, error);
      throw error;
    }
  }

  // DELETE request
  async delete<T>(path: string): Promise<T> {
    try {
      return await this.fetchWithRetry<T>(path, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });
    } catch (error) {
      console.error(`API Fetch Error DELETE ${path}:`, error);
      throw error;
    }
  }

  // Stream response (for chat)
  async *stream(path: string, data: unknown): AsyncGenerator<string> {
    const options = {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    };

    const response = await this.executeRequest(path, options);

    if (!response.body) throw new Error('ReadableStream not supported');

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        yield chunk;
      }
    } finally {
      reader.releaseLock();
    }
  }
}

export const api = new API();
