import { useState, useEffect, ReactNode } from 'react';
import { listen } from '@tauri-apps/api/event';
import { invoke } from '@tauri-apps/api/core';
import { AppRoute, RoadmapItem, SidecarStatus, SidecarConfig } from '../types';
import { GeminiService } from '../services/geminiService';
import { api } from '../lib/api';
import { AppContext } from './AppContextModel';

export const AppProvider = ({ children }: { children?: ReactNode }) => {
  // Sidecar Discovery State
  const [sidecarStatus, setSidecarStatus] = useState<SidecarStatus>('searching');
  const [port, setPort] = useState('');
  const [sidecarError, setSidecarError] = useState<string | null>(null);
  const [isApiKeySet, setIsApiKeySet] = useState(false);
  const [isApiKeyValid, setIsApiKeyValid] = useState<boolean | null>(null);

  // App State (from Sample)
  const [apiKey, setApiKeyState] = useState('');
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

  const [geminiService] = useState(() => new GeminiService());

  const checkSettingsStatus = async () => {
    try {
      const status = await api.get<{ gemini_api_key_set: boolean; gemini_api_key_valid: boolean }>('/api/settings/status');
      setIsApiKeySet(status.gemini_api_key_set);
      setIsApiKeyValid(status.gemini_api_key_valid);
      setSidecarError(null); // Clear errors if status check succeeds
    } catch (e: unknown) {
      console.error('Failed to check settings status:', e);
      if (e instanceof Error && e.message?.includes('Failed to fetch')) {
        setSidecarError('Sidecar Connection Error: Backend unreachable.');
      }
    }
  };

  // Sidecar Discovery Logic
  useEffect(() => {
    let unlistenReady: (() => void) | null = null;
    let unlistenError: (() => void) | null = null;

    const setup = async () => {
      // 1. Listen for events
      try {
        const stopReady = await listen<SidecarConfig>('sidecar-ready', (event) => {
          const { port, token } = event.payload;
          api.setPort(port);
          api.setToken(token);
          setPort(port);
          setSidecarStatus('connected');
          setSidecarError(null);
          checkSettingsStatus();
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

      // 2. Poll for existing config with retry
      const pollConfig = async (retries = 5) => {
        try {
          const config = await invoke<SidecarConfig | null>('get_sidecar_config');
          if (config && config.port && config.token) {
            api.setPort(config.port);
            api.setToken(config.token);
            setPort(config.port);
            setSidecarStatus('connected');
            await checkSettingsStatus();
            return true;
          }
        } catch (e) {
          console.error('Failed to get sidecar config:', e);
        }

        if (retries > 0) {
          setTimeout(() => pollConfig(retries - 1), 1000);
        } else if (sidecarStatus === 'searching') {
          setSidecarStatus('error');
          setSidecarError('Sidecar initialization timed out.');
        }
        return false;
      };

      await pollConfig();
    };

    setup();

    return () => {
      if (unlistenReady) unlistenReady();
      if (unlistenError) unlistenError();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
    localStorage.setItem('edu_username', userName);
  }, [userName]);

  // Persist roadmap
  useEffect(() => {
    if (roadmap) {
      localStorage.setItem('edu_roadmap', JSON.stringify(roadmap));
    }
  }, [roadmap]);

  const setApiKey = async (key: string) => {
    // Attempt to update backend first
    await geminiService.updateApiKey(key);
    // If successful, update local state
    setApiKeyState(key);
    if (key) {
      setIsApiKeySet(true);
      setIsApiKeyValid(true); // Since backend now validates, success means valid
    }
  };
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
        isApiKeySet,
        isApiKeyValid,
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
