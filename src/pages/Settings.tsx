import { useState } from 'react';
import { useApp } from '../hooks/useApp';
import { Moon, Sun, Key, Save, CheckCircle, Shield, RotateCcw, AlertTriangle } from 'lucide-react';
import { api, ApiError } from '../lib/api';

export default function Settings() {
  const { apiKey, setApiKey, theme, setTheme, setUserName, setRoadmap, isApiKeySet } = useApp();
  const [localKey, setLocalKey] = useState(apiKey);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const [forceShowInput, setForceShowInput] = useState(false);

  // Derive visibility: show input if no key is set OR if user clicked "Update Key"
  const effectivelyShowInput = forceShowInput || !isApiKeySet;

  const handleSaveKey = async () => {
    setError(null);
    try {
      await setApiKey(localKey);
      setSaved(true);
      setForceShowInput(false);
      setTimeout(() => setSaved(false), 2000);
    } catch (e: unknown) {
      console.error('Failed to save API key:', e);
      if (e instanceof ApiError) {
        setError(e.message);
      } else if (
        e instanceof Error &&
        (e.message?.includes('Failed to fetch') || e.message?.includes('Load failed'))
      ) {
        setError('Connection Error: Could not reach the sidecar. Is it running?');
      } else {
        setError(`Error: ${e instanceof Error ? e.message : 'Failed to save'}`);
      }
    }
  };

  const handleResetClick = () => {
    setShowResetConfirm(true);
  };

  const confirmReset = async () => {
    try {
      // 1. Call backend to wipe data
      await api.delete('/api/settings/reset');

      // 2. Clear state and local storage
      setUserName('');
      setRoadmap(null);

      localStorage.removeItem('edu_onboarding_complete');
      localStorage.removeItem('edu_username');
      localStorage.removeItem('edu_user_goal');
      localStorage.removeItem('edu_user_level');
      localStorage.removeItem('edu_roadmap');
      localStorage.removeItem('edu_active_roadmap_id');

      window.location.reload();
    } catch (e: unknown) {
      console.error('Failed to reset application:', e);
      setError(e instanceof Error ? e.message : 'Failed to reset application');
      setShowResetConfirm(false);
    }
  };

  return (
    <div className='relative mx-auto h-full max-w-2xl overflow-y-auto px-6 py-12'>
      <h2 className='mb-8 text-3xl font-bold text-gray-900 dark:text-white'>Settings</h2>

      {showResetConfirm && (
        <div className='animate-in fade-in fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm duration-200'>
          <div className='animate-in zoom-in-95 w-full max-w-md rounded-2xl border border-gray-200 bg-white p-6 shadow-xl duration-200 dark:border-gray-700 dark:bg-gray-800'>
            <h3 className='text-xl font-bold text-gray-900 dark:text-white'>Reset Application?</h3>
            <p className='mt-2 text-gray-500 dark:text-gray-400'>
              This will permanently delete your profile, roadmap, and settings. You will be returned
              to the onboarding screen.
            </p>
            <div className='mt-6 flex justify-end gap-3'>
              <button
                onClick={() => setShowResetConfirm(false)}
                className='rounded-xl px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
              >
                Cancel
              </button>
              <button
                onClick={confirmReset}
                className='rounded-xl bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700'
              >
                Yes, Reset Everything
              </button>
            </div>
          </div>
        </div>
      )}

      <div className='space-y-6'>
        {/* API Key Section */}
        <div className='rounded-3xl border border-gray-200 bg-white p-8 shadow-sm dark:border-gray-700 dark:bg-gray-800'>
          <div className='mb-6 flex items-center gap-3'>
            <div className='rounded-2xl bg-blue-100 p-3 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'>
              <Key size={24} />
            </div>
            <div>
              <h3 className='text-lg font-semibold'>Gemini API Key</h3>
              <p className='text-sm text-gray-500 dark:text-gray-400'>
                Required for all AI features.
              </p>
            </div>
          </div>

          <div className='space-y-4'>
            {!effectivelyShowInput ? (
              <div className='flex items-center justify-between rounded-2xl border border-green-200 bg-green-50 p-4 dark:border-green-900/50 dark:bg-green-900/20'>
                <div className='flex items-center gap-3'>
                  <div className='rounded-full bg-green-100 p-1 text-green-600 dark:bg-green-900/50 dark:text-green-400'>
                    <CheckCircle size={16} />
                  </div>
                  <div>
                    <p className='font-medium text-green-800 dark:text-green-300'>
                      API Key Configured
                    </p>
                    <p className='text-xs text-green-600 dark:text-green-400'>
                      Your key is saved locally.
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setForceShowInput(true)}
                  className='text-sm font-medium text-green-700 hover:text-green-800 hover:underline dark:text-green-400 dark:hover:text-green-300'
                >
                  Update Key
                </button>
              </div>
            ) : (
              <div className='relative'>
                <input
                  type='password'
                  value={localKey}
                  onChange={(e) => setLocalKey(e.target.value)}
                  placeholder='Paste your API key here'
                  className='w-full rounded-2xl border border-gray-200 bg-gray-50 p-4 pr-12 pl-5 font-mono text-sm text-gray-900 outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white'
                />
                <div className='absolute top-4 right-4 text-gray-400'>
                  <Shield size={18} />
                </div>
              </div>
            )}

            {effectivelyShowInput && (
              <>
                {error && (
                  <div className='rounded-2xl border border-red-100 bg-red-50 p-4 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400'>
                    {error}
                  </div>
                )}

                <div className='flex justify-end gap-3'>
                  {isApiKeySet && (
                    <button
                      onClick={() => {
                        setForceShowInput(false);
                        setError(null);
                      }}
                      className='rounded-xl px-4 py-2.5 text-sm font-medium text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
                    >
                      Cancel
                    </button>
                  )}
                  <button
                    onClick={handleSaveKey}
                    className={`flex items-center gap-2 rounded-xl px-6 py-2.5 font-medium shadow-md transition-all ${
                      saved
                        ? 'bg-green-500 text-white'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    {saved ? <CheckCircle size={18} /> : <Save size={18} />}
                    {saved ? 'Saved' : 'Save Key'}
                  </button>
                </div>
              </>
            )}

            {!isApiKeySet && !forceShowInput && (
              <div className='flex items-center gap-2 rounded-2xl border border-amber-100 bg-amber-50 p-4 text-amber-600 dark:border-amber-900/50 dark:bg-amber-900/20 dark:text-amber-400'>
                <AlertTriangle size={18} />
                <span className='text-sm font-medium'>
                  API Key not set. AI features will be disabled.
                </span>
                <button
                  onClick={() => setForceShowInput(true)}
                  className='ml-auto text-sm underline hover:text-amber-700 dark:hover:text-amber-300'
                >
                  Set Key
                </button>
              </div>
            )}

            <p className='flex items-center gap-1 text-xs text-gray-400'>
              <Shield size={12} /> Your API key is stored locally in your browser and never
              transmitted to our servers.
            </p>
          </div>
        </div>

        {/* Theme Section */}
        <div className='rounded-3xl border border-gray-200 bg-white p-8 shadow-sm dark:border-gray-700 dark:bg-gray-800'>
          <div className='flex items-center justify-between'>
            <div className='flex items-center gap-3'>
              <div className='rounded-2xl bg-purple-100 p-3 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400'>
                {theme === 'dark' ? <Moon size={24} /> : <Sun size={24} />}
              </div>
              <div>
                <h3 className='text-lg font-semibold'>Appearance</h3>
                <p className='text-sm text-gray-500 dark:text-gray-400'>
                  Customize the application theme.
                </p>
              </div>
            </div>

            <div className='flex rounded-2xl bg-gray-100 p-1.5 dark:bg-gray-700'>
              <button
                onClick={() => setTheme('light')}
                className={`rounded-xl px-5 py-2 text-sm font-medium transition-all ${
                  theme === 'light'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                }`}
              >
                Light
              </button>
              <button
                onClick={() => setTheme('dark')}
                className={`rounded-xl px-5 py-2 text-sm font-medium transition-all ${
                  theme === 'dark'
                    ? 'bg-gray-600 text-white shadow-sm'
                    : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                }`}
              >
                Dark
              </button>
            </div>
          </div>
        </div>

        {/* Reset Section */}
        <div className='rounded-3xl border border-gray-200 bg-white p-8 shadow-sm dark:border-gray-700 dark:bg-gray-800'>
          <div className='flex items-center justify-between'>
            <div className='flex items-center gap-3'>
              <div className='rounded-2xl bg-red-100 p-3 text-red-600 dark:bg-red-900/30 dark:text-red-400'>
                <RotateCcw size={24} />
              </div>
              <div>
                <h3 className='text-lg font-semibold text-gray-900 dark:text-white'>
                  Reset Application
                </h3>
                <p className='text-sm text-gray-500 dark:text-gray-400'>
                  Restart the onboarding journey.
                </p>
              </div>
            </div>

            <button
              onClick={handleResetClick}
              className='rounded-xl border border-red-100 bg-red-50 px-6 py-2.5 text-sm font-semibold text-red-600 transition-all hover:bg-red-100 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400 dark:hover:bg-red-900/30'
            >
              Reset Now
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
