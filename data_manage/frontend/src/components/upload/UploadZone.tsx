import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { CloudArrowUpIcon } from '@heroicons/react/24/outline'
import { useUploadFile } from '@/hooks/useFiles'

interface UploadZoneProps {
  onUploaded?: () => void
}

export default function UploadZone({ onUploaded }: UploadZoneProps) {
  const uploadMutation = useUploadFile()

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      acceptedFiles.forEach((file) => {
        uploadMutation.mutate(
          { file },
          {
            onSuccess: () => {
              onUploaded?.()
            }
          }
        )
      })
    },
    [uploadMutation, onUploaded]
  )

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'application/octet-stream': ['.parquet']
    },
    multiple: true,
    disabled: uploadMutation.isPending
  })

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
        transition-all duration-200
        ${isDragActive && !isDragReject ? 'border-primary-500 bg-primary-50 scale-[1.02]' : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'}
        ${isDragReject ? 'border-red-500 bg-red-50' : ''}
        ${uploadMutation.isPending ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      <input {...getInputProps()} />

      <div className="space-y-4">
        <div className={`mx-auto w-16 h-16 rounded-full flex items-center justify-center ${isDragActive ? 'bg-primary-100' : 'bg-gray-100'}`}>
          <CloudArrowUpIcon className={`h-8 w-8 ${isDragActive ? 'text-primary-600' : 'text-gray-400'}`} />
        </div>

        <div>
          <p className="text-lg font-medium text-gray-900">
            {isDragActive ? 'Drop files here' : 'Drag and drop files here'}
          </p>
          <p className="text-sm text-gray-500 mt-1">or click to select files</p>
        </div>

        <p className="text-xs text-gray-400">Supports CSV, JSON, Excel (.xlsx, .xls), Parquet</p>

        {uploadMutation.isPending && <p className="text-sm text-primary-600 animate-pulse">Uploading...</p>}

        {uploadMutation.error && <p className="text-sm text-red-600">Error: {uploadMutation.error.message}</p>}
      </div>
    </div>
  )
}
