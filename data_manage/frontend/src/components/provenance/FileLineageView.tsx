import { useEffect, useState } from 'react'
import { Dialog } from '@headlessui/react'
import { ArrowUturnLeftIcon, ArrowUturnRightIcon, DocumentIcon } from '@heroicons/react/24/solid'

import { provenanceApi } from '@/services/api'
import { FileLineage } from '@/types/provenance'

interface FileLineageViewProps {
  isOpen: boolean
  filePath: string
  onClose: () => void
}

export default function FileLineageView({ isOpen, filePath, onClose }: FileLineageViewProps) {
  const [lineage, setLineage] = useState<FileLineage | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (isOpen) {
      void loadLineage()
    }
  }, [isOpen, filePath])

  const loadLineage = async () => {
    setIsLoading(true)
    try {
      const data = await provenanceApi.getLineage(filePath)
      setLineage(data)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="bg-white rounded-xl shadow-xl w-full max-w-4xl p-6">
          <Dialog.Title className="text-lg font-semibold">File Lineage</Dialog.Title>
          <p className="text-sm text-gray-500 mt-1">{filePath}</p>

          {isLoading ? (
            <p className="text-center py-8 text-gray-500">Loading lineage...</p>
          ) : !lineage ? (
            <p className="text-center py-8 text-gray-500">No lineage found</p>
          ) : (
            <div className="space-y-6 mt-5 max-h-[70vh] overflow-y-auto pr-1">
              <div className="text-center">
                <div className="inline-flex items-center gap-2 bg-primary-100 text-primary-700 px-4 py-2 rounded-full">
                  <DocumentIcon className="h-5 w-5" />
                  <span className="font-medium break-all">{lineage.current_file}</span>
                </div>
              </div>

              {lineage.ancestors.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-3 flex items-center gap-2">
                    <ArrowUturnLeftIcon className="h-5 w-5 text-gray-500" />
                    Source Files
                  </h4>
                  <div className="space-y-3">
                    {lineage.ancestors.map((ancestor, idx) => (
                      <div key={`${ancestor.file_path}-${idx}`} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                        <ArrowUturnLeftIcon className="h-4 w-4 text-gray-400 mt-1" />
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-sm break-all">{ancestor.file_path}</div>
                          <div className="text-xs text-gray-500 mt-1">
                            Created by {ancestor.created_by || 'Unknown'} via {ancestor.transformation_type}
                          </div>
                          <div className="text-xs text-gray-400">{new Date(ancestor.created_at).toLocaleString()}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {lineage.descendants.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-3 flex items-center gap-2">
                    <ArrowUturnRightIcon className="h-5 w-5 text-gray-500" />
                    Derived Files
                  </h4>
                  <div className="space-y-3">
                    {lineage.descendants.map((descendant, idx) => (
                      <div key={`${descendant.file_path}-${idx}`} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                        <ArrowUturnRightIcon className="h-4 w-4 text-blue-400 mt-1" />
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-sm break-all">{descendant.file_path}</div>
                          <div className="text-xs text-gray-500 mt-1">
                            Created by {descendant.created_by || 'Unknown'} via {descendant.transformation_type}
                          </div>
                          <div className="text-xs text-gray-400">{new Date(descendant.created_at).toLocaleString()}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {lineage.ancestors.length === 0 && lineage.descendants.length === 0 && (
                <p className="text-center py-8 text-gray-500">This file has no recorded sources or derived files.</p>
              )}
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
