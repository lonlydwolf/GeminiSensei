import { createContext } from 'react';
import { AppState, RoadmapItem, SidecarStatus, AppRoute } from '../types';
import { GeminiService } from '../services/geminiService';

export interface AppContextType extends AppState {
  // Sidecar State
  sidecarStatus: SidecarStatus;
  port: string;
  sidecarError: string | null;
  isApiKeySet: boolean;
  isApiKeyValid: boolean | null;

  // Setters
  setApiKey: (key: string) => Promise<void>;
  setTheme: (theme: 'light' | 'dark') => void;
  setRoute: (route: AppRoute) => void;
  setUserName: (name: string) => void;
  setRoadmap: (roadmap: RoadmapItem[] | null) => void;
  completeOnboarding: () => void;
  geminiService: GeminiService;
}

export const AppContext = createContext<AppContextType | undefined>(undefined);
