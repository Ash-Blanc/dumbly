import { useState } from 'react';
import { Loader2 } from 'lucide-react';

const loadingMessages = [
  'Analyzing paper structure...',
  'Extracting key innovations...',
  'Generating business ideas...',
  'Researching market opportunities...',
  'Building revenue models...',
];

export const LoadingState = ({ progress = {} }) => {
  const [messageIndex, setMessageIndex] = useState(0);

  // Cycle through messages
  useState(() => {
    const interval = setInterval(() => {
      setMessageIndex(prev => (prev + 1) % loadingMessages.length);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const completedSteps = Object.values(progress).filter(p => p?.status === 'complete').length;
  const totalSteps = 4;
  const percentage = Math.round((completedSteps / totalSteps) * 100);

  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="relative mb-6">
        <div className="h-16 w-16 rounded-full border-2 border-zinc-700 flex items-center justify-center">
          <Loader2 className="h-8 w-8 text-violet-400 animate-spin" />
        </div>
        <div className="absolute -bottom-1 -right-1 h-6 w-6 rounded-full bg-zinc-900 border-2 border-violet-500 flex items-center justify-center">
          <span className="text-[10px] font-bold text-violet-400">{percentage}%</span>
        </div>
      </div>

      <p className="text-sm text-zinc-400 animate-pulse">
        {loadingMessages[messageIndex]}
      </p>
    </div>
  );
};
