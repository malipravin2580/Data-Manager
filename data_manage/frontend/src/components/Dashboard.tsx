import { useState } from 'react'

import { useAuth } from '@/contexts/AuthContext'
import FileList from '@/components/files/FileList'
import Header from '@/components/layout/Header'
import Sidebar from '@/components/layout/Sidebar'
import PermissionManager from '@/components/permissions/PermissionManager'
import DataPreview from '@/components/preview/DataPreview'
import AccessHistory from '@/components/provenance/AccessHistory'
import ActivityFeed from '@/components/provenance/ActivityFeed'
import FileLineageView from '@/components/provenance/FileLineageView'
import PermissionAudit from '@/components/provenance/PermissionAudit'
import ShareLinkDialog from '@/components/share/ShareLinkDialog'
import UploadZone from '@/components/upload/UploadZone'
import { useFiles, usePreview } from '@/hooks/useFiles'
import { FileType } from '@/types'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const [selectedType, setSelectedType] = useState<FileType>('all')
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [showShareDialog, setShowShareDialog] = useState(false)
  const [showPermissionDialog, setShowPermissionDialog] = useState(false)
  const [showLineageView, setShowLineageView] = useState(false)
  const [showAccessHistory, setShowAccessHistory] = useState(false)
  const [showPermissionAudit, setShowPermissionAudit] = useState(false)
  const [showActivityFeed, setShowActivityFeed] = useState(false)

  const { data: files = [], isLoading, refetch } = useFiles(selectedType)
  const { data: preview } = usePreview(selectedFile)

  return (
    <div className="min-h-screen bg-gray-100">
      <Header user={user} onLogout={logout} />

      <div className="flex">
        <Sidebar selectedType={selectedType} onSelectType={setSelectedType} />

        <main className="flex-1 p-6 space-y-6">
          <UploadZone onUploaded={() => void refetch()} />

          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">
                {selectedType === 'all' ? 'All Files' : `${selectedType.toUpperCase()} Files`}
              </h2>

              {selectedFile && (
                <div className="flex gap-2">
                  <button onClick={() => setShowShareDialog(true)} className="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded-lg">Share</button>
                  <button onClick={() => setShowPermissionDialog(true)} className="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded-lg">Permissions</button>
                  <button onClick={() => setShowLineageView(true)} className="text-sm bg-blue-100 hover:bg-blue-200 px-3 py-1 rounded-lg">Lineage</button>
                  <button onClick={() => setShowAccessHistory(true)} className="text-sm bg-green-100 hover:bg-green-200 px-3 py-1 rounded-lg">Access History</button>
                  <button onClick={() => setShowPermissionAudit(true)} className="text-sm bg-amber-100 hover:bg-amber-200 px-3 py-1 rounded-lg">Permission Audit</button>
                  <button onClick={() => setShowActivityFeed(true)} className="text-sm bg-indigo-100 hover:bg-indigo-200 px-3 py-1 rounded-lg">Activity</button>
                </div>
              )}
            </div>

            {isLoading ? (
              <div className="text-center py-8 text-gray-500">Loading...</div>
            ) : (
              <FileList files={files as any} selectedFile={selectedFile} onSelectFile={setSelectedFile} />
            )}
          </div>
        </main>

        <aside className="w-2/5 border-l border-gray-200 p-6 overflow-auto max-h-[calc(100vh-4rem)]">
          {selectedFile && preview ? (
            <DataPreview data={preview as any} filename={selectedFile} />
          ) : (
            <div className="text-center py-12 text-gray-500">Select a file to preview</div>
          )}
        </aside>
      </div>

      {selectedFile && (
        <>
          <ShareLinkDialog
            isOpen={showShareDialog}
            onClose={() => setShowShareDialog(false)}
            filePath={selectedFile}
            onCreated={() => setShowShareDialog(false)}
          />
          <PermissionManager
            isOpen={showPermissionDialog}
            onClose={() => setShowPermissionDialog(false)}
            filePath={selectedFile}
          />
          <FileLineageView
            isOpen={showLineageView}
            onClose={() => setShowLineageView(false)}
            filePath={selectedFile}
          />
          <AccessHistory
            isOpen={showAccessHistory}
            onClose={() => setShowAccessHistory(false)}
            filePath={selectedFile}
          />
          <PermissionAudit
            isOpen={showPermissionAudit}
            onClose={() => setShowPermissionAudit(false)}
            filePath={selectedFile}
          />
          <ActivityFeed
            isOpen={showActivityFeed}
            onClose={() => setShowActivityFeed(false)}
            filePath={selectedFile}
          />
        </>
      )}
    </div>
  )
}
