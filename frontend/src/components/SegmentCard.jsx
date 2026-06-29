import { Layers } from 'lucide-react';
import GlassCard from './GlassCard';

export default function SegmentCard({ segment }) {
  if (!segment) return null;
  return (
    <GlassCard className="p-8" hoverLift>
      <div className="flex items-center gap-3 mb-4">
        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-lime/10 text-lime">
          <Layers size={18} />
        </div>
        <h3 className="font-display text-lg font-semibold text-white">Borrower Segment</h3>
      </div>
      <span className="inline-block rounded-full border border-lime/30 bg-lime/10 px-4 py-1.5 text-sm text-lime font-medium mb-3">
        {segment.segment_name}
      </span>
      <p className="text-mute leading-relaxed text-sm">{segment.description}</p>
    </GlassCard>
  );
}
