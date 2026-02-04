import React, { useState } from 'react';
import { useApp } from '../contexts/AppContext';
import { ArrowRight, Key, User, CheckCircle, Lightbulb } from 'lucide-react';
import { AppRoute } from '../types';

export default function Home() {
  const { apiKey, setApiKey, userName, setUserName, setRoute } = useApp();
  const [localKey, setLocalKey] = useState(apiKey);
  const [localName, setLocalName] = useState(userName);
  const [isSaved, setIsSaved] = useState(false);

  const handleSave = () => {
    setApiKey(localKey);
    setUserName(localName);
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2000);
  };

  const isSetupComplete = !!apiKey && !!userName;

  const tips = [
    "Use the Roadmap to generate a structured learning path.",
    "Chat with different Agents (Tutor, Code Reviewer) for specific help.",
    "Select a lesson in the Chat to get context-aware assistance.",
    "Use Shift + Enter in chat for multi-line messages.",
  ];

  return (
    <div className="max-w-3xl mx-auto py-12 px-6 overflow-y-auto h-full">
      <header className="mb-12 text-center">
        <h1 className="text-4xl font-bold mb-4 text-gray-900 dark:text-white">
          Welcome to <span className="text-blue-600 dark:text-blue-400">EduMind</span>
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300">
          Your personal AI-powered learning companion.
        </p>
      </header>

      <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-xl border border-gray-100 dark:border-gray-700 overflow-hidden mb-8">
        <div className="p-8 border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
          <h2 className="text-xl font-semibold flex items-center gap-2 mb-2">
            {isSetupComplete ? "You're all set!" : "First Time Setup"}
          </h2>
          <p className="text-gray-500 dark:text-gray-400">
            {isSetupComplete 
              ? `Welcome back, ${userName}. Ready to continue learning?` 
              : "To get started, we need a few details to personalize your experience."}
          </p>
        </div>

        <div className="p-8 space-y-6">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Your Name
            </label>
            <div className="relative">
              <User className="absolute left-3 top-3 text-gray-400" size={20} />
              <input
                type="text"
                value={localName}
                onChange={(e) => setLocalName(e.target.value)}
                placeholder="How should we call you?"
                className="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-2xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Gemini API Key
            </label>
            <div className="relative">
              <Key className="absolute left-3 top-3 text-gray-400" size={20} />
              <input
                type="password"
                value={localKey}
                onChange={(e) => setLocalKey(e.target.value)}
                placeholder="Enter your Google Gemini API Key"
                className="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-2xl focus:ring-2 focus:ring-blue-500 outline-none transition-all font-mono"
              />
            </div>
            {!isSetupComplete && (
                <p className="text-xs text-gray-500">
                Your key is stored locally on your device.
                </p>
            )}
          </div>

          <div className="pt-4 flex items-center gap-4">
            <button
              onClick={handleSave}
              className={`flex-1 flex items-center justify-center gap-2 py-3 px-6 rounded-2xl font-medium transition-all ${
                isSaved
                  ? 'bg-green-500 text-white'
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
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
               className="flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:underline px-4 font-medium"
             >
               Start Learning <ArrowRight size={18} />
             </button>
            )}
          </div>
        </div>
      </div>
      
      {!isSetupComplete && (
         <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-200 rounded-2xl text-sm text-center">
            Need an API Key? Get one from <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer" className="underline font-bold">Google AI Studio</a>.
         </div>
      )}

      {isSetupComplete && (
        <div className="mt-8">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <Lightbulb className="text-yellow-500" /> Tips for Success
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {tips.map((tip, i) => (
                    <div key={i} className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm flex items-start gap-3">
                        <span className="bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                            {i+1}
                        </span>
                        <p className="text-gray-600 dark:text-gray-300 text-sm">{tip}</p>
                    </div>
                ))}
            </div>
        </div>
      )}
    </div>
  );
}
