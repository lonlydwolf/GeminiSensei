import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { listen } from '@tauri-apps/api/event';
import { invoke } from '@tauri-apps/api/core';
import { AppRoute, AppState, RoadmapItem } from '../types';
import { GeminiService } from '../services/geminiService';
import { api } from '../lib/api';

export type SidecarStatus = 'searching' | 'connected' | 'error';

interface AppContextType extends AppState {
  // Sidecar State
  sidecarStatus: SidecarStatus;
  port: string;
  sidecarError: string | null;

  // Setters
  setApiKey: (key: string) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  setRoute: (route: AppRoute) => void;
  setUserName: (name: string) => void;
  setRoadmap: (roadmap: RoadmapItem[] | null) => void;
  geminiService: GeminiService;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider = ({ children }: { children?: ReactNode }) => {
  // Sidecar Discovery State
  const [sidecarStatus, setSidecarStatus] = useState<SidecarStatus>('searching');
  const [port, setPort] = useState('');
  const [sidecarError, setSidecarError] = useState<string | null>(null);

  // App State (from Sample)
  const [apiKey, setApiKeyState] = useState(() => localStorage.getItem('edu_api_key') || '');
  const [theme, setThemeState] = useState<'light' | 'dark'>(
    () => (localStorage.getItem('edu_theme') as 'light' | 'dark') || 'dark'
  );
  const [currentRoute, setCurrentRoute] = useState<AppRoute>(AppRoute.HOME);
  const [userName, setUserNameState] = useState(() => localStorage.getItem('edu_username') || '');

  // Roadmap persistence
  const [roadmap, setRoadmap] = useState<RoadmapItem[] | null>(() => {
    try {
      const saved = localStorage.getItem('edu_roadmap');
      return saved ? JSON.parse(saved) : null;
    } catch (e) {
      console.error('Failed to parse saved roadmap:', e);
      return null;
    }
  });

  const [geminiService] = useState(() => new GeminiService(apiKey));

  // Sidecar Discovery Logic
  useEffect(() => {
    let unlistenReady: (() => void) | null = null;
    let unlistenError: (() => void) | null = null;

    const setup = async () => {
      // 1. Listen for events
      try {
        const stopReady = await listen<string>('sidecar-ready', (event) => {
          api.setPort(event.payload);
          setPort(event.payload);
          setSidecarStatus('connected');
          setSidecarError(null);
        });
        unlistenReady = stopReady;

        const stopError = await listen<string>('sidecar-error', (event) => {
          setSidecarStatus('error');
          setSidecarError(event.payload);
        });
        unlistenError = stopError;
      } catch (e) {
        console.error('Failed to setup Tauri listeners:', e);
      }

      // 2. Poll for existing port
      try {
        const existingPort = await invoke<string | null>('get_sidecar_port');
        if (existingPort) {
          api.setPort(existingPort);
          setPort(existingPort);
          setSidecarStatus('connected');
        }
      } catch (e) {
        console.error('Failed to get sidecar port:', e);
      }
    };

    setup();

    return () => {
      if (unlistenReady) unlistenReady();
      if (unlistenError) unlistenError();
    };
  }, []);

  // Sync state to local storage and apply theme
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('edu_theme', theme);
  }, [theme]);

  useEffect(() => {
    localStorage.setItem('edu_api_key', apiKey);
    geminiService.updateApiKey(apiKey);
  }, [apiKey, geminiService]);

  useEffect(() => {
    localStorage.setItem('edu_username', userName);
  }, [userName]);

  // Persist roadmap
  useEffect(() => {
    if (roadmap) {
      localStorage.setItem('edu_roadmap', JSON.stringify(roadmap));
    }
  }, [roadmap]);

  const setApiKey = (key: string) => setApiKeyState(key);
  const setTheme = (t: 'light' | 'dark') => setThemeState(t);
  const setRoute = (r: AppRoute) => setCurrentRoute(r);
  const setUserName = (n: string) => setUserNameState(n);

  return (
    <AppContext.Provider
      value={{
        sidecarStatus,
        port,
        sidecarError,
        apiKey,
        theme,
        currentRoute,
        userName,
        roadmap,
        setApiKey,
        setTheme,
        setRoute,
        setUserName,
        setRoadmap,
        geminiService,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within an AppProvider');
  return context;
};
