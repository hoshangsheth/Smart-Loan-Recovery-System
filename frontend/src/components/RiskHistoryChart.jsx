import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { TrendingUp } from 'lucide-react';
import GlassCard from './GlassCard';

export default function RiskHistoryChart({ predictions }) {
  const data = predictions.map((p) => ({
    when: new Date(p.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }),
    risk: Math.round(p.risk_score * 1000) / 10,
    dpd: p.calculated.days_past_due,
  }));

  return (
    <GlassCard className="p-6 sm:p-8">
      <div className="flex items-center gap-3 mb-2">
        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-lime/10 text-lime">
          <TrendingUp size={18} />
        </div>
        <h3 className="font-display text-lg font-semibold text-white">Risk history</h3>
      </div>
      <p className="text-xs text-mute mb-4">
        {data.length === 1
          ? 'One score so far. Re-scoring as days past due and collection attempts change builds the trend.'
          : `${data.length} scores for this case.`}
      </p>
      <div style={{ width: '100%', height: 200 }}>
        <ResponsiveContainer>
          <LineChart data={data} margin={{ left: -16, right: 8, top: 8 }}>
            <CartesianGrid stroke="#1F2421" vertical={false} />
            <XAxis dataKey="when" tick={{ fill: '#7A8079', fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis
              domain={[0, 100]}
              unit="%"
              tick={{ fill: '#7A8079', fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{ background: '#14181A', border: '1px solid #1F2421', borderRadius: 12 }}
              labelStyle={{ color: 'white' }}
              formatter={(value, name) => (name === 'risk' ? [`${value}%`, 'Risk'] : [value, 'Days past due'])}
            />
            <Line type="monotone" dataKey="risk" stroke="#D9FF3D" strokeWidth={2} dot={{ r: 4, fill: '#D9FF3D' }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </GlassCard>
  );
}
