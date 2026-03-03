import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ResponsiveContainer,
  LabelList,
} from 'recharts';
import type { StageProgress } from '../../types/analytics.ts';

interface ProductionProgressChartProps {
  stages: StageProgress[];
  targetStatus: string;
}

const PRIMARY = '#2196F3';
const SUCCESS = '#4CAF50';

export default function ProductionProgressChart({
  stages,
  targetStatus,
}: ProductionProgressChartProps) {
  if (stages.length === 0) {
    return <p className="text-sm text-gray-400">No progress data available.</p>;
  }

  const data = stages.map((s) => ({
    name: s.stage_name,
    current: s.current_count,
    target: s.target_count,
    label:
      s.target_count > 0
        ? `${s.current_count}/${s.target_count}`
        : String(s.current_count),
    pct: s.progress_percentage,
  }));

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-medium text-gray-700">Production Progress</h3>
        {targetStatus !== 'not_set' && (
          <span
            className={`text-xs font-medium px-2 py-0.5 rounded ${
              targetStatus === 'completed'
                ? 'bg-green-100 text-green-700'
                : 'bg-blue-100 text-blue-700'
            }`}
          >
            {targetStatus === 'completed' ? 'Target Completed' : 'Target In Progress'}
          </span>
        )}
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ top: 20, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip
            formatter={(value?: number, name?: string) => [
              value ?? 0,
              name === 'current' ? 'Current' : 'Target',
            ]}
          />
          <Bar dataKey="current" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={index}
                fill={entry.pct >= 100 ? SUCCESS : PRIMARY}
              />
            ))}
            <LabelList dataKey="label" position="top" style={{ fontSize: 11, fill: '#555' }} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
