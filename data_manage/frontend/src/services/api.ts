import axios from 'axios'
import { AuthTokens, FileInfo, Permission, ShareLink, User } from '@/types'
import { ActivityFeedItem, FileAccessLog, FileLineage, PermissionAuditLog } from '@/types/provenance'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

export const api = axios.create({
  baseURL: API_BASE
})

api.interceptors.request.use((config) => {
  const tokens = localStorage.getItem('tokens')
  if (tokens) {
    const { access_token } = JSON.parse(tokens) as AuthTokens
    config.headers.Authorization = `Bearer ${access_token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest?._retry) {
      originalRequest._retry = true
      const tokensRaw = localStorage.getItem('tokens')
      if (tokensRaw) {
        try {
          const { refresh_token } = JSON.parse(tokensRaw) as AuthTokens
          const { data } = await axios.post(`${API_BASE}/auth/refresh`, { refresh_token })
          localStorage.setItem('tokens', JSON.stringify(data))
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`
          return api(originalRequest)
        } catch {
          localStorage.removeItem('tokens')
        }
      }
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: async (username: string, password: string): Promise<AuthTokens> => {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)
    const { data } = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    return data
  },

  register: async (userData: {
    email: string
    username: string
    password: string
    full_name?: string
  }): Promise<User> => {
    const { data } = await api.post('/auth/register', userData)
    return data
  },

  me: async (): Promise<User> => {
    const { data } = await api.get('/auth/me')
    return data
  },

  refresh: async (refresh_token: string): Promise<AuthTokens> => {
    const { data } = await api.post('/auth/refresh', { refresh_token })
    return data
  }
}

export const filesApi = {
  list: async (path = ''): Promise<{ path: string; files: FileInfo[] }> => {
    const { data } = await api.get('/files/list', { params: { path } })
    return data
  },

  upload: async (file: File, path = ''): Promise<{ message: string; path: string }> => {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.post('/files/upload', formData, {
      params: { path },
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return data
  },

  preview: async (filePath: string): Promise<any> => {
    const { data } = await api.get(`/files/preview/${encodeURIComponent(filePath)}`)
    return data
  },

  download: async (filePath: string): Promise<Blob> => {
    const { data } = await api.get(`/files/download/${encodeURIComponent(filePath)}`, {
      responseType: 'blob'
    })
    return data
  },

  delete: async (filePath: string): Promise<{ message: string }> => {
    const { data } = await api.delete(`/files/${encodeURIComponent(filePath)}`)
    return data
  }
}

export const permissionsApi = {
  getFilePermissions: async (filePath: string): Promise<Permission[]> => {
    const { data } = await api.get(`/permissions/file/${encodeURIComponent(filePath)}`)
    return data
  },

  grant: async (request: {
    file_path: string
    user_id?: number
    team_id?: number
    permission: 'view' | 'edit' | 'admin'
  }): Promise<{ message: string }> => {
    const { data } = await api.post('/permissions/grant', request)
    return data
  },

  revoke: async (permissionId: number): Promise<{ message: string }> => {
    const { data } = await api.delete(`/permissions/revoke/${permissionId}`)
    return data
  }
}

export const shareApi = {
  create: async (request: {
    file_path: string
    permission?: string
    expires_days?: number
    password?: string
    max_views?: number
  }): Promise<ShareLink> => {
    const { data } = await api.post('/share/create', request)
    return data
  },

  validate: async (token: string, password?: string): Promise<any> => {
    const { data } = await api.get(`/share/validate/${token}`, {
      params: password ? { password } : undefined
    })
    return data
  },

  getMyLinks: async (): Promise<ShareLink[]> => {
    const { data } = await api.get('/share/my-links')
    return data
  },

  delete: async (shareId: number): Promise<{ message: string }> => {
    const { data } = await api.delete(`/share/${shareId}`)
    return data
  }
}

export const usersApi = {
  list: async (): Promise<User[]> => {
    const { data } = await api.get('/users')
    return data
  }
}

export const provenanceApi = {
  getLineage: async (filePath: string): Promise<FileLineage> => {
    const { data } = await api.get(`/provenance/lineage/${encodeURIComponent(filePath)}`)
    return data
  },

  getAccessHistory: async (filePath: string): Promise<FileAccessLog[]> => {
    const { data } = await api.get(`/provenance/access-history/${encodeURIComponent(filePath)}`)
    return data
  },

  getPermissionAudit: async (filePath: string): Promise<PermissionAuditLog[]> => {
    const { data } = await api.get(`/provenance/permission-audit/${encodeURIComponent(filePath)}`)
    return data
  }
}

export const activityApi = {
  getFeed: async (
    userId?: number,
    filePath?: string
  ): Promise<ActivityFeedItem[]> => {
    const params: Record<string, any> = {}
    if (userId) {
      params.user_id = userId
    }
    if (filePath) {
      params.file_path = filePath
    }

    const { data } = await api.get('/activity/feed', { params })
    return data
  },

  getMyActivity: async (): Promise<ActivityFeedItem[]> => {
    const { data } = await api.get('/activity/my-activity')
    return data
  }
}

export const auditApi = {
  getPermissionAuditFeed: async (
    filePath?: string,
    userId?: number
  ): Promise<PermissionAuditLog[]> => {
    const params: Record<string, any> = {}
    if (filePath) {
      params.file_path = filePath
    }
    if (userId) {
      params.user_id = userId
    }

    const { data } = await api.get('/audit/permissions', { params })
    return data
  }
}
