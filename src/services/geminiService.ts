import {
  RoadmapItem,
  GeminiRoadmapPayload,
  GeminiRoadmapResponse,
  GeminiHistoryItem,
} from '../types';
import { api } from '../lib/api';

export class GeminiService {
  constructor() {
    // API key managed by sidecar
  }

  async updateApiKey(key: string) {
    if (key) {
      await api.post('/api/settings/api-key', { api_key: key });
    }
  }

  async generateRoadmap(
    goal: string,
    background: string,
    preferences: string
  ): Promise<{ roadmap: RoadmapItem[]; id: string }> {
    try {
      // 1. Create roadmap via sidecar
      const payload: GeminiRoadmapPayload = { goal };
      if (background) payload.background = background;
      if (preferences) payload.preferences = preferences;

      const response = await api.post<{ roadmap_id: string }>('/api/roadmap/create', payload);

      const roadmapId = response.roadmap_id;

      // 2. Fetch detailed roadmap
      const detailedRoadmap = await api.get<GeminiRoadmapResponse>(`/api/roadmap/${roadmapId}`);

      // 3. Map backend schema to frontend RoadmapItem[]
      let roadmap: RoadmapItem[] = [];
      if (detailedRoadmap.phases && Array.isArray(detailedRoadmap.phases)) {
        roadmap = detailedRoadmap.phases.map((phase) => ({
          title: phase.name,
          description: '',
          duration: '',
          lessons: phase.lessons
            ? phase.lessons.map((l) => ({
                id: l.id || '', // Ensure id is string
                title: l.name,
                description: l.description || '',
                status: 'pending',
              }))
            : [],
        }));
      }

      return { roadmap, id: roadmapId };
    } catch (error) {
      console.error('Gemini Roadmap Error:', error);
      throw error;
    }
  }

  async *streamChat(
    message: string,
    _history: GeminiHistoryItem[],
    agentId: string,
    lessonId?: string
  ) {
    // We'll use the /api/chat/stream endpoint
    const stream = api.stream('/api/chat/stream', {
      message,
      lesson_id: lessonId || 'general',
      agent_id: agentId,
    });

    for await (const chunk of stream) {
      // Clean SSE format
      let text = chunk;
      if (text.startsWith('data: ')) {
        text = text.slice(6);
      }
      text = text.trim();

      if (!text) continue;

      // Sidecar might return JSON strings as chunks
      try {
        const data = JSON.parse(text);
        if (data.content) yield data.content;
        else if (typeof data === 'string') yield data;
      } catch {
        yield text;
      }
    }
  }
}
