import { useState } from 'react';
import { Loader2, ShieldCheck } from 'lucide-react';
import GlassCard from './GlassCard';
import Button from './Button';
import ConsentCheckbox from './ConsentCheckbox';
import { useAuth } from '../context/AuthContext';

/** Blocks the app for signed-in users until they accept the current terms version. */
export default function ConsentGate() {
  const { acceptCurrentTerms, signOut } = useAuth();
  const [checked, setChecked] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);

  async function handleAccept() {
    setIsSaving(true);
    setError(null);
    try {
      await acceptCurrentTerms();
    } catch (err) {
      setError(err.message);
      setIsSaving(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center bg-night/90 backdrop-blur-sm px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="consent-title"
    >
      <GlassCard className="w-full max-w-md p-6 sm:p-8">
        <ShieldCheck className="text-lime mb-4" size={28} />
        <h2 id="consent-title" className="font-display text-2xl font-bold text-white">
          One step before you continue
        </h2>
        <p className="text-sm text-mute mt-3 mb-6">
          Recovia handles borrower data and AI-generated recovery guidance, so we need your agreement to our terms
          before you save cases or generate AI briefs.
        </p>
        <ConsentCheckbox checked={checked} onChange={setChecked} />
        {error && (
          <p role="alert" className="mt-4 text-sm text-risk-high">
            {error}
          </p>
        )}
        <Button className="w-full mt-6" onClick={handleAccept} disabled={!checked || isSaving}>
          {isSaving && <Loader2 size={16} className="animate-spin" />}
          Accept and continue
        </Button>
        <button onClick={signOut} className="w-full mt-3 text-sm text-mute hover:text-white">
          Sign out instead
        </button>
      </GlassCard>
    </div>
  );
}
