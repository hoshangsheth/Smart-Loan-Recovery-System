import GlassCard from './GlassCard';
import RiskGauge from './RiskGauge';
import { getDisplayRiskBand, isApproachingCriticalZone, RISK_COLORS } from '../utils/risk';
import { AlertTriangle } from 'lucide-react';

export default function RiskScoreCard({ riskScore, riskCategory }) {
  const band = getDisplayRiskBand(riskScore);
  const color = RISK_COLORS[band];
  const nearCritical = isApproachingCriticalZone(riskScore);

  return (
    <GlassCard className="p-8 flex flex-col items-center text-center" hoverLift>
      <RiskGauge score={riskScore} size={180} />
      <div className="mt-5">
        <p className="text-xs uppercase tracking-wider text-mute mb-1">Risk Category</p>
        <p className="font-display text-xl font-semibold" style={{ color }}>{riskCategory}</p>
      </div>
      {nearCritical && (
        <div className="mt-4 flex items-start gap-2 text-left rounded-xl border border-risk-medium/30 bg-risk-medium/10 px-4 py-3">
          <AlertTriangle size={16} className="text-risk-medium shrink-0 mt-0.5" />
          <p className="text-xs text-risk-medium">
            Borrower could likely enter the Critical Zone if any more payments are missed or
            compliance fails. Immediate attention recommended.
          </p>
        </div>
      )}
    </GlassCard>
  );
}
