import axios from 'axios'
import type { Project, Video, Clip, Subtitle, ProcessingTemplate } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Projects
export const projectsApi = {
  create: (data: Partial<Project>) => 
    api.post<Project>('/api/projects/', data),
  
  getAll: (skip = 0, limit = 100) => 
    api.get<Project[]>('/api/projects/', { params: { skip, limit } }),
  
  getById: (id: number) => 
    api.get<Project>(`/api/projects/${id}`),
  
  delete: (id: number) => 
    api.delete(`/api/projects/${id}`),
}

// Videos
export const videosApi = {
  upload: (projectId: number, file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData()
    formData.append('project_id', projectId.toString())
    formData.append('file', file)
    
    return api.post<Video>('/api/videos/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(percentage)
        }
      },
    })
  },

  batchUpload: (projectId: number, files: File[], onProgress?: (progress: number) => void) => {
    const formData = new FormData()
    formData.append('project_id', projectId.toString())
    files.forEach(file => formData.append('files', file))
    
    return api.post<BatchUploadResponse>('/api/videos/batch-upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(percentage)
        }
      },
    })
  },
  
  getByProjectId: (projectId: number) => 
    api.get<Video[]>(`/api/videos/project/${projectId}`),
  
  getById: (id: number) => 
    api.get<Video>(`/api/videos/${id}`),
  
  delete: (id: number) => 
    api.delete(`/api/videos/${id}`),
}

// Clips
export const clipsApi = {
  create: (data: Partial<Clip>) => 
    api.post<Clip>('/api/clips/', data),
  
  getByProjectId: (projectId: number) => 
    api.get<Clip[]>(`/api/clips/project/${projectId}`),
  
  getByVideoId: (videoId: number) => 
    api.get<Clip[]>(`/api/clips/video/${videoId}`),
  
  getById: (id: number) => 
    api.get<Clip>(`/api/clips/${id}`),
  
  update: (id: number, data: Partial<Clip>) => 
    api.put<Clip>(`/api/clips/${id}`, data),
  
  delete: (id: number) => 
    api.delete(`/api/clips/${id}`),
}

// Subtitles
export const subtitlesApi = {
  create: (data: Partial<Subtitle>) => 
    api.post<Subtitle>('/api/subtitles/', data),
  
  getByClipId: (clipId: number) => 
    api.get<Subtitle[]>(`/api/subtitles/clip/${clipId}`),
  
  update: (id: number, data: Partial<Subtitle>) => 
    api.put<Subtitle>(`/api/subtitles/${id}`, data),
  
  delete: (id: number) => 
    api.delete(`/api/subtitles/${id}`),
}

// Processing (Celery tasks)
export interface JobResponse {
  job_id: string
  status: string
  message: string
}

export interface JobStatus {
  status: 'PENDING' | 'PROGRESS' | 'SUCCESS' | 'FAILURE'
  progress?: {
    current: number
    total: number
    status: string
  }
  result?: any
  error?: any
}

export interface BatchJobResponse {
  jobs: Array<{
    job_id?: string
    video_id?: number
    url?: string
    status: string
    message?: string
  }>
  message: string
}

export interface BatchUploadResponse {
  uploaded: number[]
  failed: string[]
  message: string
}

