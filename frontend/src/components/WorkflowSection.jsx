import { motion } from 'framer-motion';
import { UserPlus, Wallet, Cpu, BarChart3, Lightbulb, ClipboardList, FileDown } from 'lucide-react';
import GlassCard from './GlassCard';

const STEPS = [
  { icon: UserPlus, title: 'Enter borrower details', desc: 'Name, age, gender, dependents — the basics that shape every downstream calculation.' },
  { icon: Wallet, title: 'Enter financial details', desc: 'Loan type, amount, collateral, missed payments. EMI and DPD are calculated automatically.' },
  { icon: Cpu, title: 'Generate prediction', desc: 'An XGBoost model scores default probability from 10 engineered features in milliseconds.' },
  { icon: BarChart3, title: 'View AI analysis', desc: 'Risk score, category, and borrower segment land in a dashboard built for fast decisions.' },
  { icon: Lightbulb, title: 'Understand SHAP explanations', desc: 'See exactly which factors pushed risk up or down, in plain business language.' },
  { icon: ClipboardList, title: 'Review recovery strategy', desc: 'A tailored action plan — from gentle reminders to legal escalation — based on risk and DPD.' },
  { icon: FileDown, title: 'Download the PDF report', desc: 'A polished, shareable report with every figure, the strategy, and the borrower segment.' },
];

export default function WorkflowSection() {
  return (
    <section className="px-6 py-24" id="workflow">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mb-14 max-w-2xl"
        >
          <span className="text-xs uppercase tracking-wider text-lime">The workflow</span>
          <h2 className="font-display text-4xl font-bold text-white mt-3 mb-4">
            Seven steps from intake to action.
          </h2>
          <p className="text-mute">
            Every prediction follows the same guided path — no spreadsheets, no guesswork, no
            black-box scores.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
          {STEPS.map((step, i) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: (i % 3) * 0.1 }}
            >
              <GlassCard className="p-6 h-full" hoverLift>
                <div className="flex items-center gap-3 mb-4">
                  <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-lime/10 text-lime">
                    <step.icon size={18} />
                  </div>
                  <span className="font-mono text-xs text-mute">{String(i + 1).padStart(2, '0')}</span>
                </div>
                <h3 className="font-semibold text-white mb-2">{step.title}</h3>
                <p className="text-sm text-mute leading-relaxed">{step.desc}</p>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
