import { format } from 'date-fns'
import { ArrowDownTrayIcon, DocumentIcon, TrashIcon } from '@heroicons/react/24/outline'
import type { MouseEvent } from 'react'
import { useDeleteFile } from '@/hooks/useFiles'
import { fileApi } from '@/services/api'
import { FileInfo } from '@/types'

interface FileListProps {
  files: FileInfo[]
  selectedFile: string | null
  onSelectFile: (filename: string) => void
}

export default function FileList({ files, selectedFile, onSelectFile }: FileListProps) {
  const deleteMutation = useDeleteFile()

  const formatSize = (mb: number) => {
    if (mb < 1) return `${(mb * 1024).toFixed(1)} KB`
    return `${mb.toFixed(2)} MB`
  }

  const getFileIcon = (type: string) => {
    switch (type) {
      case '.csv':
        return 'CSV'
      case '.json':
        return 'JSON'
      case '.xlsx':
      case '.xls':
        return 'XLS'
      case '.parquet':
        return 'PQT'
      default:
        return 'FILE'
    }
  }

  const handleDelete = (e: MouseEvent, filename: string) => {
    e.stopPropagation()
    if (window.confirm(`Delete "${filename}"?`)) {
      deleteMutation.mutate(filename)
    }
  }

  const handleDownload = async (e: MouseEvent, filename: string) => {
    e.stopPropagation()
    const blob = await fileApi.download(filename)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    window.URL.revokeObjectURL(url)
  }

  if (files.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <DocumentIcon className="h-12 w-12 mx-auto text-gray-300" />
        <p className="mt-2">No files found</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File Name</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Size</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rows</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Modified</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {files.map((file) => (
            <tr
              key={file.name}
              onClick={() => onSelectFile(file.name)}
              className={`cursor-pointer transition-colors ${selectedFile === file.name ? 'bg-primary-50' : 'hover:bg-gray-50'}`}
            >
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <span className="text-xs mr-2 px-1.5 py-0.5 rounded bg-gray-100 text-gray-700">
                    {getFileIcon(file.type)}
                  </span>
                  <span className="text-sm font-medium text-gray-900">{file.name}</span>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatSize(file.size_mb)}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{file.rows?.toLocaleString() ?? 'N/A'}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {file.modified ? format(new Date(file.modified), 'MMM dd, yyyy HH:mm') : 'N/A'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  onClick={(e) => handleDelete(e, file.name)}
                  className="text-red-600 hover:text-red-900 p-1"
                  title="Delete"
                >
                  <TrashIcon className="h-5 w-5" />
                </button>
                <button
                  onClick={(e) => {
                    void handleDownload(e, file.name)
                  }}
                  className="text-gray-600 hover:text-gray-900 p-1 ml-2"
                  title="Download"
                >
                  <ArrowDownTrayIcon className="h-5 w-5" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
