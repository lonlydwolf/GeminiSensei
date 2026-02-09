import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useRoadmapPersistence } from './useRoadmapPersistence';
import { useApp } from './useApp';
import { api } from '../lib/api';

vi.mock('./useApp', () => ({
  useApp: vi.fn(),
}));

vi.mock('../lib/api', () => ({
  api: {
    get: vi.fn(),
  },
}));

describe('useRoadmapPersistence', () => {
  const setRoadmapMock = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    vi.mocked(useApp).mockReturnValue({
      setRoadmap: setRoadmapMock,
      apiKey: 'test-key',
      sidecarStatus: 'connected',
    } as unknown as ReturnType<typeof useApp>);
  });

  it('should fetch roadmap list even if no ID in localStorage', () => {
    vi.mocked(api.get).mockResolvedValue({ roadmaps: [] });
    renderHook(() => useRoadmapPersistence());
    expect(api.get).toHaveBeenCalledWith('/api/roadmap/list');
  });

  it('should fetch detailed roadmap if ID exists in list', async () => {
    localStorage.setItem('edu_active_roadmap_id', '123');
    
    // Mock sequential calls
    // First call: list
    // Second call: details
    vi.mocked(api.get)
        .mockResolvedValueOnce({ roadmaps: [{ id: '123', name: 'Test', created_at: '' }] })
        .mockResolvedValueOnce({
            phases: [{ name: 'Phase 1', lessons: [] }]
        });

    renderHook(() => useRoadmapPersistence());

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/api/roadmap/list');
      expect(api.get).toHaveBeenCalledWith('/api/roadmap/123');
    });
    
    await waitFor(() => {
        expect(setRoadmapMock).toHaveBeenCalled();
    });
  });
});
