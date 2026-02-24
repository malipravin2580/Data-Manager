import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import FileList from '@/components/files/FileList'
import Header from '@/components/layout/Header'
import Sidebar from '@/components/layout/Sidebar'
import DataPreview from '@/components/preview/DataPreview'
import UploadZone from '@/components/upload/UploadZone'
import { useFiles, usePreview } from '@/hooks/useFiles'
import { FileType } from '@/types'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1
    }
  }
})

function AppContent() {
  const [selectedType, setSelectedType] = useState<FileType>('all')
  const [selectedFile, setSelectedFile] = useState<string | null>(null)

  const { data: files = [], isLoading } = useFiles(selectedType)
  const { data: preview } = usePreview(selectedFile)

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />

      <div className="flex">
        <Sidebar selectedType={selectedType} onSelectType={setSelectedType} />

        <main className="flex-1 p-6 space-y-6">
          <UploadZone />

          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              {selectedType === 'all' ? 'All Files' : `${selectedType.toUpperCase()} Files`}
            </h2>

            {isLoading ? (
              <div className="text-center py-8 text-gray-500">Loading...</div>
            ) : (
              <FileList files={files} selectedFile={selectedFile} onSelectFile={setSelectedFile} />
            )}
          </div>
        </main>

        <aside className="w-2/5 border-l border-gray-200 p-6 overflow-auto max-h-[calc(100vh-4rem)]">
          {selectedFile && preview ? (
            <DataPreview data={preview} filename={selectedFile} />
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p>Select a file to preview</p>
            </div>
          )}
        </aside>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  )
}
