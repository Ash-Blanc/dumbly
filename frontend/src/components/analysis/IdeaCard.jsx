import { Star, TrendingUp, Clock, ExternalLink } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

export const IdeaCard = ({ idea, index }) => {
  const score = idea.market_fit_score ? Math.round(idea.market_fit_score * 10) : null;

  return (
    <Card hover className="group">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-violet-400">#{index + 1}</span>
            {score && (
              <span className="flex items-center gap-1 text-xs text-emerald-400">
                <Star className="h-3 w-3" />
                {score}% fit
              </span>
            )}
          </div>
          <h3 className="text-base font-semibold text-white truncate">{idea.title}</h3>
          {idea.tagline && (
            <p className="text-sm text-violet-300 truncate">{idea.tagline}</p>
          )}
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-zinc-400 mb-3 line-clamp-2">{idea.description}</p>

      {/* Features */}
      {idea.key_features?.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {idea.key_features.slice(0, 3).map((feature, i) => (
            <span key={i} className="text-xs px-2 py-0.5 rounded bg-zinc-800 text-zinc-400">
              {feature}
            </span>
          ))}
        </div>
      )}

      {/* Insights */}
      <div className="grid grid-cols-2 gap-2 pt-3 border-t border-zinc-800">
        {idea.market_insights?.market_size_estimate && (
          <div className="text-center p-2 rounded bg-violet-500/5">
            <TrendingUp className="h-3 w-3 mx-auto text-violet-400 mb-1" />
            <p className="text-xs text-zinc-500">Market</p>
            <p className="text-xs font-medium text-white">{idea.market_insights.market_size_estimate}</p>
          </div>
        )}
        {idea.technical_assessment?.development_effort && (
          <div className="text-center p-2 rounded bg-zinc-800/50">
            <Clock className="h-3 w-3 mx-auto text-zinc-400 mb-1" />
            <p className="text-xs text-zinc-500">Effort</p>
            <p className="text-xs font-medium text-white">{idea.technical_assessment.development_effort}</p>
          </div>
        )}
      </div>
    </Card>
  );
};
