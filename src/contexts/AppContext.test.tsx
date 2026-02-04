import { render, screen, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AppProvider, useApp } from './AppContext';
import { listen } from '@tauri-apps/api/event';
import { invoke } from '@tauri-apps/api/core';

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
    let eventCallback: (event: { payload: string }) => void = () => {};

    (listen as any).mockImplementation((event: string, callback: any) => {
      if (event === 'sidecar-ready') {
        eventCallback = callback;
      }
      return Promise.resolve(() => {});
    });

    render(
      <AppProvider>
        <TestComponent />
      </AppProvider>
    );

    // Simulate event
    await act(async () => {
      eventCallback({ payload: '12345' });
    });

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('connected');
      expect(screen.getByTestId('port')).toHaveTextContent('12345');
    });
  });

  it('should poll for existing port on mount', async () => {
    (invoke as any).mockResolvedValue('54321');

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

  it('should initialize roadmap from localStorage', () => {
    const mockRoadmap = [{ title: 'Saved Roadmap', description: '', duration: '', lessons: [] }];
    window.localStorage.setItem('edu_roadmap', JSON.stringify(mockRoadmap));

    const TestRoadmapComponent = () => {
      const { roadmap } = useApp();
      return <span data-testid='roadmap'>{roadmap?.[0]?.title}</span>;
    };

    render(
      <AppProvider>
        <TestRoadmapComponent />
      </AppProvider>
    );

    expect(screen.getByTestId('roadmap')).toHaveTextContent('Saved Roadmap');
  });

  it('should save roadmap to localStorage when it changes', async () => {
    const mockRoadmap = [{ title: 'New Roadmap', description: '', duration: '', lessons: [] }];

    const TestActionComponent = () => {
      const { setRoadmap } = useApp();
      return <button onClick={() => setRoadmap(mockRoadmap)}>Save</button>;
    };

    render(
      <AppProvider>
        <TestActionComponent />
      </AppProvider>
    );

    await act(async () => {
      screen.getByText('Save').click();
    });

    await waitFor(() => {
      expect(window.localStorage.getItem('edu_roadmap')).toBe(JSON.stringify(mockRoadmap));
    });
  });
});
