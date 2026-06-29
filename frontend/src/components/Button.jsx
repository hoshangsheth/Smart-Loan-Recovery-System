const VARIANTS = {
  primary: 'bg-lime text-night hover:bg-lime-dim',
  ghost: 'border border-line text-white hover:border-lime/50 hover:text-lime',
  subtle: 'bg-slate-soft text-white hover:bg-line',
};

export default function Button({
  children,
  variant = 'primary',
  className = '',
  type = 'button',
  ...rest
}) {
  return (
    <button
      type={type}
      className={`inline-flex items-center justify-center gap-2 rounded-full px-6 py-3 font-medium text-sm tracking-tight transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed ${VARIANTS[variant]} ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}
