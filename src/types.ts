export enum AppRoute {
  HOME = 'HOME',
  ROADMAP = 'ROADMAP',
  CHAT = 'CHAT',
  SETTINGS = 'SETTINGS',
}

export enum AgentID {
  TEACHER = 'teacher',
  REVIEWER = 'reviewer',
}

export enum AgentMode {
  GENERAL_TUTOR = 'General Tutor',
  CODE_REVIEWER = 'Code Reviewer',
  EL5_EXPLAINER = 'EL5 Explainer',
  QUIZ_MASTER = 'Quiz Master',
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string;
}

export interface Lesson {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'completed';
}

export interface RoadmapItem {
  title: string;
  description: string;
  duration: string;
  lessons: Lesson[];
}

export interface RoadmapRequest {
  goal: string;
  currentKnowledge: string;
  preferences: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'model';
  text: string;
  timestamp: number;
}

export interface AppState {
  apiKey: string;
  theme: 'light' | 'dark';
  currentRoute: AppRoute;
  userName: string;
  roadmap: RoadmapItem[] | null;
}
