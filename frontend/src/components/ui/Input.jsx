import { forwardRef } from 'react';

const variants = {
  default: 'bg-zinc-900 border-zinc-800',
  elevated: 'bg-zinc-800 border-zinc-700',
  ghost: 'bg-transparent border-transparent',
};

export const Input = forwardRef(({
  className = '',
  variant = 'default',
  error = false,
  icon: Icon,
  suffix,
  size = 'md',
  ...props
}, ref) => {
  const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2.5 text-sm',
    lg: 'px-5 py-3 text-base',
  };

  return (
    <div className="relative">
      {Icon && (
        <Icon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
      )}
      <input
        ref={ref}
        className={`
          w-full border rounded-lg
          text-white placeholder:text-zinc-500
          focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500
          transition-all duration-200
          ${variants[variant]}
          ${sizes[size]}
          ${Icon ? 'pl-10' : ''}
          ${suffix ? 'pr-20' : ''}
          ${error ? 'border-red-500 focus:ring-red-500/50' : ''}
          ${className}
        `}
        {...props}
      />
      {suffix && (
        <div className="absolute right-3 top-1/2 -translate-y-1/2">
          {suffix}
        </div>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export const Textarea = forwardRef(({
  className = '',
  error = false,
  ...props
}, ref) => {
  return (
    <textarea
      ref={ref}
      className={`
        w-full bg-zinc-900 border border-zinc-800 rounded-lg
        px-4 py-3 text-sm text-white placeholder:text-zinc-500
        focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500
        transition-all duration-200 resize-none
        ${error ? 'border-red-500' : ''}
        ${className}
      `}
      {...props}
    />
  );
});

Textarea.displayName = 'Textarea';
