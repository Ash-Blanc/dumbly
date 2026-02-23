export const Skeleton = ({ className = '', ...props }) => (
  <div
    className={`
      animate-pulse bg-zinc-800 rounded
      ${className}
    `}
    {...props}
  />
);

export const SkeletonText = ({ lines = 3, className = '' }) => (
  <div className={`space-y-2 ${className}`}>
    {Array.from({ length: lines }).map((_, i) => (
      <Skeleton
        key={i}
        className={`h-4 ${i === lines - 1 ? 'w-3/4' : 'w-full'}`}
      />
    ))}
  </div>
);
