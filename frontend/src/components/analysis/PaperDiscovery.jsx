import { Star, ExternalLink } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

export const PaperDiscovery = ({ papers, onSelect, selectedId }) => {
  if (!papers || papers.length === 0) return null;

  return (
    <Card padding="none" className="overflow-hidden">
      <div className="px-4 py-3 border-b border-zinc-800 flex items-center justify-between">
        <h3 className="text-sm font-medium text-white">Discovered Papers</h3>
        <Badge variant="success" size="sm">{papers.length} found</Badge>
      </div>
      <div className="divide-y divide-zinc-800">
        {papers.map((paper, idx) => {
          const isSelected = selectedId === paper.arxiv_id;
          const score = Math.round(((paper.relevance_score || 0) + (paper.novelty_score || 0)) / 2 * 100);

          return (
            <button
              key={paper.arxiv_id}
              onClick={() => onSelect(paper.arxiv_id)}
              className={`
                w-full text-left px-4 py-3 transition-colors
                ${isSelected ? 'bg-violet-500/10' : 'hover:bg-zinc-800/50'}
              `}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono text-zinc-500">{paper.arxiv_id}</span>
                    {isSelected && <Badge variant="primary" size="sm">Selected</Badge>}
                  </div>
                  <h4 className="text-sm font-medium text-white truncate">{paper.title}</h4>
                  <p className="text-xs text-zinc-500 mt-1 line-clamp-1">{paper.summary}</p>
                </div>
                <div className="flex items-center gap-1 text-amber-400 shrink-0">
                  <Star className="h-3 w-3 fill-current" />
                  <span className="text-xs font-medium">{score}%</span>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </Card>
  );
};
