import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { useApp } from '../hooks/useApp';
import { ChatMessage, AgentID } from '../types';
import { useSmartScroll } from '../hooks/useSmartScroll';
import { parseStreamChunk } from '../lib/streamParser';
import { Send, Bot, Trash2, ChevronDown, BookOpen, Target, Code } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function Chat() {
  const { geminiService, roadmap, isApiKeySet } = useApp();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedLessonId, setSelectedLessonId] = useState<string>('');
  const messagesContainerRef = useSmartScroll<HTMLDivElement>(messages);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [input]);

  const handleSend = async (textOverride?: string) => {
    const textToSend = textOverride || input;
    if (!textToSend.trim() || !isApiKeySet || isLoading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      text: textToSend,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textOverride) setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    setIsLoading(true);

    const modelMsgId = (Date.now() + 1).toString();
    setMessages((prev) => [
      ...prev,
      { id: modelMsgId, role: 'model', text: '', timestamp: Date.now() },
    ]);

    try {
      const historyForApi = messages.map((m) => ({
        role: m.role,
        parts: [{ text: m.text }],
      }));

      const stream = geminiService.streamChat(
        textToSend,
        historyForApi,
        AgentID.ORCHESTRATOR,
        selectedLessonId || undefined
      );

      for await (const chunk of stream) {
        const parsed = parseStreamChunk(chunk);

        if (parsed.error) {
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
    } catch (error: unknown) {
      console.error('Chat error:', error);
      const errorMessage =
        error instanceof Error && error.message?.includes('Failed to fetch')
          ? 'Connection Error: Could not reach the sidecar. Please ensure it is running.'
          : `Error: ${error instanceof Error ? error.message : 'An unexpected error occurred'}`;

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'model',
          text: errorMessage,
          timestamp: Date.now(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  if (!isApiKeySet) {
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

  const suggestionChips = [
    { label: 'Explain the core concept', icon: <BookOpen size={14} /> },
    { label: 'Give me a quiz', icon: <Target size={14} /> },
    { label: 'Show a code example', icon: <Code size={14} /> },
  ];

  return (
    <div className='flex h-full flex-col bg-white dark:bg-gray-950'>
      {/* Header */}
      <div className='z-10 flex items-center justify-between border-b border-gray-100 bg-white/80 px-6 py-3 backdrop-blur-md dark:border-gray-800/50 dark:bg-gray-950/80'>
        <div className='flex items-center gap-4'>
          <div className='hidden h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600 md:flex dark:bg-blue-900/20 dark:text-blue-400'>
            <Bot size={24} />
          </div>
          <div className='flex flex-col'>
            <span className='text-sm font-bold dark:text-white'>Sensei Orchestrator</span>
            <span className='text-[10px] font-bold tracking-widest text-blue-500 uppercase'>
              Online
            </span>
          </div>
        </div>

        <div className='flex items-center gap-3'>
          <div className='relative hidden sm:block'>
            <select
              value={selectedLessonId}
              onChange={(e) => setSelectedLessonId(e.target.value)}
              disabled={!roadmap || roadmap.length === 0}
              className='cursor-pointer appearance-none rounded-xl border border-gray-200 bg-gray-50 py-2 pr-10 pl-9 text-xs font-semibold text-gray-700 transition-all outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 disabled:opacity-50 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-300'
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
            <BookOpen className='pointer-events-none absolute top-2.5 left-3 text-gray-400' size={14} />
            <ChevronDown
              className='pointer-events-none absolute top-3 right-3 text-gray-400'
              size={12}
            />
          </div>

          <button
            onClick={clearChat}
            className='flex h-9 w-9 items-center justify-center rounded-xl border border-gray-200 text-gray-400 transition-all hover:border-red-200 hover:bg-red-50 hover:text-red-500 dark:border-gray-800 dark:hover:border-red-900/30 dark:hover:bg-red-900/20'
            title='Clear conversation'
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div
        ref={messagesContainerRef}
        className='flex-1 space-y-8 overflow-y-auto px-6 py-10'
        style={{ scrollBehavior: 'smooth' }}
      >
        {messages.length === 0 && (
          <div className='animate-in fade-in zoom-in-95 flex h-full flex-col items-center justify-center text-center duration-700'>
            <div className='mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'>
              <Bot size={40} />
            </div>
            <h2 className='text-2xl font-bold text-gray-900 dark:text-white'>
              How can I help you today?
            </h2>
            <p className='mt-2 max-w-sm text-gray-500 dark:text-gray-400'>
              I can explain complex topics, review your code, or quiz you on your current lesson.
            </p>

            <div className='mt-10 flex flex-wrap justify-center gap-3'>
              {suggestionChips.map((chip, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(chip.label)}
                  className='flex items-center gap-2 rounded-2xl border border-gray-200 bg-white px-5 py-3 text-sm font-medium text-gray-700 transition-all hover:-translate-y-0.5 hover:border-blue-400 hover:bg-blue-50 hover:text-blue-600 hover:shadow-md dark:border-gray-800 dark:bg-gray-900 dark:text-gray-300 dark:hover:border-blue-500 dark:hover:bg-blue-900/20 dark:hover:text-blue-400'
                >
                  <span className='text-blue-500'>{chip.icon}</span>
                  {chip.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex animate-in fade-in slide-in-from-bottom-2 gap-4 duration-300 ${
              msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'
            }`}
          >
            {msg.role === 'model' && (
              <div className='mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-blue-100 text-blue-600 dark:bg-blue-900/50 dark:text-blue-400'>
                <Bot size={18} />
              </div>
            )}
            <div
              className={`relative max-w-[85%] px-6 py-4 shadow-sm md:max-w-[75%] ${
                msg.role === 'user'
                  ? 'rounded-3xl rounded-tr-none bg-blue-600 text-white shadow-blue-500/10'
                  : 'rounded-3xl rounded-tl-none border border-gray-100 bg-gray-50 text-gray-800 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-200'
              }`}
            >
              {msg.role === 'model' ? (
                <div className='markdown-body prose prose-sm dark:prose-invert max-w-none text-sm leading-relaxed'>
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                </div>
              ) : (
                <p className='text-sm whitespace-pre-wrap'>{msg.text}</p>
              )}
              <span
                className={`absolute top-full mt-1.5 text-[10px] font-medium opacity-40 ${
                  msg.role === 'user' ? 'right-2' : 'left-2'
                }`}
              >
                {new Date(msg.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className='flex animate-in fade-in gap-4 duration-300'>
            <div className='mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-blue-100 text-blue-600 dark:bg-blue-900/50 dark:text-blue-400'>
              <Bot size={18} />
            </div>
            <div className='flex items-center gap-1.5 rounded-2xl rounded-tl-none border border-gray-100 bg-gray-50 px-5 py-4 dark:border-gray-800 dark:bg-gray-900'>
              <div
                className='h-1.5 w-1.5 animate-bounce rounded-full bg-blue-400'
                style={{ animationDelay: '0ms' }}
              ></div>
              <div
                className='h-1.5 w-1.5 animate-bounce rounded-full bg-blue-400'
                style={{ animationDelay: '150ms' }}
              ></div>
              <div
                className='h-1.5 w-1.5 animate-bounce rounded-full bg-blue-400'
                style={{ animationDelay: '300ms' }}
              ></div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className='border-t border-gray-100 bg-white p-6 dark:border-gray-900 dark:bg-gray-950'>
        <div className='mx-auto flex max-w-4xl items-end gap-3'>
          <div className='relative flex flex-1 items-end rounded-2xl border border-gray-200 bg-gray-50 transition-all focus-within:border-blue-400 focus-within:ring-4 focus-within:ring-blue-500/5 dark:border-gray-800 dark:bg-gray-900 dark:focus-within:border-blue-500'>
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Ask your sensei anything...`}
              className='max-h-[150px] w-full resize-none bg-transparent py-4 pr-4 pl-5 text-sm leading-relaxed outline-none dark:text-white'
              rows={1}
              disabled={isLoading}
            />
          </div>

          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            className='flex h-[54px] w-[54px] shrink-0 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-500/20 transition-all hover:-translate-y-0.5 hover:bg-blue-700 hover:shadow-blue-500/40 active:translate-y-0 disabled:translate-y-0 disabled:opacity-50 disabled:shadow-none dark:bg-blue-500 dark:hover:bg-blue-400'
          >
            {isLoading ? (
              <span className='h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent' />
            ) : (
              <Send size={20} className='-mr-0.5 mt-0.5' />
            )}
          </button>
        </div>
        <p className='mt-3 text-center text-[10px] font-medium text-gray-400 dark:text-gray-600'>
          Press <kbd className='rounded border border-gray-200 px-1 dark:border-gray-800'>Enter</kbd>{' '}
          to send, <kbd className='rounded border border-gray-200 px-1 dark:border-gray-800'>Shift</kbd> +{' '}
          <kbd className='rounded border border-gray-200 px-1 dark:border-gray-800'>Enter</kbd> for a
          new line.
        </p>
      </div>
    </div>
  );
}