export const processingApi = {
  // YouTube download
  downloadYouTube: (projectId: number, youtubeUrl: string) =>
    api.post<JobResponse>('/api/processing/download-youtube', {
      project_id: projectId,
      youtube_url: youtubeUrl,
    }),

  // Transcription
  transcribe: (videoId: number, language?: string) =>
    api.post<JobResponse>('/api/processing/transcribe', {
      video_id: videoId,
      language,
    }),

  // Scene detection
  detectScenes: (videoId: number, threshold?: number) =>
    api.post<JobResponse>('/api/processing/detect-scenes', {
      video_id: videoId,
      threshold: threshold || 27.0,
    }),

  // Viral detection only (without export)
  detectViral: (videoId: number, topN?: number) =>
    api.post<JobResponse>('/api/processing/detect-viral', {
      video_id: videoId,
      top_n: topN || 5,
    }),

  // Detect and export viral clips with subtitles
  detectAndExport: (
    videoId: number,
    options?: {
      topN?: number
      targetPlatform?: string
      aspectRatio?: string
      burnSubtitles?: boolean
      subtitleStyle?: string
      minDuration?: number
      maxDuration?: number
      titleTone?: string
      customPrompt?: string
      language?: string
    }
  ) =>
    api.post<JobResponse>('/api/processing/detect-and-export', {
      video_id: videoId,
      top_n: options?.topN || 5,
      target_platform: options?.targetPlatform || 'shorts',
      aspect_ratio: options?.aspectRatio || '9:16',
      burn_subtitles: options?.burnSubtitles ?? true,
      subtitle_style: options?.subtitleStyle || 'viral_white',
      min_duration: options?.minDuration || 30,
      max_duration: options?.maxDuration || 60,
      title_tone: options?.titleTone || 'engaging',
      custom_prompt: options?.customPrompt || '',
      language: options?.language || 'en',
    }),

  // Export single clip
  exportClip: (clipId: number, targetPlatform?: string, aspectRatio?: string) =>
    api.post<JobResponse>('/api/processing/export-clip', {
      clip_id: clipId,
      target_platform: targetPlatform || 'shorts',
      aspect_ratio: aspectRatio || '9:16',
    }),

  // Export all clips for a video
  exportAllClips: (videoId: number, targetPlatform?: string, aspectRatio?: string) =>
    api.post<JobResponse>('/api/processing/export-all-clips', {
      video_id: videoId,
      target_platform: targetPlatform || 'shorts',
      aspect_ratio: aspectRatio || '9:16',
    }),

  // Get job status
  getJobStatus: (jobId: string) =>
    api.get<JobStatus>(`/api/jobs/status/${jobId}`),

  // Batch operations
  batchDownloadYouTube: (projectId: number, youtubeUrls: string[]) =>
    api.post<BatchJobResponse>('/api/processing/batch-download-youtube', {
      project_id: projectId,
      youtube_urls: youtubeUrls,
    }),

  batchProcess: (
    videoIds: number[],
    options?: {
      topN?: number
      targetPlatform?: string
      aspectRatio?: string
      burnSubtitles?: boolean
      subtitleStyle?: string
      minDuration?: number
      maxDuration?: number
    }
  ) =>
    api.post<BatchJobResponse>('/api/processing/batch-process', {
      video_ids: videoIds,
      top_n: options?.topN || 5,
      target_platform: options?.targetPlatform || 'shorts',
      aspect_ratio: options?.aspectRatio || '9:16',
      burn_subtitles: options?.burnSubtitles ?? true,
      subtitle_style: options?.subtitleStyle || 'viral_white',
      min_duration: options?.minDuration || 30,
      max_duration: options?.maxDuration || 60,
    }),
}

// Storage
export interface StorageStats {
  total_size_bytes: number
  total_size_formatted: string
  uploads_size: number
  temp_size: number
  exports_size: number
  videos_count: number
  clips_count: number
  projects_count: number
}

export interface CleanupResult {
  files_deleted: number
  space_freed_bytes: number
  space_freed_formatted: string
  errors: string[]
}

export const storageApi = {
  getStats: () =>
    api.get<StorageStats>('/api/storage/stats'),

  cleanupTemp: (maxAgeHours: number = 24) =>
    api.post<CleanupResult>(`/api/storage/cleanup-temp?max_age_hours=${maxAgeHours}`),

  cleanupOrphaned: () =>
    api.post<CleanupResult>('/api/storage/cleanup-orphaned'),

  getProjectStorage: (projectId: number) =>
    api.get(`/api/storage/project/${projectId}/size`),

  cleanupProject: (projectId: number) =>
    api.delete<CleanupResult>(`/api/storage/project/${projectId}/cleanup`),
}

// Analytics
export interface OverviewStats {
  total_projects: number
  total_videos: number
  total_clips: number
  total_exported: number
  total_duration_hours: number
  avg_viral_score: number
  processing_success_rate: number
}

export interface DailyStats {
  date: string
  videos_processed: number
  clips_generated: number
  clips_exported: number
}

export interface TopClip {
  id: number
  title?: string
  viral_score: number
  duration: number
  video_id: number
  project_id: number
  exported: boolean
  created_at: string
}

