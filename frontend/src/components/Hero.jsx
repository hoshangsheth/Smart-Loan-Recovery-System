import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, TrendingDown, Users, FileCheck } from 'lucide-react';
import Button from './Button';
import GlassCard from './GlassCard';
import RiskGauge from './RiskGauge';

const FLOATING_STATS = [
  { icon: Users, label: 'Borrower segments', value: '4 profiles' },
  { icon: TrendingDown, label: 'Default risk modeled', value: 'XGBoost' },
  { icon: FileCheck, label: 'Reports generated', value: 'Instant PDF' },
];

export default function Hero() {
  const navigate = useNavigate();

  return (
    <section className="relative px-6 pt-40 pb-24 overflow-hidden" id="overview">
      {/* Ambient lime glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-lime/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="relative max-w-6xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <span className="inline-flex items-center gap-2 rounded-full border border-line bg-slate/60 px-4 py-1.5 text-xs uppercase tracking-wider text-lime mb-6">
            ML-Powered Recovery Intelligence
          </span>
          <h1 className="font-display text-5xl sm:text-6xl font-bold leading-[1.05] tracking-tight text-white mb-6">
            Know who'll <span className="text-lime">default</span> before they do.
          </h1>
          <p className="text-lg text-mute max-w-lg mb-8">
            Recovia scores every borrower's default risk in real time,
            explains exactly why, and recommends the recovery strategy most likely to
            bring the loan current - backed by SHAP-level transparency.
          </p>
          <div className="flex flex-wrap gap-4">
            <Button variant="primary" onClick={() => navigate('/predictor')}>
              Run Risk Assessment <ArrowRight size={16} />
            </Button>
            <Button variant="ghost" onClick={() => document.getElementById('workflow')?.scrollIntoView({ behavior: 'smooth' })}>
              See how it works
            </Button>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="relative flex justify-center"
        >
          <GlassCard className="p-10 flex flex-col items-center gap-4" hoverLift>
            <RiskGauge score={0.62} size={200} />
            <p className="text-sm text-mute text-center max-w-[220px]">
              Live model output - risk score, category, and strategy in one prediction call.
            </p>
          </GlassCard>

          {/* Floating stat cards */}
          {FLOATING_STATS.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 + i * 0.15, duration: 0.5 }}
              className={`absolute hidden sm:flex items-center gap-3 rounded-2xl border border-line bg-slate/90 backdrop-blur-xl px-4 py-3 shadow-xl ${
                i === 0 ? '-top-4 -right-8' : i === 1 ? 'top-1/2 -right-16' : '-bottom-6 -left-10'
              }`}
            >
              <stat.icon className="text-lime" size={18} />
              <div>
                <p className="text-[11px] text-mute leading-tight">{stat.label}</p>
                <p className="text-sm font-semibold text-white leading-tight">{stat.value}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
