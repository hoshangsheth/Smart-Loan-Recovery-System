import { UserCircle } from 'lucide-react';
import GlassCard from './GlassCard';

export default function BorrowerProfileCard({ input, borrowerId }) {
  return (
    <GlassCard className="p-8" hoverLift>
      <div className="flex items-center gap-3 mb-4">
        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-lime/10 text-lime">
          <UserCircle size={18} />
        </div>
        <div>
          <h3 className="font-display text-lg font-semibold text-white">
            {input.first_name} {input.last_name}
          </h3>
          <p className="text-xs text-mute font-mono">{borrowerId}</p>
        </div>
      </div>
      <dl className="grid grid-cols-2 gap-y-2.5 text-sm">
        <Row label="Age" value={input.age} />
        <Row label="Gender" value={input.gender} />
        <Row label="Dependents" value={input.num_dependents} />
        <Row label="Loan Type" value={input.loan_type} />
        <Row label="Missed Payments" value={input.missed_payments} />
      </dl>
    </GlassCard>
  );
}

function Row({ label, value }) {
  return (
    <div>
      <dt className="text-xs text-mute">{label}</dt>
      <dd className="text-white font-medium">{value}</dd>
    </div>
  );
}
