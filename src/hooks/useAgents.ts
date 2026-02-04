import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { Agent } from '../types';

/**
 * Hook to fetch the list of available agents from the backend.
 */
export function useAgents() {
  return useQuery<Agent[]>({
    queryKey: ['agents'],
    queryFn: () => api.get<Agent[]>('/api/agents'),
    staleTime: 1000 * 60 * 60, // Cache for 1 hour
  });
}
