import { useState } from 'react';
import { Search, Sparkles, Loader2 } from 'lucide-react';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { detectInputType, getInputTypeLabel } from '../../utils/inputDetection';

const EXAMPLES = [
  { value: '2303.12712', label: 'Attention paper' },
  { value: '2005.11401', label: 'RAG paper' },
  { value: 'transformer architectures', label: 'Topic search' },
];

export const SearchInput = ({ onSubmit, disabled = false }) => {
  const [input, setInput] = useState('');
  const [focused, setFocused] = useState(false);
  const detectedType = input.trim() ? detectInputType(input) : null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSubmit(input.trim());
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <form onSubmit={handleSubmit}>
        <div className="relative">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder="arXiv ID, URL, or research topic..."
            icon={Search}
            disabled={disabled}
            className="h-12 text-base pr-24"
            suffix={
              detectedType && (
                <Badge variant="primary" size="sm">
                  {getInputTypeLabel(detectedType)}
                </Badge>
              )
            }
          />
          <Button
            type="submit"
            disabled={!input.trim() || disabled}
            loading={disabled}
            className="absolute right-1.5 top-1/2 -translate-y-1/2"
          >
            {disabled ? null : <Sparkles className="h-4 w-4" />}
          </Button>
        </div>
      </form>

      {/* Quick examples */}
      {!input && (
        <div className="flex items-center gap-2 mt-3 justify-center">
          <span className="text-xs text-zinc-500">Try:</span>
          {EXAMPLES.map((example) => (
            <button
              key={example.value}
              onClick={() => setInput(example.value)}
              className="text-xs px-2 py-1 rounded bg-zinc-800/50 text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
            >
              {example.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
