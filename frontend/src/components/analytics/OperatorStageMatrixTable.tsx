import type { OperatorMatrixRow, StageMetrics } from '../../types/analytics.ts';

interface OperatorStageMatrixTableProps {
  matrix: OperatorMatrixRow[];
}

const STAGES: { key: keyof Omit<OperatorMatrixRow, 'operator_name' | 'station_id'>; label: string }[] = [
  { key: 'cutting', label: 'Cutting' },
  { key: 'stripping', label: 'Stripping' },
  { key: 'crimping', label: 'Crimping' },
  { key: 'testing', label: 'Testing' },
  { key: 'final_inspection', label: 'Final Insp.' },
];

function renderCell(metrics: StageMetrics) {
  if (metrics.scan_count === 0) {
    return <span className="text-gray-300">—</span>;
  }
  return (
    <div className="text-center">
      <span className="text-sm font-medium text-gray-700">{metrics.scan_count}</span>
      <div className="text-xs mt-0.5">
        <span className="text-green-600">{metrics.ok_count}</span>
        {' / '}
        <span className="text-red-600">{metrics.not_ok_count}</span>
      </div>
      <div className="text-xs text-gray-400">{metrics.ok_percentage.toFixed(0)}%</div>
    </div>
  );
}

export default function OperatorStageMatrixTable({
  matrix,
}: OperatorStageMatrixTableProps) {
  if (matrix.length === 0) {
    return <p className="text-sm text-gray-400">No matrix data available.</p>;
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="px-5 py-3 border-b border-gray-200">
        <h3 className="text-base font-medium text-gray-700">Operator &times; Stage Matrix</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wider">
              <th className="px-4 py-2 text-left">Operator</th>
              {STAGES.map((s) => (
                <th key={s.key} className="px-3 py-2 text-center">{s.label}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {matrix.map((row) => (
              <tr key={`${row.operator_name}-${row.station_id}`} className="hover:bg-gray-50">
                <td className="px-4 py-2 font-medium text-gray-700 whitespace-nowrap">
                  {row.operator_name}
                  {row.station_id && (
                    <span className="text-gray-400 font-normal ml-1">({row.station_id})</span>
                  )}
                </td>
                {STAGES.map((s) => (
                  <td key={s.key} className="px-3 py-2">
                    {renderCell(row[s.key])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
