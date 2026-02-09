import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import Chat from './Chat';
import { useApp } from '../hooks/useApp';
import { useAgents } from '../hooks/useAgents';
import { AgentID, Agent } from '../types';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { AppContextType } from '../contexts/AppContextModel';
import { UseQueryResult } from '@tanstack/react-query';

// Mock dependencies
vi.mock('../hooks/useApp', () => ({
  useApp: vi.fn(),
}));
vi.mock('../hooks/useAgents', () => ({
  useAgents: vi.fn(),
}));
vi.mock('../hooks/useSmartScroll', () => ({
  useSmartScroll: () => ({ current: null }),
}));

describe('Chat Component Simplification', () => {
  const mockStreamChat = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();

    vi.mocked(useApp).mockReturnValue({
      geminiService: {
        streamChat: mockStreamChat,
      },
      apiKey: 'test-key',
      isApiKeySet: true,
      roadmap: null,
    } as unknown as AppContextType);

    vi.mocked(useAgents).mockReturnValue({
      data: [
        { agent_id: 'teacher', name: 'Teacher', icon: 'Bot', description: '' },
        { agent_id: 'reviewer', name: 'Reviewer', icon: 'Code', description: '' },
      ],
      isLoading: false,
    } as unknown as UseQueryResult<Agent[], Error>);
  });

  it('should NOT render the agent selection dropdown', () => {
    render(<Chat />);
    // Check for the text "Agent" which is the label for the picker
    const agentLabel = screen.queryByText(/Agent/i);
    expect(agentLabel).toBeNull();
  });

  it('should call streamChat with orchestrator agent ID when sending a message', async () => {
    mockStreamChat.mockReturnValue(
      (async function* () {
        yield 'data: {"text": "Hello"}';
      })()
    );

    const { container } = render(<Chat />);

    const input = screen.getByPlaceholderText(/Ask your sensei/i);
    fireEvent.change(input, { target: { value: 'Hello Orchestrator' } });

    // The send button is the blue one with the icon
    const sendButton = container.querySelector('button.bg-blue-600');
    if (!sendButton) throw new Error('Send button not found');

    await act(async () => {
      fireEvent.click(sendButton);
    });

    await waitFor(() => {
      expect(mockStreamChat).toHaveBeenCalledWith(
        'Hello Orchestrator',
        expect.any(Array),
        AgentID.ORCHESTRATOR,
        undefined
      );
    });
  });
});
