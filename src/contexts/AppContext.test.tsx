import { render, screen, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AppProvider } from './AppContext';
import { useApp } from '../hooks/useApp';
import { listen } from '@tauri-apps/api/event';
import { invoke } from '@tauri-apps/api/core';

// Mock API
vi.mock('../lib/api', () => ({
  api: {
    setPort: vi.fn(),
    setToken: vi.fn(),
    get: vi.fn().mockResolvedValue({ gemini_api_key_set: false }),
  },
}));

// Helper component to consume context
const TestComponent = () => {
  const { sidecarStatus, port } = useApp();
  return (
    <div>
      <span data-testid='status'>{sidecarStatus}</span>
      <span data-testid='port'>{port}</span>
    </div>
  );
};

describe('AppContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.localStorage.clear();
  });

  it('should initialize with searching status', () => {
    render(
      <AppProvider>
        <TestComponent />
      </AppProvider>
    );
    expect(screen.getByTestId('status')).toHaveTextContent('searching');
  });

  it('should update status when sidecar-ready event is received', async () => {
    let eventCallback: (event: { payload: unknown }) => void = () => {};

    vi.mocked(listen).mockImplementation((_event, callback) => {
      eventCallback = callback as (event: { payload: unknown }) => void;
      return Promise.resolve(() => {});
    });

    render(
      <AppProvider>
        <TestComponent />
      </AppProvider>
    );

    // Simulate event with new object structure
    await act(async () => {
      eventCallback({ payload: { port: '12345', token: 'secret' } });
    });

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('connected');
      expect(screen.getByTestId('port')).toHaveTextContent('12345');
    });
  });

  it('should poll for existing config on mount', async () => {
    vi.mocked(invoke).mockImplementation((cmd) => {
      if (cmd === 'get_sidecar_config') {
        return Promise.resolve({ port: '54321', token: 'secret' });
      }
      return Promise.resolve(null);
    });

    render(
      <AppProvider>
        <TestComponent />
      </AppProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('connected');
      expect(screen.getByTestId('port')).toHaveTextContent('54321');
    });
  });

  it('should initialize roadmap from localStorage', async () => {
    // Mock invoke to return config immediately to stop polling
    vi.mocked(invoke).mockResolvedValue({ port: '1111', token: 'test-token' });

    const mockRoadmap = [{ title: 'Saved Roadmap', description: '', duration: '', lessons: [] }];
    window.localStorage.setItem('edu_roadmap', JSON.stringify(mockRoadmap));

    const TestRoadmapComponent = () => {
      const { roadmap, sidecarStatus } = useApp();
      return (
        <div>
          <span data-testid='roadmap'>{roadmap?.[0]?.title}</span>
          <span data-testid='status'>{sidecarStatus}</span>
        </div>
      );
    };

    render(
      <AppProvider>
        <TestRoadmapComponent />
      </AppProvider>
    );

    // Wait for sidecar init to settle to avoid act warnings
    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('connected'));

    expect(screen.getByTestId('roadmap')).toHaveTextContent('Saved Roadmap');
  });

  it('should save roadmap to localStorage when it changes', async () => {
    vi.mocked(invoke).mockResolvedValue({ port: '1111', token: 'test-token' });
    const mockRoadmap = [{ title: 'New Roadmap', description: '', duration: '', lessons: [] }];

    const TestActionComponent = () => {
      const { setRoadmap, sidecarStatus } = useApp();
      return (
        <div>
          <button onClick={() => setRoadmap(mockRoadmap)}>Save</button>
          <span data-testid='status'>{sidecarStatus}</span>
        </div>
      );
    };

    render(
      <AppProvider>
        <TestActionComponent />
      </AppProvider>
    );

    // Wait for sidecar init
    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('connected'));

    await act(async () => {
      screen.getByText('Save').click();
    });

    await waitFor(() => {
      expect(window.localStorage.getItem('edu_roadmap')).toBe(JSON.stringify(mockRoadmap));
    });
  });
});
