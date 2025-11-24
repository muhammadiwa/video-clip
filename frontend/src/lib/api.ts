import axios from 'axios'
import type { Project, Video, Clip, Subtitle } from '@/types'

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

export default api
