export interface FileInfo {
  name: string
  type: string
  size_mb: number
  rows: number | null
  modified: string
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

export interface StatsResponse {
  stats: Record<string, Record<string, number>>
}

export type FileType = 'csv' | 'json' | 'xlsx' | 'parquet' | 'all'
export type ExportFormat = 'csv' | 'json' | 'parquet' | 'xlsx'
