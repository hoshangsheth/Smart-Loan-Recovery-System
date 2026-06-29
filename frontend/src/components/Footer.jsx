import { ShieldCheck } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="px-6 py-10 border-t border-line">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-white font-display font-semibold">
          <ShieldCheck className="text-lime" size={18} />
          Recovia
        </div>
        <p className="text-sm text-mute">
          ML-assisted risk scoring for internal collections use. Not a substitute for
          regulatory or legal advice.
        </p>
      </div>
    </footer>
  );
}
