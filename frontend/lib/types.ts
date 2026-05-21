/**
 * TypeScript type definitions
 */

export interface Task {
  id: number
  task_id: string
  service: string
  type: string
  status: string
  result_url?: string
  thumbnail_url?: string
  error_message?: string
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface GalleryItem {
  id: number
  task_id: string
  type: string
  title?: string
  prompt?: string
  result_url: string
  thumbnail_url?: string
  favorited: boolean
  tags?: string
  created_at: string
}

export interface LogEntry {
  timestamp: string
  level: string
  message: string
  task_id?: string
  service?: string
  error?: string
}

export interface QuotaByService {
  service: string
  used: number
  limit: number
  percentage: number
}

export interface KeyStats {
  key_masked: string
  tasks_created: number
  quota_remaining: number
}
