import { useEffect, useState } from 'react'
import { Dialog } from '@headlessui/react'
import { ArrowDownTrayIcon, ClockIcon, EyeIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/solid'

import { provenanceApi } from '@/services/api'
import { FileAccessLog } from '@/types/provenance'

interface AccessHistoryProps {
  isOpen: boolean
  filePath: string
  onClose: () => void
}

const actionIcons = {
  view: EyeIcon,
  download: ArrowDownTrayIcon,
  edit: PencilIcon,
  delete: TrashIcon,
  upload: ArrowDownTrayIcon,
  'view.lineage': EyeIcon
}

export default function AccessHistory({ isOpen, filePath, onClose }: AccessHistoryProps) {
  const [logs, setLogs] = useState<FileAccessLog[]>([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (isOpen) {
      void loadAccessHistory()
    }
  }, [isOpen, filePath])

  const loadAccessHistory = async () => {
    setIsLoading(true)
    try {
      const data = await provenanceApi.getAccessHistory(filePath)
      setLogs(data)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="bg-white rounded-xl shadow-xl w-full max-w-2xl p-6">
          <Dialog.Title className="text-lg font-semibold">Access History</Dialog.Title>
          <p className="text-sm text-gray-500 mt-1">{filePath}</p>

          {isLoading ? (
            <p className="text-center py-8 text-gray-500">Loading access history...</p>
          ) : logs.length === 0 ? (
            <p className="text-center py-8 text-gray-500">No access records found</p>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto mt-5">
              {logs.map((log, idx) => {
                const Icon = actionIcons[log.action as keyof typeof actionIcons] || EyeIcon
                return (
                  <div key={`${log.action}-${log.created_at}-${idx}`} className="flex items-start gap-3 p-3 border-b border-gray-100 last:border-b-0">
                    <Icon className="h-5 w-5 text-gray-400 mt-1" />
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm">{log.user || 'Unknown'}</span>
                        <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">{log.action}</span>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">{log.ip_address || 'Unknown IP'}</div>
                      <div className="text-xs text-gray-400 flex items-center gap-1 mt-1">
                        <ClockIcon className="h-3 w-3" />
                        {new Date(log.created_at).toLocaleString()}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          <div className="mt-5 flex justify-end">
            <button onClick={onClose} className="border border-gray-300 py-2 px-4 rounded-lg">Close</button>
          </div>
        </Dialog.Panel>
      </div>
    </Dialog>
  )
}
