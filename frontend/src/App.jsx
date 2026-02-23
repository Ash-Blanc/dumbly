import { useState, useEffect } from 'react';
import {
  Header,
  HistoryPanel,
  SearchInput,
  ProgressSteps,
  PaperDiscovery,
  ResultsView,
  Card,
  LoadingState,
} from './components';
import { ThemeProvider } from './hooks/useTheme';
import { useHistory } from './hooks/useHistory';
import { useAnalysisStream } from './hooks/useAnalysisStream';
import './index.css';

function AppContent() {
  const [analysisId, setAnalysisId] = useState(null);
  const [isStarting, setIsStarting] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const { history, addToHistory } = useHistory();
  const { status, progress, results, error, papers, selectPaper } = useAnalysisStream(analysisId);

  const handleSubmit = async (input) => {
    setIsStarting(true);
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input }),
      });
      const data = await response.json();
      setAnalysisId(data.analysis_id);
      addToHistory({ id: data.analysis_id, input, title: input });
    } catch (err) {
      console.error('Failed to start analysis:', err);
    } finally {
      setIsStarting(false);
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

  const handleReset = () => {
    setAnalysisId(null);
  };

  const handleSelectFromHistory = (item) => {
    setAnalysisId(item.id);
  };

  const isAnalyzing = analysisId && !results && papers.length === 0;
  const showProgress = isAnalyzing && !error;
  const showDiscovery = papers.length > 0 && !results;
  const showResults = results !== null;

  return (
    <div className="app">
      {/* History Sidebar */}
      <HistoryPanel
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onSelect={handleSelectFromHistory}
        currentId={analysisId}
      />

      {/* Main Content */}
      <div className="main-content">
        <Header
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          hasHistory={history.length > 0}
        />

        <main className="max-w-3xl mx-auto">
          {/* Input Section */}
          {!showResults && (
            <Card variant="elevated" className="mb-6">
              <SearchInput
                onSubmit={handleSubmit}
                disabled={isStarting || isAnalyzing}
              />
            </Card>
          )}

          {/* Loading State */}
          {showProgress && (
            <Card variant="elevated" className="mb-6">
              <LoadingState progress={progress} />
              <div className="mt-4">
                <ProgressSteps progress={progress} />
              </div>
            </Card>
          )}

          {/* Paper Discovery */}
          {showDiscovery && (
            <div className="mb-6">
              <PaperDiscovery
                papers={papers}
                onSelect={handleSelectPaper}
              />
            </div>
          )}

          {/* Results */}
          {showResults && (
            <ResultsView
              results={results}
              onReset={handleReset}
              onExport={handleExport}
            />
          )}

          {/* Error */}
          {error && (
            <Card variant="highlight" className="mb-6 border-red-500/20 bg-red-500/5">
              <p className="text-sm text-red-400">{error}</p>
              <button
                onClick={handleReset}
                className="text-xs text-red-300 hover:text-red-200 mt-2"
              >
                Try again
              </button>
            </Card>
          )}
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;
