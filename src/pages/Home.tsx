import { useApp } from '../hooks/useApp';
import { AppRoute } from '../types';
import {
  Zap,
  Clock,
  Trophy,
  Play,
  Star,
  Code,
  Map as MapIcon,
  MessageSquare,
  ArrowRight,
  Shield,
} from 'lucide-react';

export default function Home() {
  const { userName, roadmap, setRoute } = useApp();

  // Time-based greeting
  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';

  // Sensei Quote
  const quote = 'Consistency is the key to mastery.';

  // Derived State
  const userLevel = localStorage.getItem('edu_user_level') || 'White Belt';

  // Find current lesson (mock logic: first lesson of first phase if available)
  const currentPhase = roadmap?.[0];
  const currentLesson = currentPhase?.lessons?.[0];
  const progress = 0; // Mock progress for now

  return (
    <div className='animate-in fade-in mx-auto h-full max-w-5xl space-y-8 overflow-y-auto p-6 duration-500'>
      {/* Header */}
      <header className='space-y-2'>
        <h1 className='text-3xl font-bold text-gray-900 dark:text-white'>
          {greeting}, {userName || 'Student'}! 🌅
        </h1>
        <p className='text-gray-500 italic dark:text-gray-400'>"{quote}" — Your Sensei</p>
      </header>

      {/* Main Action Card: Continue Training */}
      <div className='relative overflow-hidden rounded-3xl bg-white p-1 shadow-xl ring-1 shadow-blue-900/5 ring-gray-100 dark:bg-gray-800 dark:ring-gray-700'>
        <div className='absolute top-0 left-0 h-1 w-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 opacity-80' />

        <div className='p-6 md:p-8'>
          <div className='flex flex-col justify-between gap-6 md:flex-row md:items-center'>
            <div className='flex-1 space-y-4'>
              <div className='flex items-center gap-2 text-sm font-semibold tracking-wide text-blue-600 uppercase dark:text-blue-400'>
                <span className='flex h-2 w-2 animate-pulse rounded-full bg-blue-500' />
                🎯 Continue Your Training
              </div>

              {roadmap ? (
                <>
                  <div>
                    <h2 className='text-2xl font-bold text-gray-900 dark:text-white'>
                      {currentLesson?.title || 'Ready to Start?'}
                    </h2>
                    <p className='mt-1 text-gray-500 dark:text-gray-400'>
                      {currentPhase?.title} • ~20 min remaining
                    </p>
                  </div>

                  <div className='max-w-md space-y-2'>
                    <div className='flex justify-between text-xs font-medium text-gray-500 dark:text-gray-400'>
                      <span>Progress</span>
                      <span>{progress}%</span>
                    </div>
                    <div className='h-2.5 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-700'>
                      <div
                        className='h-full rounded-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-500'
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>
                </>
              ) : (
                <div>
                  <h2 className='text-2xl font-bold text-gray-900 dark:text-white'>
                    Your Journey Awaits
                  </h2>
                  <p className='mt-1 text-gray-500 dark:text-gray-400'>
                    Create your personalized roadmap to begin.
                  </p>
                </div>
              )}
            </div>

            <div className='shrink-0'>
              <button
                onClick={() => setRoute(roadmap ? AppRoute.CHAT : AppRoute.ROADMAP)}
                className='group flex items-center gap-3 rounded-2xl bg-gray-900 px-6 py-4 text-white shadow-lg transition-all hover:-translate-y-0.5 hover:bg-gray-800 hover:shadow-xl active:translate-y-0 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-100'
              >
                {roadmap ? (
                  <>
                    <span className='font-semibold'>Resume Lesson</span>
                    <Play size={20} className='fill-current' />
                  </>
                ) : (
                  <>
                    <span className='font-semibold'>Create Roadmap</span>
                    <ArrowRight size={20} />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Row */}
      <div className='grid grid-cols-1 gap-4 md:grid-cols-3'>
        <div className='flex items-center gap-4 rounded-3xl bg-white p-5 shadow-sm ring-1 ring-gray-100 dark:bg-gray-800 dark:ring-gray-700'>
          <div className='flex h-12 w-12 items-center justify-center rounded-2xl bg-orange-50 text-orange-600 dark:bg-orange-900/20 dark:text-orange-400'>
            <Zap size={24} className='fill-current' />
          </div>
          <div>
            <p className='text-xs font-semibold tracking-wider text-gray-400 uppercase dark:text-gray-500'>
              Daily Streak
            </p>
            <p className='text-xl font-bold text-gray-900 dark:text-white'>7 Days</p>
          </div>
        </div>

        <div className='flex items-center gap-4 rounded-3xl bg-white p-5 shadow-sm ring-1 ring-gray-100 dark:bg-gray-800 dark:ring-gray-700'>
          <div className='flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'>
            <Clock size={24} />
          </div>
          <div>
            <p className='text-xs font-semibold tracking-wider text-gray-400 uppercase dark:text-gray-500'>
              Study Time
            </p>
            <p className='text-xl font-bold text-gray-900 dark:text-white'>4.5 Hours</p>
          </div>
        </div>

        <div className='flex items-center gap-4 rounded-3xl bg-white p-5 shadow-sm ring-1 ring-gray-100 dark:bg-gray-800 dark:ring-gray-700'>
          <div className='flex h-12 w-12 items-center justify-center rounded-2xl bg-yellow-50 text-yellow-600 dark:bg-yellow-900/20 dark:text-yellow-400'>
            <Trophy size={24} className='fill-current' />
          </div>
          <div>
            <p className='text-xs font-semibold tracking-wider text-gray-400 uppercase dark:text-gray-500'>
              Current Level
            </p>
            <p className='text-xl font-bold text-gray-900 dark:text-white'>{userLevel}</p>
          </div>
        </div>
      </div>

      {/* Bottom Section: Achievements & Quick Actions */}
      <div className='grid grid-cols-1 gap-8 lg:grid-cols-3'>
        {/* Achievements */}
        <div className='space-y-4 lg:col-span-2'>
          <h3 className='flex items-center gap-2 text-lg font-bold text-gray-900 dark:text-white'>
            Recent Achievements
          </h3>
          <div className='space-y-4 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-100 dark:bg-gray-800 dark:ring-gray-700'>
            <div className='flex items-center gap-4'>
              <div className='flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400'>
                <Star size={18} className='fill-current' />
              </div>
              <div>
                <p className='font-semibold text-gray-900 dark:text-white'>Fast Learner</p>
                <p className='text-sm text-gray-500 dark:text-gray-400'>
                  Completed 5 lessons in one week
                </p>
              </div>
            </div>
            <div className='h-px bg-gray-100 dark:bg-gray-700/50' />
            <div className='flex items-center gap-4'>
              <div className='flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400'>
                <Code size={18} />
              </div>
              <div>
                <p className='font-semibold text-gray-900 dark:text-white'>Clean Code</p>
                <p className='text-sm text-gray-500 dark:text-gray-400'>
                  Perfect score on code review
                </p>
              </div>
            </div>
            <div className='h-px bg-gray-100 dark:bg-gray-700/50' />
            <div className='flex items-center gap-4'>
              <div className='flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400'>
                <Shield size={18} className='fill-current' />
              </div>
              <div>
                <p className='font-semibold text-gray-900 dark:text-white'>White Belt</p>
                <p className='text-sm text-gray-500 dark:text-gray-400'>Started the journey</p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className='space-y-4'>
          <h3 className='text-lg font-bold text-gray-900 dark:text-white'>Quick Actions</h3>
          <div className='space-y-3'>
            <button
              onClick={() => setRoute(AppRoute.CHAT)}
              className='flex w-full items-center gap-3 rounded-2xl border border-gray-200 bg-white p-4 font-medium text-gray-700 transition-all hover:border-blue-200 hover:bg-blue-50/50 hover:text-blue-600 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700 dark:hover:text-blue-400'
            >
              <div className='flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'>
                <MessageSquare size={20} />
              </div>
              Start New Chat
            </button>
            <button
              onClick={() => setRoute(AppRoute.CHAT)}
              className='flex w-full items-center gap-3 rounded-2xl border border-gray-200 bg-white p-4 font-medium text-gray-700 transition-all hover:border-orange-200 hover:bg-orange-50/50 hover:text-orange-600 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700 dark:hover:text-orange-400'
            >
              <div className='flex h-10 w-10 items-center justify-center rounded-xl bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400'>
                <Code size={20} />
              </div>
              Review Code
            </button>
            <button
              onClick={() => setRoute(AppRoute.ROADMAP)}
              className='flex w-full items-center gap-3 rounded-2xl border border-gray-200 bg-white p-4 font-medium text-gray-700 transition-all hover:border-purple-200 hover:bg-purple-50/50 hover:text-purple-600 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700 dark:hover:text-purple-400'
            >
              <div className='flex h-10 w-10 items-center justify-center rounded-xl bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400'>
                <MapIcon size={20} />
              </div>
              Explore Roadmap
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