export const analyticsApi = {
  getOverview: () =>
    api.get<OverviewStats>('/api/analytics/overview'),

  getDaily: (days: number = 7) =>
    api.get<DailyStats[]>(`/api/analytics/daily?days=${days}`),

  getTopClips: (limit: number = 10) =>
    api.get<TopClip[]>(`/api/analytics/top-clips?limit=${limit}`),

  getPlatformStats: () =>
    api.get<Array<{ platform: string; count: number; avg_duration: number }>>('/api/analytics/platform-stats'),

  getViralDistribution: () =>
    api.get<Array<{ range: string; count: number }>>('/api/analytics/viral-distribution'),

  getProjectStats: (projectId: number) =>
    api.get(`/api/analytics/project/${projectId}/stats`),
}

// Templates
export const templatesApi = {
  getAll: () =>
    api.get<ProcessingTemplate[]>('/api/templates/'),

  getDefault: () =>
    api.get<ProcessingTemplate | null>('/api/templates/default'),

  getById: (id: number) =>
    api.get<ProcessingTemplate>(`/api/templates/${id}`),

  create: (data: Partial<ProcessingTemplate>) =>
    api.post<ProcessingTemplate>('/api/templates/', data),

  update: (id: number, data: Partial<ProcessingTemplate>) =>
    api.put<ProcessingTemplate>(`/api/templates/${id}`, data),

  delete: (id: number) =>
    api.delete(`/api/templates/${id}`),

  setDefault: (id: number) =>
    api.post<ProcessingTemplate>(`/api/templates/${id}/set-default`),
}

// A/B Title Testing API
export const abTestingApi = {
  generateTitles: (clipId: number, options?: { numVariants?: number; tone?: string; language?: string }) =>
    api.post<{
      clip_id: number
      original_title: string
      variants: { title: string; approach: string; predicted_ctr: number }[]
      tone: string
      language: string
    }>('/api/processing/generate-ab-titles', {
      clip_id: clipId,
      num_variants: options?.numVariants || 3,
      tone: options?.tone || 'engaging',
      language: options?.language || 'en',
    }),
}

// Webhook API
export const webhooksApi = {
  list: () => api.get<{ webhooks: any[]; total: number }>('/api/webhooks'),

  create: (data: { url: string; events: string[]; secret?: string }) =>
    api.post('/api/webhooks', data),

  get: (webhookId: string) => api.get(`/api/webhooks/${webhookId}`),

  update: (webhookId: string, data: { url?: string; events?: string[]; active?: boolean }) =>
    api.put(`/api/webhooks/${webhookId}`, data),

  delete: (webhookId: string) => api.delete(`/api/webhooks/${webhookId}`),

  test: (webhookId: string) => api.post(`/api/webhooks/${webhookId}/test`),

  listEvents: () => api.get<{ events: string[]; descriptions: Record<string, string> }>('/api/webhooks/events/list'),
}

// Platform Upload API
export const platformsApi = {
  listSupported: () => api.get('/api/platforms/supported'),

  getCredentialsStatus: (platform: string) => api.get(`/api/platforms/credentials/${platform}`),

  saveCredentials: (platform: string, accessToken: string, refreshToken?: string) =>
    api.post('/api/platforms/credentials', {
      platform,
      access_token: accessToken,
      refresh_token: refreshToken,
    }),

  removeCredentials: (platform: string) => api.delete(`/api/platforms/credentials/${platform}`),

  uploadToYouTube: (clipId: number, data: {
    title: string
    description?: string
    tags?: string[]
    privacy?: 'private' | 'unlisted' | 'public'
  }) =>
    api.post('/api/platforms/upload/youtube', { clip_id: clipId, ...data }),

  uploadToTikTok: (clipId: number, data: {
    caption: string
    privacy?: 'private' | 'friends' | 'public'
  }) =>
    api.post('/api/platforms/upload/tiktok', { clip_id: clipId, ...data }),

  uploadToInstagram: (clipId: number, data: {
    caption: string
    share_to_feed?: boolean
  }) =>
    api.post('/api/platforms/upload/instagram', { clip_id: clipId, ...data }),

  getOAuthUrl: (platform: string) => api.get(`/api/platforms/oauth/${platform}/url`),
}

export default api
