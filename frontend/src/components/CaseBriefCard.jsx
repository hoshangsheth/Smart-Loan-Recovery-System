import { useState } from 'react';
import { AlertTriangle, Check, Copy, Loader2, Sparkles } from 'lucide-react';
import GlassCard from './GlassCard';
import Button from './Button';
import { generateCaseBrief } from '../services/api';
import { useAuth } from '../context/AuthContext';

const PRIORITY_STYLES = {
  immediate: 'border-risk-high/40 bg-risk-high/10 text-risk-high',
  this_week: 'border-risk-medium/40 bg-risk-medium/10 text-risk-medium',
  monitor: 'border-line bg-slate-soft text-mute',
};
const PRIORITY_LABELS = { immediate: 'Immediate', this_week: 'This week', monitor: 'Monitor' };
const CHANNEL_LABELS = {
  call: 'Call',
  sms: 'SMS',
  email: 'Email',
  whatsapp: 'WhatsApp',
  field_visit: 'Field visit',
  legal_notice: 'Legal notice',
  internal: 'Internal',
};

export default function CaseBriefCard({ caseId, brief, borrowerFirstName, onGenerated }) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const { profile, refreshProfile } = useAuth();
  const usage = profile?.briefs;
  const remaining = usage?.limit == null ? null : Math.max(usage.limit - usage.used, 0);
  const outOfBriefs = remaining === 0;

  async function handleGenerate() {
    setIsGenerating(true);
    setError(null);
    try {
      onGenerated(await generateCaseBrief(caseId));
    } catch (err) {
      setError(err.message);
    } finally {
      setIsGenerating(false);
      refreshProfile();
    }
  }

  // The LLM only ever sees a {borrower_name} placeholder; the name is filled in here, in the browser.
  const outreach = brief?.content.outreach_draft.replaceAll('{borrower_name}', borrowerFirstName);

  async function handleCopy() {
    await navigator.clipboard.writeText(outreach);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <GlassCard className="p-6 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-lime/10 text-lime">
            <Sparkles size={18} />
          </div>
          <div>
            <h3 className="font-display text-lg font-semibold text-white">AI case brief</h3>
            <p className="text-xs text-mute">Explains the model's score. It never changes it.</p>
          </div>
        </div>
        <Button variant={brief ? 'ghost' : 'primary'} onClick={handleGenerate} disabled={isGenerating || outOfBriefs}>
          {isGenerating ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
          {isGenerating ? 'Generating…' : brief ? 'Regenerate' : 'Generate brief'}
        </Button>
      </div>

      {remaining !== null && (
        <p className="text-xs text-mute mb-4" aria-live="polite">
          {outOfBriefs ? 'No AI briefs left' : `${remaining} of ${usage.limit} AI briefs left`} in the last 24 hours
          {usage.resets_at &&
            ` · next one frees up ${new Date(usage.resets_at).toLocaleString('en-IN', {
              dateStyle: 'medium',
              timeStyle: 'short',
            })}`}
        </p>
      )}
      {isGenerating && (
        <p className="text-sm text-mute mb-4" role="status">
          Usually 5–15 seconds. The first request after a quiet period can take up to a minute.
        </p>
      )}
      {error && (
        <p role="alert" className="mb-4 rounded-xl border border-risk-high/30 bg-risk-high/10 px-4 py-3 text-sm text-risk-high">
          {error}
        </p>
      )}

      {!brief && !isGenerating && !error && (
        <p className="text-mute text-sm">
          Generate a brief for a plain-language summary, the main risk drivers, prioritized next steps, and a
          compliant first-contact message.
        </p>
      )}

      {brief && (
        <div className="space-y-6">
          <p className="text-white leading-relaxed">{brief.content.summary}</p>

          <section>
            <h4 className="text-xs uppercase tracking-wider text-mute mb-2">Why the risk is what it is</h4>
            <ul className="space-y-1.5">
              {brief.content.key_risk_drivers.map((d) => (
                <li key={d} className="text-sm text-white/90 leading-relaxed flex gap-2">
                  <span className="text-lime" aria-hidden="true">•</span>
                  {d}
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h4 className="text-xs uppercase tracking-wider text-mute mb-2">Next actions</h4>
            <ol className="space-y-3">
              {brief.content.recommended_actions.map((a) => (
                <li key={a.action} className="rounded-2xl border border-line bg-slate-soft p-4">
                  <div className="flex flex-wrap items-center gap-2 mb-1.5">
                    <span className={`rounded-full border px-2.5 py-0.5 text-xs font-medium ${PRIORITY_STYLES[a.priority]}`}>
                      {PRIORITY_LABELS[a.priority]}
                    </span>
                    <span className="rounded-full border border-line px-2.5 py-0.5 text-xs text-mute">
                      {CHANNEL_LABELS[a.channel] ?? a.channel}
                    </span>
                  </div>
                  <p className="text-white text-sm font-medium">{a.action}</p>
                  <p className="text-mute text-sm mt-1">{a.rationale}</p>
                </li>
              ))}
            </ol>
          </section>

          <section>
            <div className="flex items-center justify-between gap-2 mb-2">
              <h4 className="text-xs uppercase tracking-wider text-mute">Draft message to borrower</h4>
              <button
                onClick={handleCopy}
                className="inline-flex items-center gap-1.5 text-xs text-mute hover:text-lime transition-colors"
              >
                {copied ? <Check size={14} /> : <Copy size={14} />}
                {copied ? 'Copied' : 'Copy'}
              </button>
            </div>
            <p className="rounded-2xl border border-line bg-slate-soft p-4 text-sm text-white/90 whitespace-pre-line">
              {outreach}
            </p>
            <p className="text-xs text-mute mt-2">Review before sending. Contact borrowers only between 8 AM and 7 PM.</p>
          </section>

          {brief.content.caveats.length > 0 && (
            <section className="rounded-2xl border border-risk-medium/30 bg-risk-medium/10 p-4">
              <h4 className="flex items-center gap-2 text-xs uppercase tracking-wider text-risk-medium mb-2">
                <AlertTriangle size={14} /> Check before acting
              </h4>
              <ul className="space-y-1">
                {brief.content.caveats.map((c) => (
                  <li key={c} className="text-sm text-risk-medium">
                    {c}
                  </li>
                ))}
              </ul>
            </section>
          )}

          <p className="text-xs text-mute font-mono">
            {brief.llm_model} · {(brief.latency_ms / 1000).toFixed(1)}s ·{' '}
            {new Date(brief.created_at).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}
          </p>
        </div>
      )}
    </GlassCard>
  );
}
