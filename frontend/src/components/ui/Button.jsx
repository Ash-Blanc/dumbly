import { forwardRef } from 'react';

const variants = {
  primary: 'bg-violet-600 hover:bg-violet-500 text-white shadow-lg shadow-violet-500/20',
  secondary: 'bg-zinc-800 hover:bg-zinc-700 text-zinc-100 border border-zinc-700',
  ghost: 'bg-transparent hover:bg-zinc-800 text-zinc-400 hover:text-white',
  danger: 'bg-red-600/10 hover:bg-red-600/20 text-red-400 border border-red-600/20',
  success: 'bg-emerald-600/10 hover:bg-emerald-600/20 text-emerald-400 border border-emerald-600/20',
};

const sizes = {
  xs: 'px-2 py-1 text-xs gap-1',
  sm: 'px-3 py-1.5 text-xs gap-1.5',
  md: 'px-4 py-2 text-sm gap-2',
  lg: 'px-5 py-2.5 text-base gap-2',
  icon: 'p-2',
};

export const Button = forwardRef(({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  disabled = false,
  loading = false,
  ...props
}, ref) => {
  return (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={`
        inline-flex items-center justify-center
        font-medium rounded-lg
        transition-all duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
      {...props}
    >
      {loading && (
        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      )}
      {children}
    </button>
  );
});

Button.displayName = 'Button';

export const IconButton = forwardRef(({ children, className = '', ...props }, ref) => (
  <Button
    ref={ref}
    size="icon"
    variant="ghost"
    className={className}
    {...props}
  >
    {children}
  </Button>
));

IconButton.displayName = 'IconButton';
