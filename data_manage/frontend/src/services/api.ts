import axios from 'axios'
import { DataPreview, ExportFormat, FileInfo, StatsResponse } from '@/types'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use((config) => {
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message
    return Promise.reject(new Error(message))
  }
)

export const fileApi = {
  list: async (fileType?: string): Promise<FileInfo[]> => {
    const params = fileType && fileType !== 'all' ? { file_type: fileType } : {}
    const response = await api.get('/files', { params })
    return response.data
  },

  upload: async (file: File, replace = false): Promise<{ message: string }> => {
    const endpoint = replace ? '/upload/replace' : '/upload'
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post(endpoint, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  delete: async (filename: string): Promise<{ message: string }> => {
    const response = await api.delete(`/file/${encodeURIComponent(filename)}`)
    return response.data
  },

  preview: async (filename: string, limit = 100, offset = 0): Promise<DataPreview> => {
    const response = await api.get(`/preview/${encodeURIComponent(filename)}`, {
      params: { limit, offset }
    })
    return response.data
  },

  stats: async (filename: string): Promise<StatsResponse> => {
    const response = await api.get(`/stats/${encodeURIComponent(filename)}`)
    return response.data
  },

  download: async (filename: string): Promise<Blob> => {
    const response = await api.get(`/download/${encodeURIComponent(filename)}`, {
      responseType: 'blob'
    })
    return response.data
  },

  export: async (filename: string, format: ExportFormat): Promise<Blob> => {
    const response = await api.get(`/export/${encodeURIComponent(filename)}`, {
      params: { format },
      responseType: 'blob'
    })
    return response.data
  },

  search: async (query: string): Promise<{ results: string[] }> => {
    const response = await api.get('/search', { params: { query } })
    return response.data
  }
}

export default api
