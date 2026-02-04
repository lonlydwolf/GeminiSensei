import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useAgents } from './useAgents';
import { api } from '../lib/api';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// Mock the API
vi.mock('../lib/api', () => ({
  api: {
    get: vi.fn(),
  },
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
);

describe('useAgents', () => {
  beforeEach(() => {
    queryClient.clear();
    vi.clearAllMocks();
  });

  it('should fetch agents successfully', async () => {
    const mockAgents = [
      { id: 'teacher', name: 'Teacher', description: 'Desc', icon: 'Icon' },
    ];
    (api.get as any).mockResolvedValue(mockAgents);

    const { result } = renderHook(() => useAgents(), { wrapper });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockAgents);
    expect(api.get).toHaveBeenCalledWith('/api/agents');
  });

  it('should handle error during fetch', async () => {
    (api.get as any).mockRejectedValue(new Error('Fetch failed'));

    const { result } = renderHook(() => useAgents(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toBeDefined();
  });
});
