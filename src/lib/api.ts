class API {
  private port: string = '';

  setPort(port: string) {
    this.port = port;
    console.log('API connected to port:', port);
  }

  private getUrl(path: string) {
    return `http://127.0.0.1:${this.port}${path}`;
  }

  // GET request
  async get<T>(path: string): Promise<T> {
    const response = await fetch(this.getUrl(path));
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
    return response.json();
  }

  // POST request
  async post<T>(path: string, data: any): Promise<T> {
    const response = await fetch(this.getUrl(path), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
    return response.json();
  }

  // Stream response (for chat)
  async *stream(path: string, data: any): AsyncGenerator<string> {
    const response = await fetch(this.getUrl(path), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value);
      const lines = text.split('\n');

      for (const line of lines) {
        if (line.trim()) {
          yield line;
        }
      }
    }
  }
}

export const api = new API();
