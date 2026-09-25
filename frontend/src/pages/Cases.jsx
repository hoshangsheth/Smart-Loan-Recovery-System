import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ChevronRight, Loader2, Plus } from 'lucide-react';
import PageShell from '../components/PageShell';
import GlassCard from '../components/GlassCard';
import Button from '../components/Button';
import { listCases } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { CASE_STATUSES, CASE_STATUS_LABELS } from '../constants/caseStatus';
import { formatPercent, getDisplayRiskBand, RISK_COLORS } from '../utils/risk';

const FILTERS = [{ value: '', label: 'All' }, ...CASE_STATUSES];

export default function Cases() {
  const navigate = useNavigate();
  const { isAdmin } = useAuth();
  const [status, setStatus] = useState('');
  const [cases, setCases] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setCases(null);
    setError(null);
    listCases(status)
      .then((rows) => !cancelled && setCases(rows))
      .catch((err) => !cancelled && setError(err.message));
    return () => {
      cancelled = true;
    };
  }, [status]);

  return (
    <PageShell>
      <div className="flex flex-wrap items-end justify-between gap-4 mb-8">
        <div>
          <span className="text-xs uppercase tracking-wider text-lime">{isAdmin ? 'All cases' : 'My cases'}</span>
          <h1 className="font-display text-3xl sm:text-4xl font-bold text-white mt-2">Recovery queue</h1>
          <p className="text-mute text-sm mt-2">Sorted by current risk, highest first.</p>
        </div>
        <Button onClick={() => navigate('/predictor')}>
          <Plus size={16} /> New case
        </Button>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-2 mb-6" role="tablist" aria-label="Filter by status">
        {FILTERS.map((f) => (
          <button
            key={f.value || 'all'}
            role="tab"
            aria-selected={status === f.value}
            onClick={() => setStatus(f.value)}
            className={`shrink-0 rounded-full border px-4 py-2 text-sm transition-colors ${
              status === f.value ? 'border-lime bg-lime text-night' : 'border-line text-mute hover:text-white'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {error && (
        <p role="alert" className="rounded-xl border border-risk-high/30 bg-risk-high/10 px-4 py-3 text-sm text-risk-high">
          Couldn't load cases: {error}
        </p>
      )}

      {!error && cases === null && (
        <div className="flex items-center justify-center gap-2 py-16 text-mute" role="status">
          <Loader2 size={18} className="animate-spin" /> Loading cases…
        </div>
      )}

      {cases?.length === 0 && (
        <GlassCard className="p-10 text-center">
          <p className="text-white font-medium">No cases here yet.</p>
          <p className="text-mute text-sm mt-2">Run a prediction while signed in and it's saved as a case.</p>
        </GlassCard>
      )}

      {cases?.length > 0 && (
        <ul className="space-y-3">
          {cases.map((c) => {
            const band = c.latest_risk_score == null ? null : getDisplayRiskBand(c.latest_risk_score);
            return (
              <li key={c.id}>
                <Link to={`/cases/${c.id}`} className="block group">
                  <GlassCard className="flex items-center gap-4 px-5 py-4" hoverLift>
                    <div
                      className="w-1.5 self-stretch rounded-full"
                      style={{ background: band ? RISK_COLORS[band] : 'var(--color-line)' }}
                      aria-hidden="true"
                    />
                    <div className="min-w-0 flex-1">
                      <p className="text-white font-medium truncate">
                        {c.first_name} {c.last_name}
                      </p>
                      <p className="text-xs text-mute font-mono truncate">
                        {c.borrower_ref} · {c.loan_type}
                      </p>
                    </div>
                    <div className="text-right shrink-0">
                      <p className="font-display text-lg font-semibold" style={{ color: band ? RISK_COLORS[band] : undefined }}>
                        {c.latest_risk_score == null ? '—' : formatPercent(c.latest_risk_score, 1)}
                      </p>
                      <p className="text-xs text-mute">{CASE_STATUS_LABELS[c.status] ?? c.status}</p>
                    </div>
                    <ChevronRight size={18} className="text-mute group-hover:text-lime shrink-0" aria-hidden="true" />
                  </GlassCard>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </PageShell>
  );
}
