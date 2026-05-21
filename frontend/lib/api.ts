/**
 * API client for Magnific backend
 */

const API_BASE = '/api'

interface ApiKeyConfig {
  keys: string[]
  webhook_url?: string
  webhook_secret?: string
}

interface DashboardStats {
  total_tasks: number
  completed_tasks: number
  failed_tasks: number
  pending_tasks: number
  tasks_today: number
  tasks_this_week: number
  gallery_item_count: number
  quota_by_service: Array<{
    service: string
    used: number
    limit: number
    percentage: number
  }>
  recent_tasks: any[]
  key_stats: Array<{
    key_masked: string
    tasks_created: number
    quota_remaining: number
  }>
}

// Config API
export async function saveApiKeys(config: ApiKeyConfig) {
  const response = await fetch(`${API_BASE}/config/keys`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  })
  if (!response.ok) throw new Error('Failed to save API keys')
  return response.json()
}

export async function getApiKeys() {
  const response = await fetch(`${API_BASE}/config/keys`)
  if (!response.ok) throw new Error('Failed to fetch API keys')
  return response.json()
}

export async function verifyApiKey(api_key: string) {
  const response = await fetch(`${API_BASE}/config/verify-key`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ api_key })
  })
  if (!response.ok) throw new Error('Failed to verify API key')
  return response.json()
}

// Dashboard API
export async function getDashboardStats(): Promise<DashboardStats> {
  const response = await fetch(`${API_BASE}/dashboard/stats`)
  if (!response.ok) throw new Error('Failed to fetch dashboard stats')
  return response.json()
}

// Video API
export async function generateVideo(data: {
  prompt: string
  image_url?: string
  video_url?: string
  duration?: number
  mode?: string
  model?: string
  negative_prompt?: string
  cfg_scale?: number
  aspect_ratio?: string
  generate_audio?: boolean
  character_orientation?: 'video' | 'image'
  start_image_url?: string
  end_image_url?: string
  multi_shot?: boolean
  shot_type?: string
  multi_prompt?: string
}) {
  const response = await fetch(`${API_BASE}/video/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to generate video')
  }
  return response.json()
}

// Image API
export async function generateImage(data: {
  prompt: string
  model?: string
  width?: number
  height?: number
  num_images?: number
}) {
  const response = await fetch(`${API_BASE}/image/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to generate image')
  }
  return response.json()
}

// Image Editing API
export async function upscaleImage(image_url: string) {
  const response = await fetch(`${API_BASE}/editing/upscale`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_url, operation: 'upscale' })
  })
  if (!response.ok) throw new Error('Failed to upscale image')
  return response.json()
}

export async function removeBackground(image_url: string) {
  const response = await fetch(`${API_BASE}/editing/remove-background`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_url, operation: 'remove-background' })
  })
  if (!response.ok) throw new Error('Failed to remove background')
  return response.json()
}

export async function relightImage(image_url: string) {
  const response = await fetch(`${API_BASE}/editing/relight`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_url, operation: 'relight' })
  })
  if (!response.ok) throw new Error('Failed to relight image')
  return response.json()
}

// Audio API
export async function generateAudio(data: {
  prompt: string
  type: string
  duration?: number
  voice_id?: string
  stability?: number
  similarity_boost?: number
  speed?: number
  use_speaker_boost?: boolean
}) {
  const response = await fetch(`${API_BASE}/audio/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  if (!response.ok) throw new Error('Failed to generate audio')
  return response.json()
}

// Gallery API
export async function getGallery(params?: {
  type?: string
  favorited?: boolean
  limit?: number
  offset?: number
}) {
  const query = new URLSearchParams()
  if (params?.type) query.append('type', params.type)
  if (params?.favorited !== undefined) query.append('favorited', String(params.favorited))
  if (params?.limit) query.append('limit', String(params.limit))
  if (params?.offset) query.append('offset', String(params.offset))
  
  const response = await fetch(`${API_BASE}/gallery?${query}`)
  if (!response.ok) throw new Error('Failed to fetch gallery')
  return response.json()
}

export async function toggleFavorite(itemId: number) {
  const response = await fetch(`${API_BASE}/gallery/${itemId}/favorite`, {
    method: 'POST'
  })
  if (!response.ok) throw new Error('Failed to toggle favorite')
  return response.json()
}

export async function deleteGalleryItem(itemId: number) {
  const response = await fetch(`${API_BASE}/gallery/${itemId}`, {
    method: 'DELETE'
  })
  if (!response.ok) throw new Error('Failed to delete item')
  return response.json()
}

// Tasks API
export async function getTasks(params?: {
  status?: string
  type?: string
  limit?: number
  offset?: number
}) {
  const query = new URLSearchParams()
  if (params?.status) query.append('status', params.status)
  if (params?.type) query.append('type', params.type)
  if (params?.limit) query.append('limit', String(params.limit))
  if (params?.offset) query.append('offset', String(params.offset))
  
  const response = await fetch(`${API_BASE}/tasks?${query}`)
  if (!response.ok) throw new Error('Failed to fetch tasks')
  return response.json()
}

export async function getTask(taskId: string) {
  const response = await fetch(`${API_BASE}/tasks/${taskId}`)
  if (!response.ok) throw new Error('Failed to fetch task')
  return response.json()
}

export async function checkTaskStatus(taskId: string) {
  const response = await fetch(`${API_BASE}/tasks/${taskId}/check-status`, {
    method: 'POST'
  })
  if (!response.ok) throw new Error('Failed to check task status')
  return response.json()
}

// Lip Sync API
export async function generateLipSync(data: {
  model: string
  audio_url: string
  video_url?: string
  image_url?: string
  resolution?: string
  seed?: number
  guidance_scale?: number
}) {
  const response = await fetch(`${API_BASE}/lip-sync/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to generate lip-sync')
  }
  return response.json()
}

// Logs API
export async function getLogs(params?: {
  level?: string
  search?: string
  limit?: number
  offset?: number
}) {
  const query = new URLSearchParams()
  if (params?.level) query.append('level', params.level)
  if (params?.search) query.append('search', params.search)
  if (params?.limit) query.append('limit', String(params.limit))
  if (params?.offset) query.append('offset', String(params.offset))
  
  const response = await fetch(`${API_BASE}/logs?${query}`)
  if (!response.ok) throw new Error('Failed to fetch logs')
  return response.json()
}
