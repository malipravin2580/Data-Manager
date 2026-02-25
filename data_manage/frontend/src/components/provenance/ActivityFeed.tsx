import { useEffect, useState } from 'react'
import { Dialog } from '@headlessui/react'
import { ArrowDownTrayIcon, ClockIcon, DocumentIcon, EyeIcon, PencilIcon } from '@heroicons/react/24/solid'

import { activityApi } from '@/services/api'
import { ActivityFeedItem } from '@/types/provenance'

interface ActivityFeedProps {
  isOpen: boolean
  userId?: number
  filePath?: string
  onClose: () => void
}

const actionIcons = {
  view: EyeIcon,
  download: ArrowDownTrayIcon,
  edit: PencilIcon,
  upload: DocumentIcon,
  delete: DocumentIcon,
  'view.lineage': EyeIcon
}

export default function ActivityFeed({ isOpen, userId, filePath, onClose }: ActivityFeedProps) {
  const [activities, setActivities] = useState<ActivityFeedItem[]>([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (isOpen) {
      void loadActivityFeed()
    }
  }, [isOpen, userId, filePath])

  const loadActivityFeed = async () => {
    setIsLoading(true)
    try {
      const data = await activityApi.getFeed(userId, filePath)
      setActivities(data)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="bg-white rounded-xl shadow-xl w-full max-w-2xl p-6">
          <Dialog.Title className="text-lg font-semibold">
            {userId ? 'User Activity' : filePath ? 'File Activity' : 'Recent Activity'}
          </Dialog.Title>

          {isLoading ? (
            <p className="text-center py-8 text-gray-500">Loading activity feed...</p>
          ) : activities.length === 0 ? (
            <p className="text-center py-8 text-gray-500">No activity found</p>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto mt-5">
              {activities.map((activity, idx) => {
                const Icon = actionIcons[activity.action as keyof typeof actionIcons] || EyeIcon
                return (
                  <div key={`${activity.id}-${idx}`} className="flex items-start gap-3 p-3 border-b border-gray-100 last:border-b-0">
                    <Icon className="h-5 w-5 text-gray-400 mt-1" />
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm">{activity.user || 'Unknown'}</span>
                        <span className="text-sm">→</span>
                        <span className="text-sm font-medium break-all">{activity.file_path}</span>
                        <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">{activity.action}</span>
                      </div>

                      {activity.details && (
                        <div className="text-xs text-gray-500 mt-1 break-all">{JSON.stringify(activity.details)}</div>
                      )}

                      <div className="text-xs text-gray-400 flex items-center gap-1 mt-1">
                        <ClockIcon className="h-3 w-3" />
                        {new Date(activity.created_at).toLocaleString()}
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
