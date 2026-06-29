/**
 * Rounded, bordered glass-effect card — the base surface used throughout
 * the app for everything from nav to dashboard tiles.
 */
export default function GlassCard({ children, className = '', hoverLift = false, as: Tag = 'div', ...rest }) {
  return (
    <Tag
      className={`rounded-3xl border border-line bg-slate/60 backdrop-blur-xl ${
        hoverLift ? 'transition-colors duration-300 hover:border-lime/40' : ''
      } ${className}`}
      {...rest}
    >
      {children}
    </Tag>
  );
}
