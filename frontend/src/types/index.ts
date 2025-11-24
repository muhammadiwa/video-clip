export interface Project {
  id: number
  name: string
  description?: string
  status: 'created' | 'processing' | 'ready' | 'edited'
  source_language: string
  target_platform: 'shorts' | 'reels' | 'tiktok'
  target_duration: number
  aspect_ratio: string
  created_at: string
  updated_at?: string
}

export interface Video {
  id: number
  project_id: number
  filename: string
  original_filename: string
  file_path: string
  file_size: number
  duration?: number
  width?: number
  height?: number
  fps?: number
  codec?: string
  source_type: 'upload' | 'youtube' | 'vimeo'
  source_url?: string
  status: 'uploaded' | 'processing' | 'processed' | 'error'
  processing_progress: number
  created_at: string
}

export interface Clip {
  id: number
  project_id: number
  name: string
  description?: string
  start_time: number
  end_time: number
  duration: number
  viral_score: number
  category?: 'hook' | 'story' | 'punchline' | 'cta'
  keywords?: string[]
  aspect_ratio: string
  resolution: string
  fps: number
  subtitle_style?: SubtitleStyle
  overlays?: any
  audio_settings?: any
  status: 'detected' | 'edited' | 'exported'
  exported: boolean
  export_path?: string
  created_at: string
}

export interface Subtitle {
  id: number
  clip_id: number
  text: string
  start_time: number
  end_time: number
  language: string
  style?: SubtitleStyle
  created_at: string
}

export interface SubtitleStyle {
  font?: string
  fontSize?: number
  color?: string
  backgroundColor?: string
  strokeColor?: string
  strokeWidth?: number
  position?: 'top' | 'middle' | 'bottom'
  alignment?: 'left' | 'center' | 'right'
  bold?: boolean
  italic?: boolean
  shadow?: boolean
}

export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}
