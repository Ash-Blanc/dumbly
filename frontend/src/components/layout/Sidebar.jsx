import { useState } from 'react';
import { Menu, X, Sun, Moon, Search, Sparkles, History, Trash2 } from 'lucide-react';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { useTheme } from '../../hooks/useTheme';
import { useHistory } from '../../hooks/useHistory';

export const Sidebar = ({ isOpen, onClose, currentAnalysisId }) => {
  const { theme, toggleTheme } = useTheme();
  const { history, removeFromHistory, clearHistory } = useHistory();

  if (!isOpen) return null;

  return (
    <aside
      className={`
        fixed inset-y-0 right-0 top-0 z-40 h-full
        bg-black/50 backdrop-blur-sm
        transform translate-x-full
        ${isOpen ? 'translate-x-0' : 'translate-x-full'}
      `}
      onClick={onClose}
      className="absolute inset-y-0 top-4 right-4 text-zinc-500 hover:text-white"
    >
      <X className="h-5 w-5" />
    </aside>

    <div className={`
      w-80 max-w-xs
      bg-zinc-900 border-r border-zinc-800
      transform translate-x-4
      ${isOpen ? 'translate-x-0' : 'translate-x-0'}
    `}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800">
        <h2 className="text-sm font-semibold text-white">History</h2>
        <button
          onClick={onClose}
          className="p-1 hover:bg-zinc-800 rounded"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Theme Toggle */}
      <div className="flex items-center gap-2 px-4 py-2 border-b border-zinc-800">
          <span className="text-xs text-zinc-500">Theme</span>
          <button
            onClick={toggleTheme}
            className="p-2 rounded bg-zinc-800 hover:bg-zinc-700"
          >
            {theme === 'dark' ? (
              <Sun className="h-4 w-4 text-amber-400" />
            ) : (
              <Moon className="h-4 w-4 text-violet-400" />
            )}
          </button>
        </div>

        {/* History List */}
        <div className="flex-1 overflow-y-auto">
          {history.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-zinc-500">
              <History className="h-8 w-8 opacity-50" />
              <p className="text-sm">No analyses yet</p>
            </div>
          ) : (
            <div className="space-y-1 p-2">
              {history.map((item) => (
                <button
                  key={item.id}
                  onClick={() => removeFromHistory(item.id)}
                  className={`
                    w-full text-left p-3 rounded-lg
                    ${currentAnalysis?.id === item.id ? 'bg-violet-500/10 border-violet-500' : 'hover:bg-zinc-800/50'}
                    transition-colors
                  `}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white truncate">
item.title}</p>
                      <span className="text-xs text-zinc-500">
                        {new Date(item.timestamp).toLocaleDateString()}
                      </span>
                    </div>
                  ))}
                ))}
              </div>
            )}

            {/* Clear All */}
            {history.length > 0 && (
              <div className="px-4 py-2 border-t border-zinc-800">
                <Button variant="ghost" size="sm" onClick={clearHistory}>
                  <Trash2 className="h-3 w-3 mr-1" />
                  Clear all
                </Button>
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  );
};
