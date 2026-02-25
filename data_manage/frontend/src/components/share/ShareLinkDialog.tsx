import { useState } from 'react'
import { Dialog } from '@headlessui/react'
import { CheckIcon, ClipboardIcon, LinkIcon } from '@heroicons/react/24/solid'

import { shareApi } from '@/services/api'
import { ShareLink } from '@/types'

interface ShareLinkDialogProps {
  isOpen: boolean
  onClose: () => void
  filePath: string
  onCreated: (link: ShareLink) => void
}

export default function ShareLinkDialog({ isOpen, onClose, filePath, onCreated }: ShareLinkDialogProps) {
  const [formData, setFormData] = useState({ permission: 'view', expires_days: 7, password: '', max_views: '' })
  const [createdLink, setCreatedLink] = useState<ShareLink | null>(null)
  const [copied, setCopied] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    try {
      const link = await shareApi.create({
        file_path: filePath,
        permission: formData.permission,
        expires_days: formData.expires_days,
        password: formData.password || undefined,
        max_views: formData.max_views ? parseInt(formData.max_views, 10) : undefined
      })
      setCreatedLink(link)
      onCreated(link)
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = async () => {
    if (!createdLink) {
      return
    }
    await navigator.clipboard.writeText(createdLink.url)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
          <Dialog.Title className="text-lg font-semibold flex items-center gap-2">
            <LinkIcon className="h-5 w-5 text-primary-500" /> Share File
          </Dialog.Title>

          {createdLink ? (
            <div className="mt-4 space-y-4">
              <div className="bg-gray-50 p-3 rounded-lg flex items-center gap-2">
                <input className="flex-1 bg-transparent text-sm" readOnly value={createdLink.url} />
                <button onClick={() => void copyToClipboard()} className="p-2 hover:bg-gray-200 rounded-lg">
                  {copied ? <CheckIcon className="h-5 w-5 text-green-500" /> : <ClipboardIcon className="h-5 w-5 text-gray-500" />}
                </button>
              </div>
              <button onClick={onClose} className="w-full bg-primary-600 text-white py-2 rounded-lg">Done</button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="mt-4 space-y-3">
              <select
                value={formData.permission}
                onChange={(e) => setFormData({ ...formData, permission: e.target.value })}
                className="w-full border border-gray-300 rounded-lg py-2 px-3"
              >
                <option value="view">View only</option>
                <option value="edit">View & Edit</option>
              </select>
              <input
                type="number"
                min={1}
                value={formData.expires_days}
                onChange={(e) => setFormData({ ...formData, expires_days: Number(e.target.value) || 7 })}
                className="w-full border border-gray-300 rounded-lg py-2 px-3"
                placeholder="Expires days"
              />
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full border border-gray-300 rounded-lg py-2 px-3"
                placeholder="Password (optional)"
              />
              <input
                type="number"
                min={1}
                value={formData.max_views}
                onChange={(e) => setFormData({ ...formData, max_views: e.target.value })}
                className="w-full border border-gray-300 rounded-lg py-2 px-3"
                placeholder="Max views (optional)"
              />
              <div className="flex gap-2">
                <button type="button" onClick={onClose} className="flex-1 border border-gray-300 py-2 rounded-lg">Cancel</button>
                <button type="submit" disabled={isLoading} className="flex-1 bg-primary-600 text-white py-2 rounded-lg">{isLoading ? 'Creating...' : 'Create Link'}</button>
              </div>
            </form>
          )}
        </Dialog.Panel>
      </div>
    </Dialog>
  )
}
