import { useState } from 'react';
import { useApp } from '../hooks/useApp';
import { ArrowRight, Key, User, CheckCircle, Lightbulb } from 'lucide-react';
import { AppRoute } from '../types';

export default function Home() {
  const { apiKey, setApiKey, userName, setUserName, setRoute } = useApp();
  const [localKey, setLocalKey] = useState(apiKey);
  const [localName, setLocalName] = useState(userName);
  const [isSaved, setIsSaved] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const handleSave = async () => {
    setSaveError(null);
    try {
      await setApiKey(localKey);
      setUserName(localName);
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 2000);
    } catch (error: unknown) {
      console.error('Failed to save settings:', error);
      const msg =
        error instanceof Error &&
        (error.message?.includes('Failed to fetch') || error.message?.includes('Load failed'))
          ? 'Connection Error: Could not reach the sidecar. Is it running?'
          : `Error: ${error instanceof Error ? error.message : 'Failed to save'}`;
      setSaveError(msg);
    }
  };

  const isSetupComplete = !!apiKey && !!userName;

  const tips = [
    'Use the Roadmap to generate a structured learning path.',
    'Chat with different Agents (Tutor, Code Reviewer) for specific help.',
    'Select a lesson in the Chat to get context-aware assistance.',
    'Use Shift + Enter in chat for multi-line messages.',
  ];

  return (
    <div className='mx-auto h-full max-w-3xl overflow-y-auto px-6 py-12'>
      <header className='mb-12 text-center'>
        <h1 className='mb-4 text-4xl font-bold text-gray-900 dark:text-white'>
          Welcome to <span className='text-blue-600 dark:text-blue-400'>EduMind</span>
        </h1>
        <p className='text-xl text-gray-600 dark:text-gray-300'>
          Your personal AI-powered learning companion.
        </p>
      </header>

      <div className='mb-8 overflow-hidden rounded-3xl border border-gray-100 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800'>
        <div className='border-b border-gray-100 bg-gray-50 p-8 dark:border-gray-700 dark:bg-gray-800/50'>
          <h2 className='mb-2 flex items-center gap-2 text-xl font-semibold'>
            {isSetupComplete ? "You're all set!" : 'First Time Setup'}
          </h2>
          <p className='text-gray-500 dark:text-gray-400'>
            {isSetupComplete
              ? `Welcome back, ${userName}. Ready to continue learning?`
              : 'To get started, we need a few details to personalize your experience.'}
          </p>
        </div>

        <div className='space-y-6 p-8'>
          <div className='space-y-2'>
            <label className='block text-sm font-medium text-gray-700 dark:text-gray-300'>
              Your Name
            </label>
            <div className='relative'>
              <User className='absolute top-3 left-3 text-gray-400' size={20} />
              <input
                type='text'
                value={localName}
                onChange={(e) => setLocalName(e.target.value)}
                placeholder='How should we call you?'
                className='w-full rounded-2xl border border-gray-200 bg-gray-50 py-3 pr-4 pl-10 transition-all outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900'
              />
            </div>
          </div>

          <div className='space-y-2'>
            <label className='block text-sm font-medium text-gray-700 dark:text-gray-300'>
              Gemini API Key
            </label>
            <div className='relative'>
              <Key className='absolute top-3 left-3 text-gray-400' size={20} />
              <input
                type='password'
                value={localKey}
                onChange={(e) => setLocalKey(e.target.value)}
                placeholder='Enter your Google Gemini API Key'
                className='w-full rounded-2xl border border-gray-200 bg-gray-50 py-3 pr-4 pl-10 font-mono transition-all outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900'
              />
            </div>
            {!isSetupComplete && (
              <p className='text-xs text-gray-500'>Your key is stored locally on your device.</p>
            )}
          </div>

          {saveError && (
            <div className='rounded-2xl border border-red-100 bg-red-50 p-4 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400'>
              {saveError}
            </div>
          )}

          <div className='flex items-center gap-4 pt-4'>
            <button
              onClick={handleSave}
              className={`flex flex-1 items-center justify-center gap-2 rounded-2xl px-6 py-3 font-medium transition-all ${
                isSaved ? 'bg-green-500 text-white' : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {isSaved ? (
                <>
                  <CheckCircle size={20} /> Saved!
                </>
              ) : (
                'Save Setup'
              )}
            </button>

            {isSetupComplete && (
              <button
                onClick={() => setRoute(AppRoute.ROADMAP)}
                className='flex items-center gap-2 px-4 font-medium text-blue-600 hover:underline dark:text-blue-400'
              >
                Start Learning <ArrowRight size={18} />
              </button>
            )}
          </div>
        </div>
      </div>

      {!isSetupComplete && (
        <div className='mt-8 rounded-2xl bg-blue-50 p-4 text-center text-sm text-blue-800 dark:bg-blue-900/20 dark:text-blue-200'>
          Need an API Key? Get one from{' '}
          <a
            href='https://aistudio.google.com/app/apikey'
            target='_blank'
            rel='noreferrer'
            className='font-bold underline'
          >
            Google AI Studio
          </a>
          .
        </div>
      )}

      {isSetupComplete && (
        <div className='mt-8'>
          <h3 className='mb-4 flex items-center gap-2 text-lg font-bold'>
            <Lightbulb className='text-yellow-500' /> Tips for Success
          </h3>
          <div className='grid grid-cols-1 gap-4 md:grid-cols-2'>
            {tips.map((tip, i) => (
              <div
                key={i}
                className='flex items-start gap-3 rounded-2xl border border-gray-100 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800'
              >
                <span className='mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'>
                  {i + 1}
                </span>
                <p className='text-sm text-gray-600 dark:text-gray-300'>{tip}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
