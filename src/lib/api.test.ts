import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// We need to mock fetch
const fetchMock = vi.fn();
vi.stubGlobal('fetch', fetchMock);

// Import the API class to test (we'll need to export the class itself or rely on the instance)
// Currently src/lib/api.ts exports `api` instance.
// But we want to test the logic inside `executeRequest`.
// Ideally we would import { API } from './api' but it's not exported.
// Let's modify src/lib/api.ts to export the class first, or just test the instance.
// Testing the instance is fine as long as we can control fetch.

import { api, ApiError } from './api';

describe('API Library', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Set port to allow requests
    api.setPort('8000');
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should throw ApiError with structured data on 400 Bad Request', async () => {
    const errorResponse = {
      code: 'VALIDATION_ERROR',
      message: 'Invalid input',
      details: { field: 'email' },
    };

    fetchMock.mockResolvedValue({
      ok: false,
      status: 400,
      statusText: 'Bad Request',
      json: async () => errorResponse,
      clone: () => ({
        json: async () => errorResponse,
      }),
    } as Response);

    try {
      await api.get('/test');
      // Should not reach here
      expect(true).toBe(false);
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      const apiError = error as ApiError;
      expect(apiError.code).toBe('VALIDATION_ERROR');
      expect(apiError.message).toBe('Invalid input');
      expect(apiError.details).toEqual({ field: 'email' });
      expect(apiError.status).toBe(400);
    }
  });

  it('should handle legacy/generic errors gracefully', async () => {
    const errorResponse = {
      detail: 'Something went wrong',
    };

    fetchMock.mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: async () => errorResponse,
      clone: () => ({
        json: async () => errorResponse,
      }),
    } as Response);

    try {
      await api.get('/test');
      expect(true).toBe(false);
    } catch (error) {
      // If the backend doesn't send "code", we might default to generic
      // We will implement this behavior next.
      expect(error).toBeInstanceOf(ApiError);
      const apiError = error as ApiError;
      expect(apiError.code).toBe('UNKNOWN_ERROR'); // Or whatever default we choose
      expect(apiError.message).toBe('API Error: 500 Something went wrong');
    }
  });

  it('should retry on network error (fetch failure)', async () => {
      // First attempt fails
      fetchMock.mockRejectedValueOnce(new TypeError('Load failed'));
      // Second attempt succeeds
      fetchMock.mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true }),
      } as Response);

      const result = await api.get('/retry-test');
      expect(result).toEqual({ success: true });
      expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it('should NOT retry on ApiError (4xx/5xx)', async () => {
      const errorResponse = { code: 'ERR', message: 'Fail' };
      fetchMock.mockResolvedValue({
          ok: false,
          status: 400,
          clone: () => ({ json: async () => errorResponse }),
      } as Response);

      try {
          await api.get('/no-retry');
      } catch (e) {
          expect(e).toBeInstanceOf(ApiError);
      }
      expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});
