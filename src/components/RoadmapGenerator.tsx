import { useState, useEffect } from 'react';
import { CheckCircle, Circle, Loader2, Sparkles } from 'lucide-react';

const QUOTES = [
  'A journey of a thousand miles begins with a single step.',
  'The expert in anything was once a beginner.',
  'It does not matter how slowly you go as long as you do not stop.',
  'Learning never exhausts the mind.',
  'Code is like humor. When you have to explain it, it’s bad.',
  'First, solve the problem. Then, write the code.',
];

const STAGES = [
  'Analyzing your goals',
  'Researching curriculum',
  'Creating lesson structure',
  'Setting objectives',
  'Finalizing your path',
];

interface RoadmapGeneratorProps {
  onComplete?: () => void;
}

export default function RoadmapGenerator({ onComplete }: RoadmapGeneratorProps) {
  const [currentStage, setCurrentStage] = useState(0);
  const [quoteIndex, setQuoteIndex] = useState(0);

  useEffect(() => {
    // Cycle through stages
    if (currentStage < STAGES.length) {
      const timeout = setTimeout(
        () => {
          setCurrentStage((prev) => prev + 1);
        },
        3000 + Math.random() * 2000
      ); // Random duration between 3-5s per stage
      return () => clearTimeout(timeout);
    } else {
      if (onComplete) onComplete();
    }
  }, [currentStage, onComplete]);

  useEffect(() => {
    // Cycle quotes every 4 seconds
    const interval = setInterval(() => {
      setQuoteIndex((prev) => (prev + 1) % QUOTES.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className='animate-in fade-in flex flex-col items-center justify-center p-8 text-center duration-700'>
      <div className='relative mb-8'>
        <div className='absolute inset-0 animate-pulse rounded-full bg-blue-500 opacity-20 blur-3xl'></div>
        <Sparkles
          size={64}
          className='animate-bounce-slow relative z-10 text-blue-600 dark:text-blue-400'
        />
      </div>

      <h2 className='mb-2 text-2xl font-bold text-gray-900 dark:text-white'>
        Your Sensei is preparing your training plan...
      </h2>

      <p className='mb-10 h-12 max-w-md text-gray-500 italic transition-opacity duration-500 dark:text-gray-400'>
        "{QUOTES[quoteIndex]}"
      </p>

      <div className='w-full max-w-sm space-y-4 rounded-3xl border border-gray-100 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800'>
        {STAGES.map((stage, index) => (
          <div key={index} className='flex items-center gap-4'>
            <div className='flex w-6 shrink-0 justify-center'>
              {index < currentStage ? (
                <CheckCircle size={20} className='animate-in zoom-in text-green-500 duration-300' />
              ) : index === currentStage ? (
                <Loader2 size={20} className='animate-spin text-blue-500' />
              ) : (
                <Circle size={20} className='text-gray-300 dark:text-gray-600' />
              )}
            </div>
            <span
              className={`text-sm font-medium transition-colors duration-300 ${
                index === currentStage
                  ? 'origin-left scale-105 text-blue-600 dark:text-blue-400'
                  : index < currentStage
                    ? 'text-gray-400 line-through dark:text-gray-500'
                    : 'text-gray-400 dark:text-gray-600'
              }`}
            >
              {stage}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
