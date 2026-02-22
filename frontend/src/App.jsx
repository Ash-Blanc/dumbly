import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, Sparkles, Loader2, CheckCircle2, ExternalLink, Download,
  TrendingUp, Cpu, Target, Zap, FileText, Lightbulb,
  ArrowRight, Star, X, RefreshCw, Layers
} from 'lucide-react';
import { detectInputType, getInputTypeLabel } from './utils/inputDetection';
import { useAnalysisStream } from './hooks/useAnalysisStream';
import './index.css';

// Animation variants
const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
};

const staggerContainer = {
  animate: {
    transition: { staggerChildren: 0.1 }
  }
};

const slideInRight = {
  initial: { opacity: 0, x: 30 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -30 }
};

// Steps for progress indicator
const STEPS = [
  { id: 'paper_analysis', name: 'Analysis', icon: FileText },
  { id: 'idea_generation', name: 'Ideas', icon: Lightbulb },
  { id: 'market_research', name: 'Market', icon: Target },
  { id: 'business_model', name: 'Business', icon: TrendingUp },
];

// Example inputs
const EXAMPLE_INPUTS = [
  { value: '2303.12712', label: 'Attention Is All You Need' },
  { value: '2005.11401', label: 'RAG Paper' },
  { value: 'transformer architectures', label: 'Topic: Transformers' },
];

