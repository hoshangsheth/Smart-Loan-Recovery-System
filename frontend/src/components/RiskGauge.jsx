import { motion } from 'framer-motion';
import { getDashboardRiskBand, RISK_COLORS } from '../utils/risk';

/**
 * Animated circular risk gauge — the signature visual element of the app.
 * A small static-feeling version appears in the hero; a large interactive
 * version anchors the results dashboard.
 *
 * `score` is 0-1. The arc sweeps 270° (from -135° to +135°), matching a
 * classic speedometer layout, and recolors across the same three zones
 * used by the dashboard border / gauge chart on the backend.
 */
export default function RiskGauge({ score = 0, size = 220, strokeWidth = 16, animate = true }) {
  const band = getDashboardRiskBand(score);
  const color = RISK_COLORS[band];

  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const sweepFraction = 270 / 360;
  const arcLength = circumference * sweepFraction;

  const targetOffset = arcLength * (1 - score);

  const center = size / 2;

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="-rotate-[225deg]"
      >
        {/* Track */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="#1F2421"
          strokeWidth={strokeWidth}
          strokeDasharray={`${arcLength} ${circumference}`}
          strokeLinecap="round"
        />
        {/* Progress arc */}
        <motion.circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={`${arcLength} ${circumference}`}
          strokeLinecap="round"
          initial={animate ? { strokeDashoffset: arcLength } : false}
          animate={{ strokeDashoffset: targetOffset }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
          style={{ filter: `drop-shadow(0 0 8px ${color}66)` }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.span
          className="font-display font-bold tabular-nums"
          style={{ fontSize: size * 0.2, color }}
          initial={animate ? { opacity: 0 } : false}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.6 }}
        >
          {Math.round(score * 100)}%
        </motion.span>
        <span className="text-xs uppercase tracking-wider text-mute mt-1">Risk Score</span>
      </div>
    </div>
  );
}
