import { useLocalStorage } from './useLocalStorage';

const MAX_HISTORY = 20;

export function useHistory() {
  const [history, setHistory] = useLocalStorage('analysis_history', []);

  const addToHistory = (analysis) => {
    setHistory(prev => {
      const filtered = prev.filter(item => item.id !== analysis.id);
      const newItem = {
        id: analysis.id,
        title: analysis.title || analysis.input,
        input: analysis.input,
        timestamp: Date.now(),
        paperId: analysis.paperId,
      };
      return [newItem, ...filtered].slice(0, MAX_HISTORY);
    });
  };

  const removeFromHistory = (id) => {
    setHistory(prev => prev.filter(item => item.id !== id));
  };

  const clearHistory = () => {
    setHistory([]);
  };

  return { history, addToHistory, removeFromHistory, clearHistory };
}
