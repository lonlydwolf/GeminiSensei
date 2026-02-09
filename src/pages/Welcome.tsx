import { useState } from 'react';
import { useApp } from '../hooks/useApp';
import {
  Key,
  Shield,
  BookOpen,
  ArrowRight,
  User,
  Target,
  BarChart,
  CheckCircle,
} from 'lucide-react';

export default function Welcome() {
  const { setApiKey, setUserName, completeOnboarding } = useApp();
  const [tempKey, setTempKey] = useState('');
  const [name, setName] = useState('');
  const [level, setLevel] = useState('Beginner');
  const [goal, setGoal] = useState('');
  const [step, setStep] = useState(1);
  const [showLearnMore, setShowLearnMore] = useState(false);

  const handleApiKeySubmit = () => {
    if (tempKey.trim()) {
      setApiKey(tempKey.trim());
      setStep(3);
    }
  };

  const handleFinalSubmit = () => {
    if (!name.trim() || !goal.trim()) return;

    setUserName(name.trim());
    // Persist goal and level for the Roadmap page to pick up later
    localStorage.setItem('edu_user_goal', goal.trim());
    localStorage.setItem('edu_user_level', level);

    completeOnboarding();
  };

  return (
    <div className='flex min-h-screen items-center justify-center bg-gray-50 p-6 font-sans text-gray-900 transition-colors dark:bg-gray-950 dark:text-gray-100'>
      <div className='w-full max-w-xl overflow-hidden rounded-3xl bg-white shadow-xl ring-1 ring-gray-900/5 transition-all dark:bg-gray-900 dark:ring-white/10'>
        {/* Progress Bar */}
        <div className='h-1.5 w-full bg-gray-100 dark:bg-gray-800'>
          <div
            className='h-full bg-blue-600 transition-all duration-500 ease-out'
            style={{ width: `${(step / 3) * 100}%` }}
          />
        </div>

        <div className='p-8 md:p-10'>
          {/* Step 1: Philosophy */}
          {step === 1 && (
            <div className='animate-in fade-in slide-in-from-bottom-4 space-y-8 duration-700'>
              <div className='text-center'>
                <div className='relative mx-auto mb-6 flex h-24 w-24 items-center justify-center overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800'>
                  {/* Belt Animation */}
                  <div className='absolute inset-0 flex items-center justify-center'>
                    <div
                      className='h-4 w-16 rotate-45 transform animate-pulse border border-gray-300 bg-white shadow-sm transition-colors duration-[3000ms] dark:bg-gray-200'
                      style={{ animation: 'belt-color-change 5s infinite alternate' }}
                    />
                    <style>{`
                       @keyframes belt-color-change {
                         0% { background-color: #f3f4f6; border-color: #d1d5db; } /* White Belt */
                         25% { background-color: #fcd34d; border-color: #d97706; } /* Yellow Belt */
                         50% { background-color: #22c55e; border-color: #15803d; } /* Green Belt */
                         75% { background-color: #3b82f6; border-color: #1d4ed8; } /* Blue Belt */
                         100% { background-color: #111827; border-color: #000000; } /* Black Belt */
                       }
                     `}</style>
                  </div>
                  <Shield size={40} className='z-10 text-gray-400 opacity-20' />
                </div>

                <h1 className='text-3xl font-bold tracking-tight text-gray-900 dark:text-white'>
                  🥋 Welcome to GeminiSensei
                </h1>

                <div className='mt-6 space-y-2 text-lg text-gray-600 dark:text-gray-300'>
                  <p>I am your AI programming sensei.</p>
                  <p>
                    I will <span className='font-semibold text-red-500'>not</span> give you code.
                  </p>
                  <p>I will teach you to write it yourself.</p>
                </div>
              </div>

              {showLearnMore && (
                <div className='animate-in fade-in slide-in-from-top-2 space-y-4 border-t border-gray-100 pt-4 duration-500 dark:border-gray-800'>
                  <div className='flex gap-4 rounded-2xl bg-gray-50 p-4 transition-colors dark:bg-gray-800/50'>
                    <div className='flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'>
                      <BookOpen size={20} />
                    </div>
                    <div>
                      <h3 className='font-semibold text-gray-900 dark:text-white'>
                        Strict Protocol
                      </h3>
                      <p className='text-sm text-gray-500 dark:text-gray-400'>
                        No copy-pasting. You type every line to build muscle memory.
                      </p>
                    </div>
                  </div>
                  <div className='flex gap-4 rounded-2xl bg-gray-50 p-4 transition-colors dark:bg-gray-800/50'>
                    <div className='flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400'>
                      <Target size={20} />
                    </div>
                    <div>
                      <h3 className='font-semibold text-gray-900 dark:text-white'>Spec-First</h3>
                      <p className='text-sm text-gray-500 dark:text-gray-400'>
                        We design before we build. Architectural thinking is key.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <div className='flex flex-col gap-3 pt-2'>
                <button
                  onClick={() => setStep(2)}
                  className='group flex w-full items-center justify-center gap-2 rounded-xl bg-gray-900 py-3.5 text-base font-semibold text-white transition-all hover:bg-gray-800 hover:shadow-lg active:scale-95 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-100'
                >
                  Let's Start
                  <ArrowRight
                    size={18}
                    className='transition-transform group-hover:translate-x-1'
                  />
                </button>

                {!showLearnMore && (
                  <button
                    onClick={() => setShowLearnMore(true)}
                    className='w-full text-sm font-medium text-gray-500 transition-colors hover:text-gray-900 dark:text-gray-400 dark:hover:text-white'
                  >
                    Learn More
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Step 2: API Key */}
          {step === 2 && (
            <div className='animate-in fade-in slide-in-from-right-8 space-y-8 duration-500'>
              <div className='text-center'>
                <h2 className='text-2xl font-bold text-gray-900 dark:text-white'>
                  Unlock Your Sensei
                </h2>
                <p className='mt-2 text-gray-500 dark:text-gray-400'>
                  Enter your Gemini API Key to activate the AI brain.
                </p>
              </div>

              <div className='space-y-4'>
                <div className='group relative'>
                  <div className='pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-gray-400 group-focus-within:text-blue-500'>
                    <Key size={20} />
                  </div>
                  <input
                    type='password'
                    value={tempKey}
                    onChange={(e) => setTempKey(e.target.value)}
                    placeholder='Paste API Key here...'
                    className='w-full rounded-xl border border-gray-200 bg-gray-50 py-3.5 pr-4 pl-11 text-sm font-medium text-gray-900 transition-all outline-none placeholder:text-gray-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10 dark:border-gray-700 dark:bg-gray-800 dark:text-white dark:focus:border-blue-500 dark:focus:bg-gray-900'
                    autoFocus
                  />
                </div>
                <div className='text-center'>
                  <a
                    href='https://aistudio.google.com/app/apikey'
                    target='_blank'
                    rel='noopener noreferrer'
                    className='inline-flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-700 hover:underline dark:text-blue-400 dark:hover:text-blue-300'
                  >
                    Get a free key from Google AI Studio <ArrowRight size={10} />
                  </a>
                </div>
              </div>

              <div className='flex gap-3'>
                <button
                  onClick={() => setStep(1)}
                  className='rounded-xl px-5 py-3.5 text-sm font-semibold text-gray-600 transition-colors hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
                >
                  Back
                </button>
                <button
                  onClick={handleApiKeySubmit}
                  disabled={!tempKey.trim()}
                  className='flex flex-1 items-center justify-center gap-2 rounded-xl bg-blue-600 py-3.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/25 transition-all hover:bg-blue-700 disabled:opacity-50 disabled:shadow-none'
                >
                  Continue
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Profile Setup */}
          {step === 3 && (
            <div className='animate-in fade-in slide-in-from-right-8 space-y-6 duration-500'>
              <div className='text-center'>
                <h2 className='text-2xl font-bold text-gray-900 dark:text-white'>Profile Setup</h2>
                <p className='mt-2 text-gray-500 dark:text-gray-400'>
                  Help me understand who you are.
                </p>
              </div>

              <div className='space-y-5'>
                {/* Name Input */}
                <div className='space-y-1.5'>
                  <label className='text-xs font-bold tracking-wide text-gray-500 uppercase dark:text-gray-400'>
                    What should I call you?
                  </label>
                  <div className='relative'>
                    <div className='pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-gray-400'>
                      <User size={18} />
                    </div>
                    <input
                      type='text'
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder='Your Name'
                      className='w-full rounded-xl border border-gray-200 bg-gray-50 py-3 pr-4 pl-11 text-sm font-medium text-gray-900 transition-all outline-none focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10 dark:border-gray-700 dark:bg-gray-800 dark:text-white dark:focus:border-blue-500'
                      autoFocus
                    />
                  </div>
                </div>

                {/* Experience Level */}
                <div className='space-y-1.5'>
                  <label className='text-xs font-bold tracking-wide text-gray-500 uppercase dark:text-gray-400'>
                    Experience Level
                  </label>
                  <div className='grid grid-cols-3 gap-3'>
                    {['Beginner', 'Intermediate', 'Advanced'].map((l) => (
                      <button
                        key={l}
                        onClick={() => setLevel(l)}
                        className={`flex flex-col items-center justify-center rounded-xl border py-3 text-xs font-semibold transition-all ${
                          level === l
                            ? 'border-blue-600 bg-blue-50 text-blue-700 dark:border-blue-500 dark:bg-blue-900/20 dark:text-blue-400'
                            : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700'
                        }`}
                      >
                        {level === l && <CheckCircle size={14} className='mb-1' />}
                        {l}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Goal Input */}
                <div className='space-y-1.5'>
                  <label className='text-xs font-bold tracking-wide text-gray-500 uppercase dark:text-gray-400'>
                    What do you want to master?
                  </label>
                  <div className='relative'>
                    <div className='pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-gray-400'>
                      <BarChart size={18} />
                    </div>
                    <input
                      type='text'
                      value={goal}
                      onChange={(e) => setGoal(e.target.value)}
                      placeholder='e.g. Python, React, System Design...'
                      className='w-full rounded-xl border border-gray-200 bg-gray-50 py-3 pr-4 pl-11 text-sm font-medium text-gray-900 transition-all outline-none focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10 dark:border-gray-700 dark:bg-gray-800 dark:text-white dark:focus:border-blue-500'
                    />
                  </div>
                </div>
              </div>

              <div className='pt-2'>
                <button
                  onClick={handleFinalSubmit}
                  disabled={!name.trim() || !goal.trim()}
                  className='flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 py-3.5 text-sm font-bold text-white shadow-lg shadow-blue-500/25 transition-all hover:bg-blue-700 active:scale-95 disabled:opacity-50 disabled:shadow-none'
                >
                  Create My Training Plan <ArrowRight size={18} />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
