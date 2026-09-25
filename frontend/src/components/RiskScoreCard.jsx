import { AlertTriangle, Scale } from 'lucide-react';
import GlassCard from './GlassCard';
import RiskGauge from './RiskGauge';
import { resolveBand, RISK_COLORS } from '../utils/risk';

export default function RiskScoreCard({ riskScore, riskCategory, riskBand, assetClassification, policyOverride, warning }) {
  const band = resolveBand({ band: riskBand, category: riskCategory, score: riskScore });
  const color = RISK_COLORS[band];

  return (
    <GlassCard className="p-8 flex flex-col items-center text-center" hoverLift>
      <RiskGauge score={riskScore} band={band} size={180} />
      <p className="text-xs text-mute mt-2 max-w-[16rem]">Estimated chance this loan is not fully recovered</p>
      <div className="mt-4">
        <p className="text-xs uppercase tracking-wider text-mute mb-1">Risk Category</p>
        <p className="font-display text-xl font-semibold" style={{ color }}>{riskCategory}</p>
        {assetClassification && (
          <span className="inline-block mt-2 rounded-full border border-line px-3 py-1 text-xs text-white font-mono">
            RBI class: {assetClassification}
          </span>
        )}
      </div>
      {policyOverride && (
        <div className="mt-4 flex items-start gap-2 text-left rounded-xl border border-line bg-slate-soft px-4 py-3">
          <Scale size={16} className="text-lime shrink-0 mt-0.5" />
          <p className="text-xs text-mute">
            <span className="text-white">Raised by policy.</span> {policyOverride}
          </p>
        </div>
      )}
      {warning && (
        <div className="mt-4 flex items-start gap-2 text-left rounded-xl border border-risk-medium/30 bg-risk-medium/10 px-4 py-3">
          <AlertTriangle size={16} className="text-risk-medium shrink-0 mt-0.5" />
          <p className="text-xs text-risk-medium">{warning}</p>
        </div>
      )}
    </GlassCard>
  );
}
