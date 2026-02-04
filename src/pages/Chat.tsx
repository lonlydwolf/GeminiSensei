import React, { useState, useRef, useEffect } from 'react';
import { useApp } from '../contexts/AppContext';
import { ChatMessage, AgentID } from '../types';
import { useAgents } from '../hooks/useAgents';
import { useSmartScroll } from '../hooks/useSmartScroll';
import { getIconComponent } from '../lib/iconUtils';
import { parseStreamChunk } from '../lib/streamParser';
import { Send, Bot, User, Trash2, ChevronDown, BookOpen, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function Chat() {
  const { geminiService, apiKey, roadmap } = useApp();
  const { data: agents, isLoading: loadingAgents } = useAgents();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentAgentId, setCurrentAgentId] = useState<string>(AgentID.TEACHER);
  const [selectedLessonId, setSelectedLessonId] = useState<string>('');
  const messagesContainerRef = useSmartScroll<HTMLDivElement>(messages);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Set default agent when agents load if needed
  useEffect(() => {
    if (agents && agents.length > 0 && !agents.find((a) => a.id === currentAgentId)) {
      setCurrentAgentId(agents[0].id);
    }
  }, [agents]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [input]);

  const handleSend = async () => {
    if (!input.trim() || !apiKey || isLoading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      text: input,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    setIsLoading(true);

    const modelMsgId = (Date.now() + 1).toString();
    setMessages((prev) => [
      ...prev,
      { id: modelMsgId, role: 'model', text: '', timestamp: Date.now() },
    ]);

    try {
      let historyForApi = messages.map((m) => ({
        role: m.role,
        parts: [{ text: m.text }],
      }));

      const stream = geminiService.streamChat(
        input,
        historyForApi,
        currentAgentId,
        selectedLessonId || undefined
      );

      for await (const chunk of stream) {
        const parsed = parseStreamChunk(chunk);

        if (parsed.error) {
          // If we get an error chunk, replace the model message with the error
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === modelMsgId
                ? {
                    ...msg,
                    text: `Error: ${parsed.error}`,
                  }
                : msg
            )
          );
          // Stop processing the stream if it's a critical error
          break;
        }

        if (parsed.text) {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === modelMsgId ? { ...msg, text: msg.text + parsed.text } : msg
            )
          );
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'model',
          text: 'Error: Could not connect to Gemini. Please check your API Key.',
          timestamp: Date.now(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  if (!apiKey) {
    return (
      <div className='flex h-full flex-col items-center justify-center p-6 text-center'>
        <div className='mb-4 rounded-full bg-red-50 p-4 dark:bg-red-900/20'>
          <Bot size={48} className='text-red-500' />
        </div>
        <h2 className='mb-2 text-2xl font-bold'>API Key Missing</h2>
        <p className='text-gray-600 dark:text-gray-400'>
          Please go to Settings to configure your Gemini API Key.
        </p>
      </div>
    );
  }

  // Get current agent info safely
  const activeAgent = agents?.find((a) => a.id === currentAgentId);
  const ActiveIcon = activeAgent ? getIconComponent(activeAgent.icon) : Bot;

  // Find current lesson title for display
  let selectedLessonTitle = 'General Chat';
  if (selectedLessonId && roadmap) {
    for (const phase of roadmap) {
      const lesson = phase.lessons.find((l) => l.id === selectedLessonId);
      if (lesson) {
        selectedLessonTitle = lesson.title;
        break;
      }
    }
  }

  return (
    <div className='flex h-full flex-col bg-gray-50 dark:bg-gray-900'>
      {/* Header */}
      <div className='z-10 flex flex-col items-center justify-between gap-4 border-b border-gray-200 bg-white p-4 shadow-sm md:flex-row dark:border-gray-700 dark:bg-gray-800'>
        {/* Left: Agent Picker */}
        <div className='group relative z-20 w-full md:w-64'>
          <label className='mb-1 ml-1 block text-xs font-bold tracking-wider text-gray-400 uppercase'>
            Agent
          </label>
          <div className='relative'>
            <select
              value={currentAgentId}
              onChange={(e) => {
                setCurrentAgentId(e.target.value);
                setMessages([]);
              }}
              disabled={loadingAgents}
              className='w-full cursor-pointer appearance-none rounded-2xl bg-gray-100 py-2.5 pr-10 pl-10 font-medium text-gray-800 transition-colors outline-none hover:bg-gray-200 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600'
            >
              {loadingAgents ? (
                <option>Loading agents...</option>
              ) : (
                agents?.map((agent) => (
                  <option key={agent.id} value={agent.id}>
                    {agent.name}
                  </option>
                ))
              )}
            </select>
            <div className='pointer-events-none absolute top-2.5 left-3 text-gray-500'>
              {loadingAgents ? (
                <Loader2 className='animate-spin' size={18} />
              ) : (
                <ActiveIcon size={18} />
              )}
            </div>
            <ChevronDown
              className='pointer-events-none absolute top-3 right-3 text-gray-500'
              size={16}
            />
          </div>
        </div>

        {/* Right: Lesson Picker */}
        <div className='relative z-10 w-full md:w-64'>
          <label className='mb-1 ml-1 block text-xs font-bold tracking-wider text-gray-400 uppercase'>
            Focus Lesson
          </label>
          <div className='relative'>
            <select
              value={selectedLessonId}
              onChange={(e) => setSelectedLessonId(e.target.value)}
              disabled={!roadmap || roadmap.length === 0}
              className='w-full cursor-pointer appearance-none rounded-2xl border border-gray-200 bg-white py-2.5 pr-10 pl-10 font-medium text-gray-800 transition-colors outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200'
            >
              <option value=''>General Chat</option>
              {roadmap?.map((phase, i) => (
                <optgroup key={i} label={phase.title}>
                  {phase.lessons.map((lesson) => (
                    <option key={lesson.id} value={lesson.id}>
                      {lesson.title}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
            <div className='pointer-events-none absolute top-2.5 left-3 text-gray-500'>
              <BookOpen size={18} />
            </div>
            <ChevronDown
              className='pointer-events-none absolute top-3 right-3 text-gray-500'
              size={16}
            />
          </div>
        </div>
      </div>

      {/* Messages */}
      <div ref={messagesContainerRef} className='flex-1 space-y-6 overflow-y-auto p-4'>
        {messages.length === 0 && (
          <div className='flex h-full flex-col items-center justify-center text-gray-400 opacity-60'>
            <Bot size={64} className='mb-4' />
            <p>Start a conversation with {activeAgent?.name || 'the agent'}</p>
            {selectedLessonId && (
              <p className='mt-2 text-sm text-blue-500'>Focus: {selectedLessonTitle}</p>
            )}
          </div>
        )}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'model' && (
              <div className='mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-600 dark:bg-blue-900/50 dark:text-blue-400'>
                <Bot size={18} />
              </div>
            )}
            <div
              className={`max-w-[85%] rounded-3xl px-6 py-4 shadow-sm ${
                msg.role === 'user'
                  ? 'rounded-br-md bg-blue-600 text-white'
                  : 'rounded-bl-md border border-gray-200 bg-white text-gray-800 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200'
              }`}
            >
              {msg.role === 'model' ? (
                <div className='markdown-body overflow-x-auto text-sm leading-relaxed'>
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                </div>
              ) : (
                <p className='text-sm whitespace-pre-wrap'>{msg.text}</p>
              )}
            </div>
            {msg.role === 'user' && (
              <div className='mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-300'>
                <User size={18} />
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className='flex gap-4'>
            <div className='mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-600 dark:bg-blue-900/50 dark:text-blue-400'>
              <Bot size={18} />
            </div>
            <div className='flex items-center gap-2 rounded-3xl rounded-bl-md border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800'>
              <span className='h-2 w-2 animate-bounce rounded-full bg-gray-400'></span>
              <span className='h-2 w-2 animate-bounce rounded-full bg-gray-400 delay-75'></span>
              <span className='h-2 w-2 animate-bounce rounded-full bg-gray-400 delay-150'></span>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className='border-t border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800'>
        <div className='relative mx-auto flex max-w-4xl items-end gap-2 rounded-3xl border border-gray-200 bg-gray-50 p-2 shadow-sm transition-shadow focus-within:ring-2 focus-within:ring-blue-500 dark:border-gray-700 dark:bg-gray-900'>
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={`Message ${activeAgent?.name || 'the agent'}... (Shift + Enter for new line)`}
            className='max-h-[150px] w-full resize-none bg-transparent py-3 pl-4 text-sm outline-none'
            rows={1}
            disabled={isLoading}
          />
          <div className='flex flex-col gap-2 pr-1 pb-1'>
            <button
              onClick={clearChat}
              className='rounded-full p-2 text-gray-400 transition-colors hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-900/20'
              title='Clear Chat'
            >
              <Trash2 size={18} />
            </button>
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className='rounded-full bg-blue-600 p-2 text-white shadow-md transition-colors hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600'
            >
              <Send size={18} className={isLoading ? 'opacity-0' : ''} />
              {isLoading && (
                <span className='absolute inset-0 flex items-center justify-center'>
                  <span className='h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent'></span>
                </span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
