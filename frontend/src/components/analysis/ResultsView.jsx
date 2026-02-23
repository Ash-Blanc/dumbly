import { ExternalLink, Download, RotateCcw, Share2, TrendingUp } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { IdeaCard } from './IdeaCard';

export const ResultsView = ({ results, onReset, onExport }) => {
  const { paper_analysis, ideas, business_models } = results;

  const handleExport = (format) => {
    onExport?.(format);
  };

  return (
    <div className="space-y-6">
      {/* Paper Summary */}
      {paper_analysis && (
        <Card>
          <div className="flex items-start justify-between gap-4 mb-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                <Badge variant="success">Complete</Badge>
                {paper_analysis.novelty_score && (
                  <span className="flex items-center gap-1 text-xs text-violet-400">
                    <TrendingUp className="h-3 w-3" />
                    {Math.round(paper_analysis.novelty_score * 100)}% novelty
                  </span>
                )}
              </div>
              <h2 className="text-xl font-bold text-white mb-1">
                {paper_analysis.paper_title}
              </h2>
              <a
                href={`https://arxiv.org/abs/${paper_analysis.paper_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-zinc-500 hover:text-violet-400 flex items-center gap-1 transition-colors"
              >
                <ExternalLink className="h-3 w-3" />
                arXiv:{paper_analysis.paper_id}
              </a>
            </div>
            <Button variant="ghost" size="icon" onClick={onReset}>
              <RotateCcw className="h-4 w-4" />
            </Button>
          </div>

          <p className="text-sm text-zinc-400 leading-relaxed mb-4">
            {paper_analysis.summary}
          </p>

          {paper_analysis.key_innovations?.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {paper_analysis.key_innovations.slice(0, 5).map((innovation, i) => (
                <Badge key={i} variant="primary">{innovation}</Badge>
              ))}
            </div>
          )}
        </Card>
      )}

      {/* Ideas */}
      {ideas && ideas.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-white mb-4">
            Business Opportunities
            <span className="text-sm font-normal text-zinc-500 ml-2">({ideas.length})</span>
          </h3>
          <div className="grid md:grid-cols-2 gap-4">
            {ideas.map((idea, idx) => (
              <IdeaCard key={idx} idea={idea} index={idx} />
            ))}
          </div>
        </div>
      )}

      {/* Export Actions */}
      <div className="flex justify-center gap-3 pt-4">
        <Button variant="secondary" onClick={() => handleExport('markdown')}>
          <Download className="h-4 w-4" />
          Markdown
        </Button>
        <Button variant="secondary" onClick={() => handleExport('json')}>
          <Download className="h-4 w-4" />
          JSON
        </Button>
        <Button variant="secondary" onClick={() => handleExport('pdf')}>
          <Download className="h-4 w-4" />
          PDF
        </Button>
      </div>
    </div>
  );
};
