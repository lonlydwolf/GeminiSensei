import { useState, useEffect, FormEvent } from 'react';
import { useApp } from '../hooks/useApp';
import { Sparkles, Book, Clock, AlertCircle, CheckCircle, BarChart } from 'lucide-react';
import { ApiError } from '../lib/api';

export default function Roadmap() {
  const { geminiService, roadmap, setRoadmap, isApiKeySet } = useApp();
  const [goal, setGoal] = useState('');
  const [background, setBackground] = useState('');
  const [preferences, setPreferences] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generationStage, setGenerationStage] = useState(0);

  useEffect(() => {
    const savedGoal = localStorage.getItem('edu_user_goal');
    if (savedGoal) setGoal(savedGoal);

    const savedLevel = localStorage.getItem('edu_user_level');
    if (savedLevel) setBackground(savedLevel);
  }, []);

  const handleGenerate = async (e: FormEvent) => {
    e.preventDefault();
    if (!isApiKeySet) {
      setError('Please set your API Key in Settings or Home first.');
      return;
    }
    setLoading(true);
    setError(null);
    setGenerationStage(0);
    // Don't clear roadmap immediately to avoid flash if retrying
    if (!roadmap) setRoadmap(null);

    try {
      const animationPromise = new Promise<void>((resolve) => {
        setTimeout(() => setGenerationStage(1), 1500);
        setTimeout(() => setGenerationStage(2), 3000);
        setTimeout(() => setGenerationStage(3), 4500);
        setTimeout(() => resolve(), 6000);
      });

      const [result] = await Promise.all([
        geminiService.generateRoadmap(goal, background, preferences),
        animationPromise,
      ]);

      setRoadmap(result.roadmap);
      localStorage.setItem('edu_active_roadmap_id', result.id);
    } catch (err) {
      console.error(err);
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to generate roadmap. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='mx-auto h-full max-w-5xl overflow-y-auto px-6 py-8'>
      <div className='mb-8'>
        <h2 className='mb-2 text-3xl font-bold'>Learning Roadmap</h2>
        <p className='text-gray-500 dark:text-gray-400'>
          Define your goals and let AI structure your learning path.
        </p>
      </div>

      <div className='grid grid-cols-1 gap-8 lg:grid-cols-3'>
        {/* Form Section */}
        <div className='space-y-6 lg:col-span-1'>
          <form
            onSubmit={handleGenerate}
            className='sticky top-6 space-y-4 rounded-3xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800'
          >
            <div>
              <label className='mb-1 block pl-1 text-sm font-medium'>Learning Goal</label>
              <textarea
                className='w-full resize-none rounded-2xl border border-gray-200 bg-gray-50 p-3 text-sm outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900'
                rows={3}
                placeholder='e.g. Learn Python for Data Science'
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                required
              />
            </div>
            <div>
              <label className='mb-1 block pl-1 text-sm font-medium'>Current Knowledge</label>
              <textarea
                className='w-full resize-none rounded-2xl border border-gray-200 bg-gray-50 p-3 text-sm outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900'
                rows={2}
                placeholder='e.g. Basic HTML/CSS'
                value={background}
                onChange={(e) => setBackground(e.target.value)}
              />
            </div>
            <div>
              <label className='mb-1 block pl-1 text-sm font-medium'>Preferences</label>
              <textarea
                className='w-full resize-none rounded-2xl border border-gray-200 bg-gray-50 p-3 text-sm outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900'
                rows={2}
                placeholder='e.g. Video tutorials, hands-on projects'
                value={preferences}
                onChange={(e) => setPreferences(e.target.value)}
              />
            </div>

            <button
              type='submit'
              disabled={loading || !goal}
              className='flex w-full items-center justify-center gap-2 rounded-2xl bg-blue-600 py-3 font-medium text-white shadow-lg shadow-blue-500/20 transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50'
            >
              {loading ? (
                <span className='h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent' />
              ) : (
                <>
                  <Sparkles size={18} /> Generate Plan
                </>
              )}
            </button>
            {error && (
              <div className='flex items-start gap-2 rounded-2xl bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400'>
                <AlertCircle size={16} className='mt-0.5 shrink-0' />
                <span>{error}</span>
              </div>
            )}
          </form>
        </div>

        {/* Results Section */}
        <div className='lg:col-span-2'>
          {!roadmap && !loading && (
            <div className='flex h-64 flex-col items-center justify-center rounded-3xl border-2 border-dashed border-gray-200 text-gray-400 dark:border-gray-700'>
              <Book size={48} className='mb-4 opacity-50' />
              <p>Your roadmap will appear here.</p>
            </div>
          )}

          {loading && (
            <div className='animate-in fade-in slide-in-from-bottom-4 flex flex-col items-center justify-center py-12 duration-700'>
              <div className='mb-8 text-center'>
                <div className='mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'>
                  <BarChart size={32} className='animate-pulse' />
                </div>
                <h2 className='text-2xl font-bold text-gray-900 dark:text-white'>
                  🎯 Your sensei is preparing your training plan...
                </h2>
              </div>

              <div className='mx-auto w-full max-w-sm space-y-4'>
                {[
                  'Analyzing your goals',
                  'Researching curriculum',
                  'Creating lesson structure',
                  'Setting objectives',
                ].map((text, i) => (
                  <div key={i} className='flex items-center gap-4 transition-all duration-500'>
                    <div className='shrink-0 transition-all duration-500'>
                      {generationStage > i ? (
                        <CheckCircle
                          size={24}
                          className='animate-in zoom-in spin-in-90 text-green-500 duration-300'
                        />
                      ) : generationStage === i ? (
                        <div className='h-6 w-6 animate-spin rounded-full border-2 border-blue-500 border-t-transparent' />
                      ) : (
                        <div className='h-6 w-6 rounded-full border-2 border-gray-200 dark:border-gray-700' />
                      )}
                    </div>
                    <p
                      className={`font-medium transition-colors duration-500 ${
                        generationStage >= i
                          ? 'text-gray-900 dark:text-white'
                          : 'text-gray-400 dark:text-gray-600'
                      }`}
                    >
                      {text}
                    </p>
                  </div>
                ))}
              </div>

              <div className='animate-in fade-in slide-in-from-bottom-2 pt-10 text-center delay-500 duration-1000'>
                <p className='text-sm font-medium text-gray-500 italic dark:text-gray-400'>
                  "A journey of a thousand miles begins with a single step"
                </p>
              </div>
            </div>
          )}

          {roadmap && (
            <div className='relative space-y-0 pb-12'>
              <div className='absolute top-6 bottom-6 left-8 -z-10 w-0.5 bg-gray-200 dark:bg-gray-700'></div>
              {roadmap.map((item, index) => (
                <div key={index} className='group mb-8 flex gap-6'>
                  <div className='z-10 flex h-16 w-16 shrink-0 items-center justify-center rounded-full border-2 border-blue-500 bg-white text-xl font-bold text-blue-500 shadow-sm dark:bg-gray-800'>
                    {index + 1}
                  </div>
                  <div className='flex-1 rounded-3xl border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md dark:border-gray-700 dark:bg-gray-800'>
                    <div className='mb-3 flex flex-wrap items-start justify-between gap-2'>
                      <h3 className='text-xl font-bold'>{item.title}</h3>
                      {item.duration && (
                        <span className='flex items-center gap-1 rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'>
                          <Clock size={12} /> {item.duration}
                        </span>
                      )}
                    </div>
                    {item.description && (
                      <p className='mb-4 leading-relaxed text-gray-600 dark:text-gray-300'>
                        {item.description}
                      </p>
                    )}

                    <div className='border-t border-gray-100 pt-4 dark:border-gray-700'>
                      <p className='mb-3 pl-1 text-xs font-semibold tracking-wider text-gray-500 uppercase'>
                        Lessons
                      </p>
                      <div className='grid grid-cols-1 gap-2'>
                        {item.lessons?.map((lesson) => (
                          <div
                            key={lesson.id}
                            className='group/lesson flex items-center gap-3 rounded-xl border border-gray-100 bg-gray-50 p-3 transition-colors hover:border-blue-200 dark:border-gray-700/50 dark:bg-gray-900/50 dark:hover:border-blue-900/50'
                          >
                            <div className='text-blue-500 opacity-40 transition-opacity group-hover/lesson:opacity-100'>
                              <CheckCircle size={18} />
                            </div>
                            <div className='flex-1'>
                              <p className='text-sm font-medium text-gray-700 dark:text-gray-200'>
                                {lesson.title}
                              </p>
                              {lesson.description && (
                                <p className='mt-0.5 line-clamp-1 text-xs text-gray-500 dark:text-gray-400'>
                                  {lesson.description}
                                </p>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
