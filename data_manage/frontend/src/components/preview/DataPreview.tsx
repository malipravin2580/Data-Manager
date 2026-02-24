import { useState } from 'react'
import { Tab } from '@headlessui/react'
import {
  ArrowDownTrayIcon,
  ChartBarIcon,
  InformationCircleIcon,
  TableCellsIcon
} from '@heroicons/react/24/outline'
import { useStats } from '@/hooks/useFiles'
import { fileApi } from '@/services/api'
import { DataPreview as DataPreviewType, ExportFormat } from '@/types'
import ColumnStats from './ColumnStats'
import DataTable from './DataTable'
import MetadataPanel from './MetadataPanel'

interface DataPreviewProps {
  data: DataPreviewType
  filename: string
}

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

export default function DataPreview({ data, filename }: DataPreviewProps) {
  const [exportFormat, setExportFormat] = useState<ExportFormat>('csv')
  const { data: stats } = useStats(filename)

  const handleExport = async () => {
    const blob = await fileApi.export(filename, exportFormat)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${filename.split('.')[0]}.${exportFormat}`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <TableCellsIcon className="h-5 w-5 text-gray-500" />
          {filename}
        </h2>

        <div className="flex items-center gap-3">
          <select
            value={exportFormat}
            onChange={(e) => setExportFormat(e.target.value as ExportFormat)}
            className="border border-gray-300 rounded-lg px-3 py-1 text-sm"
          >
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
            <option value="parquet">Parquet</option>
            <option value="xlsx">Excel</option>
          </select>

          <button
            onClick={() => {
              void handleExport()
            }}
            className="flex items-center gap-2 bg-primary-600 text-white px-4 py-1.5 rounded-lg hover:bg-primary-700 transition"
          >
            <ArrowDownTrayIcon className="h-4 w-4" />
            Export
          </button>
        </div>
      </div>

      <Tab.Group>
        <Tab.List className="flex border-b border-gray-200 px-6">
          <Tab
            className={({ selected }) =>
              classNames(
                'px-4 py-3 text-sm font-medium border-b-2 -mb-px focus:outline-none',
                selected
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              )
            }
          >
            <div className="flex items-center gap-2">
              <TableCellsIcon className="h-4 w-4" />
              Data
            </div>
          </Tab>
          <Tab
            className={({ selected }) =>
              classNames(
                'px-4 py-3 text-sm font-medium border-b-2 -mb-px focus:outline-none',
                selected
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              )
            }
          >
            <div className="flex items-center gap-2">
              <ChartBarIcon className="h-4 w-4" />
              Statistics
            </div>
          </Tab>
          <Tab
            className={({ selected }) =>
              classNames(
                'px-4 py-3 text-sm font-medium border-b-2 -mb-px focus:outline-none',
                selected
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              )
            }
          >
            <div className="flex items-center gap-2">
              <InformationCircleIcon className="h-4 w-4" />
              Metadata
            </div>
          </Tab>
        </Tab.List>

        <Tab.Panels className="p-6">
          <Tab.Panel>
            <DataTable columns={data.columns} data={data.data} totalRows={data.total_rows} />
          </Tab.Panel>
          <Tab.Panel>
            {stats ? (
              <ColumnStats stats={stats.stats} columns={data.columns} />
            ) : (
              <p className="text-gray-500">Loading statistics...</p>
            )}
          </Tab.Panel>
          <Tab.Panel>
            <MetadataPanel metadata={data.metadata} />
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </div>
  )
}
