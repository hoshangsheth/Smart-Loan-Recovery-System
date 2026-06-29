import { ClipboardList } from 'lucide-react';
import GlassCard from './GlassCard';

export default function RecoveryStrategyCard({ strategy }) {
  return (
    <GlassCard className="p-8" hoverLift>
      <div className="flex items-center gap-3 mb-4">
        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-lime/10 text-lime">
          <ClipboardList size={18} />
        </div>
        <h3 className="font-display text-lg font-semibold text-white">Recommended Recovery Strategy</h3>
      </div>
      <p className="text-mute leading-relaxed">{strategy}</p>
    </GlassCard>
  );
}
