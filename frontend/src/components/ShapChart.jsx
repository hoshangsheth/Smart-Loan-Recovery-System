import { BarChart, Bar, XAxis, YAxis, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { Lightbulb } from 'lucide-react';
import GlassCard from './GlassCard';

export default function ShapChart({ features }) {
  if (!features?.length) return null;

  const chartData = features.map((f) => ({
    name: f.feature,
    impact: Math.round(f.shap_value * 1000) / 1000,
    direction: f.direction,
  }));

  return (
    <GlassCard className="p-8" hoverLift>
      <div className="flex items-center gap-3 mb-2">
        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-lime/10 text-lime">
          <Lightbulb size={18} />
        </div>
        <h3 className="font-display text-lg font-semibold text-white">SHAP Feature Impact</h3>
      </div>
      <p className="text-xs text-mute mb-4">
        How much each factor pushed the predicted risk up or down.
      </p>

      <div style={{ width: '100%', height: 220 }}>
        <ResponsiveContainer>
          <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 16 }}>
            <XAxis type="number" hide />
            <YAxis
              type="category"
              dataKey="name"
              width={130}
              tick={{ fill: '#7A8079', fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{ background: '#14181A', border: '1px solid #1F2421', borderRadius: 12 }}
              labelStyle={{ color: 'white' }}
              formatter={(value) => [value, 'SHAP value']}
            />
            <Bar dataKey="impact" radius={[6, 6, 6, 6]}>
              {chartData.map((entry, i) => (
                <Cell key={i} fill={entry.direction === 'increased' ? '#F1473B' : '#4ADE80'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <ul className="mt-4 space-y-2">
        {features.map((f) => (
          <li key={f.feature} className="text-xs text-mute leading-relaxed">
            <span className="text-white font-medium">{f.feature}:</span> {f.description}{' '}
            <span className={f.direction === 'increased' ? 'text-risk-high' : 'text-risk-low'}>
              This {f.direction} the predicted risk.
            </span>
          </li>
        ))}
      </ul>
    </GlassCard>
  );
}
