import { CheckCircle2, Loader2 } from 'lucide-react';

const STEPS = [
  { id: 'paper_analysis', label: 'Analyzing' },
  { id: 'idea_generation', label: 'Ideas' },
  { id: 'market_research', label: 'Market' },
  { id: 'business_model', label: 'Business' },
];

export const ProgressSteps = ({ progress = {} }) => {
  const getStepStatus = (stepId) => {
    const step = progress[stepId];
    if (!step) return 'pending';
    return step.status;
  };

  const completedCount = STEPS.filter(s => getStepStatus(s.id) === 'complete').length;
  const progressPercent = (completedCount / STEPS.length) * 100;

  return (
    <div className="w-full">
      {/* Progress bar */}
      <div className="h-1 bg-zinc-800 rounded-full overflow-hidden mb-4">
        <div
          className="h-full bg-violet-500 transition-all duration-500"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Steps */}
      <div className="flex justify-between">
        {STEPS.map((step) => {
          const status = getStepStatus(step.id);

          return (
            <div key={step.id} className="flex items-center gap-2">
              <div className={`
                w-6 h-6 rounded-full flex items-center justify-center
                ${status === 'complete' ? 'bg-emerald-500/20' : ''}
                ${status === 'running' ? 'bg-violet-500/20' : ''}
                ${status === 'pending' ? 'bg-zinc-800' : ''}
              `}>
                {status === 'complete' && (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                )}
                {status === 'running' && (
                  <Loader2 className="h-4 w-4 text-violet-400 animate-spin" />
                )}
                {status === 'pending' && (
                  <div className="h-2 w-2 rounded-full bg-zinc-600" />
                )}
              </div>
              <span className={`
                text-xs font-medium
                ${status === 'complete' ? 'text-emerald-400' : ''}
                ${status === 'running' ? 'text-violet-400' : ''}
                ${status === 'pending' ? 'text-zinc-500' : ''}
              `}>
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
