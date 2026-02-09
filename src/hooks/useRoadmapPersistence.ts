import { useEffect } from 'react';
import { useApp } from './useApp';
import { api } from '../lib/api';
import { RoadmapItem, RoadmapListResponse } from '../types';

interface RoadmapResponse {
  phases: {
    name: string;
    lessons: {
      id: string;
      name: string;
      description?: string;
      status?: string;
    }[];
  }[];
}

export function useRoadmapPersistence() {
  const { roadmap, setRoadmap, sidecarStatus } = useApp();

  useEffect(() => {
    if (sidecarStatus !== 'connected') return;

    const syncRoadmap = async () => {
      try {
        // 1. Get list of available roadmaps
        const listResponse = await api.get<RoadmapListResponse>('/api/roadmap/list');
        const roadmaps = listResponse.roadmaps;
        const savedId = localStorage.getItem('edu_active_roadmap_id');

        let targetId = savedId;
        const latest = roadmaps.length > 0 ? roadmaps[0] : null;

        if (roadmaps.length === 0) {
          // If backend is empty, but we have an ID, maybe DB was wiped?
          // We stay quiet and keep local storage data for now.
          return;
        }

        if (savedId) {
          const exists = roadmaps.find((r) => r.id === savedId);
          if (!exists) {
            if (latest) {
              console.warn('Saved roadmap not found, restoring latest.');
              targetId = latest.id;
              localStorage.setItem('edu_active_roadmap_id', latest.id);
            } else {
              // Should have been caught by roadmaps.length === 0 check
              return;
            }
          }
        } else if (latest) {
          console.log('No active roadmap ID locally, restoring latest from backend.');
          targetId = latest.id;
          localStorage.setItem('edu_active_roadmap_id', latest.id);
        }

        if (targetId) {
          const detailedRoadmap = await api.get<RoadmapResponse>(`/api/roadmap/${targetId}`);
          if (detailedRoadmap.phases && Array.isArray(detailedRoadmap.phases)) {
            const mappedRoadmap: RoadmapItem[] = detailedRoadmap.phases.map((phase) => ({
              title: phase.name,
              description: '',
              duration: '',
              lessons: phase.lessons
                ? phase.lessons.map((l) => ({
                    id: l.id || '',
                    title: l.name,
                    description: l.description || '',
                    status: l.status === 'completed' ? 'completed' : 'pending',
                  }))
                : [],
            }));

            // Only update if changed
            if (JSON.stringify(roadmap) !== JSON.stringify(mappedRoadmap)) {
              setRoadmap(mappedRoadmap);
            }
          }
        }
      } catch (err) {
        console.error('Failed to sync roadmap:', err);
      }
    };

    syncRoadmap();
  }, [setRoadmap, sidecarStatus, roadmap]);
}
