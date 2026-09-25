import { Link } from 'react-router-dom';

export default function ConsentCheckbox({ checked, onChange, id = 'terms-consent' }) {
  return (
    <label htmlFor={id} className="flex items-start gap-3 cursor-pointer select-none text-sm text-mute">
      <input
        id={id}
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="mt-0.5 w-4 h-4 shrink-0 rounded accent-lime"
      />
      <span>
        I agree to the{' '}
        <Link to="/terms" target="_blank" className="text-lime hover:underline">
          Terms &amp; Conditions
        </Link>{' '}
        and{' '}
        <Link to="/privacy" target="_blank" className="text-lime hover:underline">
          Privacy Policy
        </Link>
        , and I'll follow the{' '}
        <Link to="/responsible-recovery" target="_blank" className="text-lime hover:underline">
          Responsible Recovery guidelines
        </Link>{' '}
        when contacting borrowers.
      </span>
    </label>
  );
}
