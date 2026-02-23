import { History, Trash2, Clock, FileText } from 'lucide-react';
import { Button } from '../ui/Button';
import { useHistory } from '../../hooks/useHistory';

export const HistoryPanel = ({ onSelect, currentId, isOpen, onClose }) => {
  const { history, removeFromHistory, clearHistory } = useHistory();

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 z-40 lg:hidden"
        onClick={onClose}
      />

      {/* Panel */}
      <aside className={`
        fixed lg:static top-0 right-0 h-full w-72
        bg-zinc-900/95 backdrop-blur-sm border-l border-zinc-800
        z-50 flex flex-col
        transform transition-transform duration-200
        ${isOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'}
      `}>
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <History className="h-4 w-4 text-zinc-400" />
            <h2 className="text-sm font-semibold text-white">Recent</h2>
          </div>
          {history.length > 0 && (
            <Button variant="ghost" size="sm" onClick={clearHistory}>
              <Trash2 className="h-3 w-3" />
            </Button>
          )}
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto">
          {history.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-zinc-500 px-4">
              <Clock className="h-8 w-8 opacity-30 mb-2" />
              <p className="text-sm text-center">No analyses yet</p>
              <p className="text-xs text-center mt-1">Your history will appear here</p>
            </div>
          ) : (
            <div className="p-2 space-y-1">
              {history.map((item) => (
                <button
                  key={item.id}
                  onClick={() => {
                    onSelect(item);
                    onClose?.();
                  }}
                  className={`
                    w-full text-left p-3 rounded-lg group
                    transition-all duration-150
                    ${currentId === item.id
                      ? 'bg-violet-500/10 border border-violet-500/30'
                      : 'hover:bg-zinc-800/50 border border-transparent'
                    }
                  `}
                >
                  <div className="flex items-start gap-3">
                    <FileText className="h-4 w-4 text-zinc-500 mt-0.5 shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white truncate">
                        {item.title}
                      </p>
                      <p className="text-xs text-zinc-500 mt-0.5">
                        {new Date(item.timestamp).toLocaleDateString()}
                      </p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        removeFromHistory(item.id);
                      }}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/20 rounded text-red-400 transition-opacity"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </aside>
    </>
  );
};
