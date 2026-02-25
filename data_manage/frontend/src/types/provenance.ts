export interface FileLineage {
  current_file: string
  ancestors: Array<{
    file_path: string
    transformation_type: string
    created_at: string
    created_by: string | null
  }>
  descendants: Array<{
    file_path: string
    transformation_type: string
    created_at: string
    created_by: string | null
  }>
}

export interface FileAccessLog {
  user: string | null
  action: string
  ip_address: string | null
  created_at: string
  details: Record<string, any> | null
}

export interface PermissionAuditLog {
  action: string
  target_user: string | null
  target_team_id: number | null
  old_permission: string | null
  new_permission: string | null
  performed_by: string | null
  created_at: string
}

export interface ActivityFeedItem {
  id: number
  file_path: string
  user: string | null
  action: string
  details: Record<string, any> | null
  ip_address: string | null
  created_at: string
}
