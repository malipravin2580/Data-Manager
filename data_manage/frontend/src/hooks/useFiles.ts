import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { filesApi } from '@/services/api'
import { FileType } from '@/types'

export function useFiles(fileType: FileType = 'all') {
  return useQuery({
    queryKey: ['files', fileType],
    queryFn: async () => {
      const res = await filesApi.list()
      if (fileType === 'all') {
        return res.files
      }
      return res.files.filter((f) => f.path.toLowerCase().endsWith(`.${fileType}`))
    },
    staleTime: 30000
  })
}

export function useUploadFile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ file, path }: { file: File; path?: string }) =>
      filesApi.upload(file, path ?? ''),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files'] })
    }
  })
}

export function useDeleteFile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: filesApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files'] })
    }
  })
}

export function usePreview(filename: string | null) {
  return useQuery({
    queryKey: ['preview', filename],
    queryFn: () => filesApi.preview(filename!),
    enabled: !!filename
  })
}

export function useStats(filename: string | null) {
  return useQuery({
    queryKey: ['stats', filename],
    queryFn: async () => ({ stats: {} }),
    enabled: false
  })
}
