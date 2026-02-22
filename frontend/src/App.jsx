import React, { useState } from 'react';
import { Search, Sparkles, Loader2, CheckCircle2, ExternalLink, Download, TrendingUp, Cpu, Target } from 'lucide-react';
import { detectInputType, getInputTypeLabel } from './utils/inputDetection';
import { useAnalysisStream } from './hooks/useAnalysisStream';
import './index.css';

const STEPS = [
  { id: 'paper_analysis', name: 'Paper Analysis' },
  { id: 'idea_generation', name: 'Ideas' },
  { id: 'market_research', name: 'Market Research' },
  { id: 'business_model', name: 'Business Models' },
];

function App() {
  const [input, setInput] = useState('');
  const [detectedType, setDetectedType] = useState(null);
  const [analysisId, setAnalysisId] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const { status, progress, results, error, papers, selectPaper } = useAnalysisStream(analysisId);

  const handleInputChange = (e) => {
    const value = e.target.value;
    setInput(value);
    if (value.trim()) {
      setDetectedType(detectInputType(value));
    } else {
      setDetectedType(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isAnalyzing) return;

    setIsAnalyzing(true);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: input.trim() }),
      });

      const data = await response.json();
      setAnalysisId(data.analysis_id);
    } catch (err) {
      console.error('Failed to start analysis:', err);
      setIsAnalyzing(false);
    }
  };

  const handleExport = async (format) => {
    if (!analysisId) return;

    try {
      const response = await fetch('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ analysis_id: analysisId, format }),
      });

      const data = await response.json();
      window.open(`/api/export/${data.export_id}/download`, '_blank');
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  const handleSelectPaper = async (arxivId) => {
    try {
      await fetch('/api/analyze/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ analysis_id: analysisId, arxiv_id: arxivId }),
      });
      selectPaper(arxivId);
    } catch (err) {
      console.error('Failed to select paper:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4">
            arXiv SaaS Generator
          </h1>
          <p className="text-gray-400 text-lg">
            Transform research papers into SaaS opportunities with AI
          </p>
        </header>

        {/* Input Form */}
        {!results && (
          <div className="glass-card p-6 mb-8">
            <form onSubmit={handleSubmit} className="flex gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={20} />
                <input
                  type="text"
                  className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                  placeholder="Enter arXiv ID, URL, or research topic..."
                  value={input}
                  onChange={handleInputChange}
                  disabled={isAnalyzing}
                />
                {detectedType && (
                  <span className="absolute right-4 top-1/2 -translate-y-1/2 text-xs px-2 py-1 bg-purple-500/20 text-purple-300 rounded-full">
                    {getInputTypeLabel(detectedType)}
                  </span>
                )}
              </div>
              <button
                type="submit"
                className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl font-semibold flex items-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50"
                disabled={isAnalyzing || !input.trim()}
              >
                {isAnalyzing ? (
                  <><Loader2 className="animate-spin" size={20} /> Analyzing...</>
                ) : (
                  <><Sparkles size={20} /> Generate</>
                )}
              </button>
            </form>
          </div>
        )}

        {/* Paper Discovery */}
        {papers.length > 0 && !results && (
          <div className="glass-card p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Discovered Papers</h2>
            <div className="space-y-4">
              {papers.map((paper, idx) => (
                <div
                  key={paper.arxiv_id}
                  className="p-4 bg-white/5 rounded-lg border border-white/10 hover:border-purple-500/50 cursor-pointer transition-colors"
                  onClick={() => handleSelectPaper(paper.arxiv_id)}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="text-xs text-purple-400 mb-1 block">#{idx + 1} Match</span>
                      <h3 className="font-medium text-white">{paper.title}</h3>
                      <p className="text-sm text-gray-400 mt-2 line-clamp-2">{paper.summary}</p>
                    </div>
                    <span className="text-xs px-2 py-1 bg-green-500/20 text-green-300 rounded-full whitespace-nowrap">
                      {Math.round((paper.relevance_score + paper.novelty_score) / 2 * 100)}% match
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Progress */}
        {analysisId && !results && !papers.length && (
          <div className="glass-card p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Analysis Progress</h2>
            <div className="flex gap-4 flex-wrap">
              {STEPS.map((step) => (
                <div key={step.id} className="flex items-center gap-2">
                  {progress[step.id]?.status === 'complete' ? (
                    <CheckCircle2 className="text-green-400" size={20} />
                  ) : progress[step.id]?.status === 'running' ? (
                    <Loader2 className="animate-spin text-purple-400" size={20} />
                  ) : (
                    <div className="w-5 h-5 rounded-full border border-gray-600" />
                  )}
                  <span className={progress[step.id]?.status === 'complete' ? 'text-white' : 'text-gray-500'}>
                    {step.name}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="space-y-8">
            {/* Paper Summary */}
            {results.paper_analysis && (
              <div className="glass-card p-6">
                <h2 className="text-2xl font-bold mb-4">{results.paper_analysis.paper_title}</h2>
                <p className="text-gray-300 mb-4">{results.paper_analysis.summary}</p>
                <div className="flex gap-4 flex-wrap">
                  <a
                    href={`https://arxiv.org/abs/${results.paper_analysis.paper_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-purple-400 hover:text-purple-300 flex items-center gap-1"
                  >
                    <ExternalLink size={16} /> View on arXiv
                  </a>
                  <span className="text-gray-400 flex items-center gap-1">
                    <TrendingUp size={16} /> Novelty: {Math.round(results.paper_analysis.novelty_score * 100)}%
                  </span>
                </div>
              </div>
            )}

            {/* Ideas Grid */}
            {results.ideas && (
              <div>
                <h2 className="text-2xl font-bold mb-4">Generated SaaS Opportunities</h2>
                <div className="grid md:grid-cols-2 gap-6">
                  {results.ideas.map((idea, idx) => (
                    <div key={idx} className="glass-card p-6">
                      <div className="flex justify-between items-start mb-3">
                        <h3 className="text-xl font-semibold text-purple-300">{idea.title}</h3>
                        <span className="text-xs px-2 py-1 bg-green-500/20 text-green-300 rounded-full">
                          {Math.round(idea.market_fit_score * 10)}% fit
                        </span>
                      </div>
                      <p className="text-sm text-gray-300 mb-4">{idea.tagline}</p>
                      <p className="text-gray-400 text-sm mb-4">{idea.description}</p>

                      {/* Key Features */}
                      <div className="flex flex-wrap gap-2 mb-4">
                        {idea.key_features?.slice(0, 3).map((feature, i) => (
                          <span key={i} className="text-xs px-2 py-1 bg-white/5 rounded-full text-gray-400">
                            {feature}
                          </span>
                        ))}
                      </div>

                      {/* Market Insights */}
                      {idea.market_insights && (
                        <div className="p-3 bg-black/20 rounded-lg border border-white/5 mb-4">
                          <h4 className="text-xs uppercase text-gray-500 mb-2 flex items-center gap-1">
                            <Target size={12} /> Market Insights
                          </h4>
                          <p className="text-sm text-gray-300">{idea.market_insights.market_size_estimate}</p>
                        </div>
                      )}

                      {/* Technical Assessment */}
                      {idea.technical_assessment && (
                        <div className="p-3 bg-black/20 rounded-lg border border-white/5">
                          <h4 className="text-xs uppercase text-gray-500 mb-2 flex items-center gap-1">
                            <Cpu size={12} /> Technical Stack
                          </h4>
                          <p className="text-sm text-gray-300">{idea.technical_assessment.recommended_tech_stack?.backend || 'N/A'}</p>
                          <p className="text-xs text-gray-500 mt-1">Effort: {idea.technical_assessment.development_effort}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Export Buttons */}
            <div className="flex gap-4 flex-wrap">
              <button
                onClick={() => handleExport('markdown')}
                className="px-4 py-2 bg-white/10 rounded-lg flex items-center gap-2 hover:bg-white/20 transition-colors"
              >
                <Download size={16} /> Export Markdown
              </button>
              <button
                onClick={() => handleExport('json')}
                className="px-4 py-2 bg-white/10 rounded-lg flex items-center gap-2 hover:bg-white/20 transition-colors"
              >
                <Download size={16} /> Export JSON
              </button>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="glass-card p-6 border border-red-500/50">
            <p className="text-red-400">Error: {error}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
