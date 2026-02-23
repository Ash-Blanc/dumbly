import { Menu, Sun, Moon, History, Sparkles } from 'lucide-react';
import { Button } from '../ui/Button';
import { useTheme } from '../../hooks/useTheme';

export const Header = ({ onMenuClick, hasHistory = false }) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="flex items-center justify-between py-4 mb-8">
      {/* Left: Menu + Logo */}
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          onClick={onMenuClick}
          className="lg:hidden"
        >
          <Menu className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight">
            <span className="text-white">arXiv</span>{' '}
            <span className="text-violet-400">SaaS</span>
          </h1>
          <p className="text-xs text-zinc-500 mt-0.5">Transform research into startups</p>
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2">
        {hasHistory && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onMenuClick}
            className="hidden lg:flex"
          >
            <History className="h-4 w-4" />
          </Button>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
        >
          {theme === 'dark' ? (
            <Sun className="h-4 w-4 text-amber-400" />
          ) : (
            <Moon className="h-4 w-4 text-violet-400" />
          )}
        </Button>
      </div>
    </header>
  );
};
