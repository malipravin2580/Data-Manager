import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { ColumnInfo } from '@/types'

interface ColumnStatsProps {
  stats: Record<string, Record<string, number>>
  columns: ColumnInfo[]
}

export default function ColumnStats({ stats, columns }: ColumnStatsProps) {
  const numericColumns = columns.filter(
    (col) => stats[col.name] && !['object', 'string', 'bool'].includes(col.dtype)
  )

  return (
    <div className="space-y-6">
      {numericColumns.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No numeric columns found for statistics</p>
      ) : (
        numericColumns.map((col) => {
          const colStats = stats[col.name]
          const chartData = [
            { name: 'Min', value: colStats.min },
            { name: 'Q1', value: colStats['25%'] },
            { name: 'Median', value: colStats['50%'] },
            { name: 'Q3', value: colStats['75%'] },
            { name: 'Max', value: colStats.max }
          ]

          return (
            <div key={col.name} className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-4">{col.name}</h3>

              <div className="grid grid-cols-5 gap-4 mb-4">
                <StatItem label="Mean" value={colStats.mean?.toFixed(2)} />
                <StatItem label="Std" value={colStats.std?.toFixed(2)} />
                <StatItem label="Min" value={colStats.min?.toFixed(2)} />
                <StatItem label="Max" value={colStats.max?.toFixed(2)} />
                <StatItem label="Count" value={colStats.count?.toLocaleString()} />
              </div>

              <div className="h-40">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )
        })
      )}
    </div>
  )
}

function StatItem({ label, value }: { label: string; value: string | undefined }) {
  return (
    <div className="text-center">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="text-lg font-medium text-gray-900">{value ?? 'N/A'}</div>
    </div>
  )
}
