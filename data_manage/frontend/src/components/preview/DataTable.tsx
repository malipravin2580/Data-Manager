import { useState } from 'react'
import { ColumnInfo } from '@/types'

interface DataTableProps {
  columns: ColumnInfo[]
  data: Record<string, any>[]
  totalRows: number
}

export default function DataTable({ columns, data, totalRows }: DataTableProps) {
  const [sortColumn, setSortColumn] = useState<string | null>(null)
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc')

  const handleSort = (col: string) => {
    if (sortColumn === col) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(col)
      setSortDirection('asc')
    }
  }

  const sortedData = [...data].sort((a, b) => {
    if (!sortColumn) return 0
    const aVal = a[sortColumn]
    const bVal = b[sortColumn]

    if (aVal == null) return 1
    if (bVal == null) return -1

    const comparison = String(aVal).localeCompare(String(bVal))
    return sortDirection === 'asc' ? comparison : -comparison
  })

  return (
    <div className="overflow-x-auto">
      <div className="mb-2 text-sm text-gray-500">
        Showing {data.length.toLocaleString()} of {totalRows.toLocaleString()} rows
      </div>

      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((col) => (
              <th
                key={col.name}
                onClick={() => handleSort(col.name)}
                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              >
                <div className="flex items-center gap-1">
                  {col.name}
                  {sortColumn === col.name && <span>{sortDirection === 'asc' ? 'up' : 'down'}</span>}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {sortedData.map((row, rowIdx) => (
            <tr key={rowIdx} className="hover:bg-gray-50">
              {columns.map((col) => (
                <td key={col.name} className="px-4 py-2 text-sm text-gray-900 whitespace-nowrap">
                  {row[col.name]?.toString() ?? <span className="text-gray-400">NULL</span>}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
