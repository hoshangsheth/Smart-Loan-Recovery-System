import { Wallet } from 'lucide-react';
import GlassCard from './GlassCard';
import { formatCurrencyINR } from '../utils/risk';

export default function EmiSummaryCard({ calculated, loanAmount, outstandingLoan }) {
  const rows = [
    { label: 'Monthly EMI', value: formatCurrencyINR(calculated.monthly_emi) },
    { label: 'Loan Amount', value: formatCurrencyINR(loanAmount) },
    { label: 'Outstanding', value: formatCurrencyINR(outstandingLoan) },
    { label: 'Interest Rate', value: `${calculated.interest_rate_used}%` },
    { label: 'Tenure', value: `${calculated.loan_tenure_used} months` },
  ];

  return (
    <GlassCard className="p-8" hoverLift>
      <div className="flex items-center gap-3 mb-4">
        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-lime/10 text-lime">
          <Wallet size={18} />
        </div>
        <h3 className="font-display text-lg font-semibold text-white">EMI Summary</h3>
      </div>
      <dl className="space-y-2.5">
        {rows.map((r) => (
          <div key={r.label} className="flex justify-between text-sm border-b border-line/60 pb-2 last:border-0 last:pb-0">
            <dt className="text-mute">{r.label}</dt>
            <dd className="text-white font-mono">{r.value}</dd>
          </div>
        ))}
      </dl>
    </GlassCard>
  );
}
