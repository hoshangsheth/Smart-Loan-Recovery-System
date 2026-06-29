import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { BarChart3 } from 'lucide-react';
import GlassCard from './GlassCard';

function FeatureBarChart({ chart }) {
  if (!chart) return null;
  return (
    <GlassCard className="p-6" hoverLift>
      <h4 className="text-sm font-semibold text-white mb-3">Engineered Feature Percentages</h4>
      <div style={{ width: '100%', height: 200 }}>
        <ResponsiveContainer>
          <BarChart data={chart.data}>
            <XAxis dataKey="label" tick={{ fill: '#7A8079', fontSize: 10 }} axisLine={false} tickLine={false} />
            <YAxis hide />
            <Tooltip
              contentStyle={{ background: '#14181A', border: '1px solid #1F2421', borderRadius: 12 }}
              formatter={(value) => [`${value}%`, 'Value']}
            />
            <Bar dataKey="value" fill="#D9FF3D" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="text-xs text-mute mt-3">{chart.caption}</p>
    </GlassCard>
  );
}

function DonutChart({ chart, title }) {
  if (!chart) return null;
  return (
    <GlassCard className="p-6" hoverLift>
      <h4 className="text-sm font-semibold text-white mb-3">{title}</h4>
      <div style={{ width: '100%', height: 200 }}>
        <ResponsiveContainer>
          <PieChart>
            <Pie data={chart.data} dataKey="value" nameKey="label" innerRadius={55} outerRadius={80} paddingAngle={2}>
              {chart.data.map((entry, i) => (
                <Cell key={i} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip contentStyle={{ background: '#14181A', border: '1px solid #1F2421', borderRadius: 12 }} />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="flex justify-center gap-4 mt-2">
        {chart.data.map((d) => (
          <div key={d.label} className="flex items-center gap-1.5 text-xs text-mute">
            <span className="w-2.5 h-2.5 rounded-full" style={{ background: d.color }} />
            {d.label}
          </div>
        ))}
      </div>
      <p className="text-xs text-mute mt-3">{chart.caption}</p>
    </GlassCard>
  );
}

export default function AnalyticsCharts({ analytics }) {
  if (!analytics) return null;

  return (
    <div>
      <div className="flex items-center gap-3 mb-5">
        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-lime/10 text-lime">
          <BarChart3 size={18} />
        </div>
        <h3 className="font-display text-lg font-semibold text-white">Analytical Visuals &amp; Key Metrics</h3>
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        <FeatureBarChart chart={analytics.feature_percentage_chart} />
        <DonutChart chart={analytics.payment_history_chart} title="Payment History" />
        <DonutChart chart={analytics.loan_vs_collateral_chart} title="Loan vs Collateral Value" />
      </div>
      {analytics.collateral_coverage_insight && (
        <p
          className={`text-sm mt-5 rounded-xl border px-4 py-3 ${
            analytics.collateral_coverage_insight.level === 'warning'
              ? 'border-risk-medium/30 bg-risk-medium/10 text-risk-medium'
              : analytics.collateral_coverage_insight.level === 'success'
              ? 'border-risk-low/30 bg-risk-low/10 text-risk-low'
              : 'border-line bg-slate-soft text-mute'
          }`}
        >
          {analytics.collateral_coverage_insight.message}
        </p>
      )}
    </div>
  );
}
