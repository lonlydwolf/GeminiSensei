import { useState } from 'react';
import { useApp } from '../hooks/useApp';
import { Moon, Sun, Key, Save, CheckCircle, Shield } from 'lucide-react';

export default function Settings() {
  const { apiKey, setApiKey, theme, setTheme } = useApp();
  const [localKey, setLocalKey] = useState(apiKey);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSaveKey = async () => {
    setError(null);
    try {
      await setApiKey(localKey);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e: unknown) {
      console.error('Failed to save API key:', e);
      const msg =
        e instanceof Error &&
        (e.message?.includes('Failed to fetch') || e.message?.includes('Load failed'))
          ? 'Connection Error: Could not reach the sidecar. Is it running?'
          : `Error: ${e instanceof Error ? e.message : 'Failed to save'}`;
      setError(msg);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-12 px-6 h-full overflow-y-auto">
      <h2 className="text-3xl font-bold mb-8 text-gray-900 dark:text-white">Settings</h2>

      <div className="space-y-6">
        {/* API Key Section */}
        <div className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-2xl">
              <Key size={24} />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Gemini API Key</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Required for all AI features.</p>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="relative">
              <input
                type="password"
                value={localKey}
                onChange={(e) => setLocalKey(e.target.value)}
                placeholder="Paste your API key here"
                className="w-full p-4 pl-5 pr-12 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              />
              <div className="absolute right-4 top-4 text-gray-400">
                  <Shield size={18} />
              </div>
            </div>

            {error && (
              <div className="p-4 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-2xl text-sm border border-red-100 dark:border-red-800">
                {error}
              </div>
            )}

            <div className="flex justify-end">
                <button
                onClick={handleSaveKey}
                className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-medium transition-all shadow-md ${
                    saved 
                    ? 'bg-green-500 text-white' 
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
                >
                {saved ? <CheckCircle size={18} /> : <Save size={18} />}
                {saved ? 'Saved' : 'Save Key'}
                </button>
            </div>
            <p className="text-xs text-gray-400 flex items-center gap-1">
               <Shield size={12} /> Your API key is stored locally in your browser and never transmitted to our servers.
            </p>
          </div>
        </div>

        {/* Theme Section */}
        <div className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-sm border border-gray-200 dark:border-gray-700">
           <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-2xl">
                  {theme === 'dark' ? <Moon size={24} /> : <Sun size={24} />}
                </div>
                <div>
                  <h3 className="text-lg font-semibold">Appearance</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Customize the application theme.</p>
                </div>
              </div>
              
              <div className="flex bg-gray-100 dark:bg-gray-700 p-1.5 rounded-2xl">
                  <button
                    onClick={() => setTheme('light')}
                    className={`px-5 py-2 rounded-xl text-sm font-medium transition-all ${
                        theme === 'light' 
                        ? 'bg-white text-gray-900 shadow-sm' 
                        : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                    }`}
                  >
                    Light
                  </button>
                  <button
                    onClick={() => setTheme('dark')}
                    className={`px-5 py-2 rounded-xl text-sm font-medium transition-all ${
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
      </div>
    </div>
  );
}
