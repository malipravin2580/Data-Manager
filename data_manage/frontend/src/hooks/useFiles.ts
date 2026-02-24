import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { fileApi } from '@/services/api'
import { FileType } from '@/types'

export function useFiles(fileType: FileType = 'all') {
  return useQuery({
    queryKey: ['files', fileType],
    queryFn: () => fileApi.list(fileType === 'all' ? undefined : fileType),
    staleTime: 30000
  })
}

export function useUploadFile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ file, replace }: { file: File; replace?: boolean }) =>
      fileApi.upload(file, replace),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files'] })
    }
  })
}

export function useDeleteFile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: fileApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files'] })
    }
  })
}

export function usePreview(filename: string | null) {
  return useQuery({
    queryKey: ['preview', filename],
    queryFn: () => fileApi.preview(filename!),
    enabled: !!filename
  })
}

export function useStats(filename: string | null) {
  return useQuery({
    queryKey: ['stats', filename],
    queryFn: () => fileApi.stats(filename!),
    enabled: !!filename
  })
}
