export function TextField({ label, hint, ...rest }) {
  return (
    <label className="block mb-5">
      <span className="block text-sm font-medium text-white mb-1.5">{label}</span>
      <input
        className="w-full rounded-xl border border-line bg-slate-soft px-4 py-3 text-white placeholder:text-mute/60 focus:border-lime/60 transition-colors"
        {...rest}
      />
      {hint && <span className="block text-xs text-mute mt-1.5">{hint}</span>}
    </label>
  );
}

export function NumberField({ label, hint, ...rest }) {
  return (
    <label className="block mb-5">
      <span className="block text-sm font-medium text-white mb-1.5">{label}</span>
      <input
        type="number"
        className="w-full rounded-xl border border-line bg-slate-soft px-4 py-3 text-white placeholder:text-mute/60 focus:border-lime/60 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        {...rest}
      />
      {hint && <span className="block text-xs text-mute mt-1.5">{hint}</span>}
    </label>
  );
}

export function SelectField({ label, hint, children, ...rest }) {
  return (
    <label className="block mb-5">
      <span className="block text-sm font-medium text-white mb-1.5">{label}</span>
      <select
        className="w-full rounded-xl border border-line bg-slate-soft px-4 py-3 text-white focus:border-lime/60 transition-colors appearance-none"
        {...rest}
      >
        {children}
      </select>
      {hint && <span className="block text-xs text-mute mt-1.5">{hint}</span>}
    </label>
  );
}

export function CheckboxField({ label, ...rest }) {
  return (
    <label className="flex items-center gap-3 mb-5 cursor-pointer select-none">
      <input type="checkbox" className="w-4 h-4 rounded accent-lime" {...rest} />
      <span className="text-sm text-white">{label}</span>
    </label>
  );
}