function App() {
  const [input, setInput] = useState('');
  const [detectedType, setDetectedType] = useState(null);
  const [analysisId, setAnalysisId] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showExamples, setShowExamples] = useState(true);

  const { status, progress, results, error, papers, selectPaper } = useAnalysisStream(analysisId);

  const handleInputChange = (e) => {
    const value = e.target.value;
    setInput(value);
    setShowExamples(value.trim() === '');
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
    setShowExamples(false);

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

  const handleReset = () => {
    setInput('');
    setAnalysisId(null);
    setIsAnalyzing(false);
    setDetectedType(null);
    setShowExamples(true);
  };

  return (
    <div className="min-h-screen">
      {/* Background Effects */}
      <div className="bg-glow" />
      <div className="bg-grid" />

      <div className="container mx-auto px-4 py-6 max-w-5xl relative z-10">
        {/* Header */}
        <motion.header
          className="text-center mb-12"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 mb-5"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
          >
            <Zap size={14} className="text-violet-400" />
            <span className="text-xs font-medium text-zinc-400">AI Research Analysis</span>
          </motion.div>

          <h1 className="text-4xl md:text-5xl font-bold mb-3 tracking-tight">
            <span className="text-white">arXiv</span>{' '}
            <span className="text-gradient">SaaS</span>{' '}
            <span className="text-white">Generator</span>
          </h1>

          <p className="text-lg text-zinc-500 max-w-xl mx-auto">
            Transform research papers into business opportunities
          </p>
        </motion.header>

        <AnimatePresence mode="wait">
          {/* Input Section */}
          {!results && (
            <motion.section
              key="input"
              variants={fadeInUp}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <div className="glass-card max-w-2xl mx-auto mb-6 p-5">
                <form onSubmit={handleSubmit}>
                  <div className="flex gap-3">
                    <div className="flex-1 relative">
                      <Search
                        className="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-500"
                        size={18}
                      />
                      <input
                        type="text"
                        className="glass-input pl-10 pr-3 py-3 text-sm"
                        placeholder="arXiv ID, URL, or topic..."
                        value={input}
                        onChange={handleInputChange}
                        disabled={isAnalyzing}
                      />
                      <AnimatePresence>
                        {detectedType && (
                          <motion.span
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.8 }}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-xs px-2 py-0.5 rounded-full bg-violet-500/20 text-violet-300"
                          >
                            {getInputTypeLabel(detectedType)}
                          </motion.span>
                        )}
                      </AnimatePresence>
                    </div>

                    <motion.button
                      type="submit"
                      className="btn-primary px-5"
                      disabled={isAnalyzing || !input.trim()}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      {isAnalyzing ? (
                        <Loader2 className="animate-spin" size={18} />
                      ) : (
                        <Sparkles size={18} />
                      )}
                    </motion.button>
                  </div>
                </form>

                {/* Example Inputs */}
                <AnimatePresence>
                  {showExamples && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-3 pt-3 border-t border-white/5"
                    >
                      <div className="flex flex-wrap gap-2">
                        {EXAMPLE_INPUTS.map((example, i) => (
                          <motion.button
                            key={i}
                            onClick={() => setInput(example.value)}
                            className="text-xs px-2.5 py-1 rounded-md bg-white/5 hover:bg-white/10 text-zinc-400 hover:text-white border border-white/5 transition-all"
                            whileHover={{ scale: 1.02 }}
                          >
                            {example.label}
                          </motion.button>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.section>
          )}
        </AnimatePresence>

        {/* Paper Discovery */}
        <AnimatePresence>
          {papers.length > 0 && !results && (
            <motion.section
              variants={fadeInUp}
              initial="initial"
              animate="animate"
              exit="exit"
              className="mb-6"
            >
              <div className="glass-card p-5">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold">Discovered Papers</h2>
                  <span className="text-xs px-2 py-1 rounded-full bg-emerald-500/20 text-emerald-400">
                    {papers.length} found
                  </span>
                </div>

                <div className="space-y-2">
                  {papers.map((paper, idx) => (
                    <motion.div
                      key={paper.arxiv_id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      whileHover={{ x: 4 }}
                      onClick={() => handleSelectPaper(paper.arxiv_id)}
                      className="group p-3 rounded-lg bg-white/[0.02] hover:bg-white/[0.04] border border-white/5 hover:border-violet-500/30 cursor-pointer transition-all"
                    >
                      <div className="flex justify-between items-start gap-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-[10px] font-semibold text-violet-400">
                              #{idx + 1}
                            </span>
                            <span className="text-[10px] text-zinc-500">{paper.arxiv_id}</span>
                          </div>
                          <h3 className="text-sm font-medium text-white group-hover:text-violet-200 line-clamp-1">
                            {paper.title}
                          </h3>
                          <p className="text-xs text-zinc-500 mt-1 line-clamp-1">
                            {paper.summary}
                          </p>
                        </div>

                        <div className="flex items-center gap-1 shrink-0">
                          <Star size={12} className="text-amber-400" />
                          <span className="text-xs font-medium">
                            {Math.round((paper.relevance_score + paper.novelty_score) / 2 * 100)}%
                          </span>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.section>
          )}
        </AnimatePresence>

        {/* Progress Indicator */}
        <AnimatePresence>
          {analysisId && !results && !papers.length && (
            <motion.section
              variants={fadeInUp}
              initial="initial"
              animate="animate"
              exit="exit"
              className="mb-6"
            >
              <div className="glass-card p-5">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-sm font-medium text-zinc-400">Processing</h2>
                  <Loader2 className="animate-spin text-violet-400" size={16} />
                </div>

                <div className="flex gap-3">
                  {STEPS.map((step, idx) => {
                    const stepProgress = progress[step.id];
                    const isComplete = stepProgress?.status === 'complete';
                    const isRunning = stepProgress?.status === 'running';
                    const Icon = step.icon;

                    return (
                      <div
                        key={step.id}
                        className={`flex-1 p-2.5 rounded-lg text-center transition-all ${
                          isComplete
                            ? 'bg-emerald-500/10'
                            : isRunning
                            ? 'bg-violet-500/10'
                            : 'bg-white/[0.02]'
                        }`}
                      >
                        <div className="flex justify-center mb-1">
                          {isComplete ? (
                            <CheckCircle2 size={16} className="text-emerald-400" />
                          ) : isRunning ? (
                            <Loader2 size={16} className="text-violet-400 animate-spin" />
                          ) : (
                            <Icon size={16} className="text-zinc-600" />
                          )}
                        </div>
                        <p className={`text-[10px] ${
                          isComplete ? 'text-emerald-400' : isRunning ? 'text-violet-400' : 'text-zinc-600'
                        }`}>
                          {step.name}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </div>
            </motion.section>
          )}
        </AnimatePresence>

        {/* Results Section */}
        <AnimatePresence>
          {results && (
            <motion.section
              key="results"
              variants={staggerContainer}
              initial="initial"
              animate="animate"
              exit="exit"
              className="space-y-6"
            >
              {/* Paper Summary */}
              {results.paper_analysis && (
                <motion.div variants={fadeInUp} className="glass-card p-5">
                  <div className="flex items-start justify-between gap-3 mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400">
                          Complete
                        </span>
                        {results.paper_analysis.novelty_score && (
                          <span className="text-xs text-violet-400 flex items-center gap-1">
                            <TrendingUp size={12} />
                            {Math.round(results.paper_analysis.novelty_score * 100)}%
                          </span>
                        )}
                      </div>
                      <h2 className="text-xl font-bold text-white mb-1">
                        {results.paper_analysis.paper_title}
                      </h2>
                      <a
                        href={`https://arxiv.org/abs/${results.paper_analysis.paper_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-zinc-500 hover:text-violet-400 flex items-center gap-1"
                      >
                        <ExternalLink size={12} />
                        arXiv:{results.paper_analysis.paper_id}
                      </a>
                    </div>

                    <motion.button
                      onClick={handleReset}
                      className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-zinc-400 hover:text-white transition-all"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <RefreshCw size={16} />
                    </motion.button>
                  </div>

                  <p className="text-sm text-zinc-400 leading-relaxed mb-4">
                    {results.paper_analysis.summary}
                  </p>

                  {results.paper_analysis.key_innovations?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {results.paper_analysis.key_innovations.slice(0, 4).map((innovation, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 text-xs bg-violet-500/10 text-violet-300 rounded-md"
                        >
                          {innovation}
                        </span>
                      ))}
                    </div>
                  )}
                </motion.div>
              )}

              {/* Ideas Grid */}
              {results.ideas && results.ideas.length > 0 && (
                <motion.div variants={fadeInUp}>
                  <div className="flex items-center gap-2 mb-4">
                    <Layers size={16} className="text-zinc-500" />
                    <h2 className="text-lg font-semibold">Opportunities</h2>
                    <span className="text-xs text-zinc-500">({results.ideas.length})</span>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    {results.ideas.map((idea, idx) => (
                      <motion.div
                        key={idx}
                        variants={slideInRight}
                        whileHover={{ y: -2 }}
                        className="idea-card p-4"
                      >
                        {/* Header */}
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-[10px] font-bold text-violet-400">
                                #{idx + 1}
                              </span>
                              {idea.market_fit_score && (
                                <span className="text-[10px] text-emerald-400 flex items-center gap-0.5">
                                  <Star size={10} />
                                  {Math.round(idea.market_fit_score * 10)}%
                                </span>
                              )}
                            </div>
                            <h3 className="text-base font-semibold text-white truncate">
                              {idea.title}
                            </h3>
                            <p className="text-xs text-violet-300 truncate">
                              {idea.tagline}
                            </p>
                          </div>
                        </div>

                        <p className="text-xs text-zinc-400 mb-3 line-clamp-2">
                          {idea.description}
                        </p>

                        {/* Key Features */}
                        {idea.key_features?.length > 0 && (
                          <div className="flex flex-wrap gap-1 mb-3">
                            {idea.key_features.slice(0, 3).map((feature, i) => (
                              <span
                                key={i}
                                className="px-1.5 py-0.5 text-[10px] bg-white/5 text-zinc-400 rounded"
                              >
                                {feature}
                              </span>
                            ))}
                          </div>
                        )}

                        {/* Insights */}
                        <div className="grid grid-cols-2 gap-2">
                          {idea.market_insights && (
                            <div className="p-2 rounded-md bg-violet-500/5 border border-violet-500/10">
                              <p className="text-[10px] text-zinc-500 mb-0.5">Market</p>
                              <p className="text-xs text-white truncate">
                                {idea.market_insights.market_size_estimate || 'N/A'}
                              </p>
                            </div>
                          )}
                          {idea.technical_assessment && (
                            <div className="p-2 rounded-md bg-white/[0.02] border border-white/5">
                              <p className="text-[10px] text-zinc-500 mb-0.5">Effort</p>
                              <p className="text-xs text-white truncate">
                                {idea.technical_assessment.development_effort || 'N/A'}
                              </p>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Export */}
              <motion.div variants={fadeInUp} className="flex gap-2 justify-center pt-2">
                <motion.button
                  onClick={() => handleExport('markdown')}
                  className="btn-primary px-4 py-2 text-sm"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Download size={14} />
                  Markdown
                </motion.button>
                <motion.button
                  onClick={() => handleExport('json')}
                  className="btn-secondary px-4 py-2 text-sm"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Download size={14} />
                  JSON
                </motion.button>
              </motion.div>
            </motion.section>
          )}
        </AnimatePresence>

        {/* Error State */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="glass-card p-4 border-red-500/20 bg-red-500/5 max-w-md mx-auto"
            >
              <div className="flex items-center gap-3">
                <div className="p-1.5 rounded-md bg-red-500/20">
                  <X size={16} className="text-red-400" />
                </div>
                <div className="flex-1">
                  <p className="text-sm text-red-300">{error}</p>
                </div>
                <motion.button
                  onClick={handleReset}
                  className="text-xs text-red-400 hover:text-red-300"
                  whileHover={{ x: 2 }}
                >
                  Retry <ArrowRight size={12} className="inline" />
                </motion.button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;
