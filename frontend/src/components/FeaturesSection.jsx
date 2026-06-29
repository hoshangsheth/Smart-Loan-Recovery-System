import { motion } from 'framer-motion';
import { Brain, Layers, ShieldAlert, FileBarChart } from 'lucide-react';
import GlassCard from './GlassCard';

const FEATURES = [
  {
    icon: Brain,
    title: 'Explainable risk scoring',
    desc: 'Every prediction comes with SHAP-based feature attributions, so collections teams know exactly why a score landed where it did.',
  },
  {
    icon: Layers,
    title: 'Borrower segmentation',
    desc: 'A separate clustering model groups borrowers into business-meaningful profiles like "High Income, Low Default Risk" - independent of the risk score itself.',
  },
  {
    icon: ShieldAlert,
    title: 'Tiered recovery strategy',
    desc: 'Strategy recommendations scale from automated reminders to legal escalation, driven by both risk score and days past due.',
  },
  {
    icon: FileBarChart,
    title: 'One-click PDF reporting',
    desc: 'Every borrower profile, score, and strategy is ready to export as a clean, shareable report - no screenshots required.',
  },
];

export default function FeaturesSection() {
  return (
    <section className="px-6 py-24">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mb-14 max-w-2xl"
        >
          <span className="text-xs uppercase tracking-wider text-lime">Platform</span>
          <h2 className="font-display text-4xl font-bold text-white mt-3">
            Built for collections professionals.
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-5">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.1 }}
            >
              <GlassCard className="p-8 h-full" hoverLift>
                <div className="flex items-center justify-center w-12 h-12 rounded-2xl bg-lime/10 text-lime mb-5">
                  <f.icon size={22} />
                </div>
                <h3 className="font-display text-xl font-semibold text-white mb-3">{f.title}</h3>
                <p className="text-mute leading-relaxed">{f.desc}</p>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
