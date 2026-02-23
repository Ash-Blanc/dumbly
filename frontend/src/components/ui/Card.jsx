import { forwardRef } from 'react';

const variants = {
  default: 'bg-zinc-900/50 border-zinc-800',
  elevated: 'bg-zinc-900 border-zinc-700 shadow-lg',
  interactive: 'bg-zinc-900/50 border-zinc-800 hover:border-zinc-700 hover:bg-zinc-900/70',
  highlight: 'bg-violet-500/5 border-violet-500/20',
};

export const Card = forwardRef(({
  children,
  className = '',
  variant = 'default',
  padding = 'md',
  ...props
}, ref) => {
  const paddingSizes = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };

  return (
    <div
      ref={ref}
      className={`
        rounded-xl border
        transition-all duration-200
        ${variants[variant]}
        ${paddingSizes[padding]}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
});

Card.displayName = 'Card';

export const CardHeader = ({ children, className = '', action }) => (
  <div className={`flex items-start justify-between gap-3 mb-3 ${className}`}>
    <div className="flex-1">{children}</div>
    {action && <div>{action}</div>}
  </div>
);

export const CardTitle = ({ children, className = '' }) => (
  <h3 className={`text-base font-semibold text-white ${className}`}>{children}</h3>
);

export const CardDescription = ({ children, className = '' }) => (
  <p className={`text-sm text-zinc-400 mt-1 ${className}`}>{children}</p>
);

export const CardContent = ({ children, className = '' }) => (
  <div className={className}>{children}</div>
);

export const CardFooter = ({ children, className = '' }) => (
  <div className={`mt-4 pt-4 border-t border-zinc-800 ${className}`}>{children}</div>
);
