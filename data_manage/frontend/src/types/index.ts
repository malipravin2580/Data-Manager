export interface User {
  id: number
  email: string
  username: string
  full_name: string | null
  role: 'admin' | 'editor' | 'viewer'
  is_active: boolean
  created_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface FileInfo {
  name: string
  type: 'file' | 'folder'
  size: number | null
  modified: number
  path: string
}

export interface ColumnInfo {
  name: string
  dtype: string
  null_count: number
  unique_count: number
}

export interface DataPreview {
  columns: ColumnInfo[]
  data: Record<string, any>[]
  total_rows: number
  metadata: Record<string, any>
}

export interface Permission {
  id: number
  file_path: string
  user_id: number | null
  team_id: number | null
  permission: 'view' | 'edit' | 'admin'
}

export interface ShareLink {
  id: number
  token: string
  file_path: string
  permission: string
  expires_at: string
  max_views: number | null
  view_count: number
  url: string
}

export interface Activity {
  id: number
  user_id: number
  action: string
  resource_type: string
  resource_id: string
  details: string | null
  created_at: string
}

export type FileType = 'csv' | 'json' | 'xlsx' | 'parquet' | 'all'
export type ExportFormat = 'csv' | 'json' | 'parquet' | 'xlsx'
