import { describe, it, expect, vi, beforeEach } from 'vitest';
import { GeminiService } from './geminiService';
import { api } from '../lib/api';

// Mock api
vi.mock('../lib/api', () => ({
  api: {
    post: vi.fn(),
    stream: vi.fn(),
    get: vi.fn(),
  },
}));

describe('GeminiService', () => {
  let service: GeminiService;

  beforeEach(() => {
    service = new GeminiService('fake-key');
    vi.clearAllMocks();
  });

  it('should omit empty optional fields from payload', async () => {
    (api.post as any).mockResolvedValue({
      roadmap_id: '123',
    });
    (api.get as any).mockResolvedValue({ phases: [] });

    await service.generateRoadmap('learn rust', '', '');

    expect(api.post).toHaveBeenCalledWith('/api/roadmap/create', {
      goal: 'learn rust',
    });
  });

  it('should call roadmap create and get endpoints with correct mapping', async () => {
    (api.post as any).mockResolvedValue({
      roadmap_id: '123',
    });
    // Mock backend response with 'name' and 'id'
    (api.get as any).mockResolvedValue({
      phases: [
        {
          name: 'Phase 1',
          lessons: [{ id: 'uuid-123', name: 'Lesson 1', description: 'Desc 1' }],
        },
      ],
    });

    const result = await service.generateRoadmap('learn rust', 'beginner', 'fast');

    expect(api.post).toHaveBeenCalledWith('/api/roadmap/create', {
      goal: 'learn rust',
      background: 'beginner',
      preferences: 'fast',
    });
    expect(api.get).toHaveBeenCalledWith('/api/roadmap/123');

    // Frontend expects nested 'lessons' with 'id'
    expect(result).toEqual([
      {
        title: 'Phase 1',
        description: '',
        duration: '',
        lessons: [{ id: 'uuid-123', title: 'Lesson 1', description: 'Desc 1', status: 'pending' }],
      },
    ]);
  });

  it('should call chat stream endpoint and handle SSE format', async () => {
    const mockStream = async function* () {
      yield 'data: hello\n\n';
    };
    (api.stream as any).mockReturnValue(mockStream());

    const chunks = [];
    for await (const chunk of service.streamChat('hi', [], 'teacher', 'custom-lesson-id')) {
      chunks.push(chunk);
    }

    expect(chunks).toEqual(['hello']);
    expect(api.stream).toHaveBeenCalledWith('/api/chat/stream', {
      message: 'hi',
      lesson_id: 'custom-lesson-id',
      agent_id: 'teacher',
    });
  });

  it('should sync api key to backend', async () => {
    (api.post as any).mockResolvedValue({ success: true });

    await service.updateApiKey('new-key');

    expect(api.post).toHaveBeenCalledWith('/api/settings/api-key', {
      api_key: 'new-key',
    });
  });
});
