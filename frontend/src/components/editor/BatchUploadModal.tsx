'use client'

import { useState, useRef, useCallback } from 'react'
import { 
  X, 
  Upload, 
  Youtube, 
  Loader, 
  CheckCircle, 
  AlertCircle,
  Plus,
  Trash2,
  FileVideo,
  Link2
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { videosApi, processingApi } from '@/lib/api'

interface BatchUploadModalProps {
  projectId: number
  onClose: () => void
  onSuccess: () => void
}

type UploadMode = 'files' | 'youtube'

interface YouTubeUrl {
  id: string
  url: string
  status: 'pending' | 'downloading' | 'success' | 'error'
  message?: string
}

export default function BatchUploadModal({ projectId, onClose, onSuccess }: BatchUploadModalProps) {
  const [mode, setMode] = useState<UploadMode>('files')
  const [files, setFiles] = useState<File[]>([])
  const [youtubeUrls, setYoutubeUrls] = useState<YouTubeUrl[]>([])
  const [newUrl, setNewUrl] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadStatus, setUploadStatus] = useState<string>('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFilesSelect = useCallback((selectedFiles: FileList | null) => {
    if (!selectedFiles) return
    const videoFiles = Array.from(selectedFiles).filter(f => 
      f.type.startsWith('video/') || ['.mp4', '.mov', '.avi', '.mkv', '.webm'].some(ext => f.name.toLowerCase().endsWith(ext))
    )
    setFiles(prev => [...prev, ...videoFiles])
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    handleFilesSelect(e.dataTransfer.files)
  }, [handleFilesSelect])

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const addYoutubeUrl = () => {
    if (!newUrl.trim()) return
    const urlPattern = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$/
    if (!urlPattern.test(newUrl)) {
      alert('Please enter a valid YouTube URL')
      return
    }
    setYoutubeUrls(prev => [...prev, { id: Date.now().toString(), url: newUrl.trim(), status: 'pending' }])
    setNewUrl('')
  }

  const removeYoutubeUrl = (id: string) => {
    setYoutubeUrls(prev => prev.filter(u => u.id !== id))
  }

  const handleUploadFiles = async () => {
    if (files.length === 0) return
    
    setIsUploading(true)
    setUploadStatus('Uploading files...')
    
    try {
      const response = await videosApi.batchUpload(projectId, files, (progress) => {
        setUploadProgress(progress)
      })
      
      setUploadStatus(`Uploaded ${response.data.uploaded.length} files successfully`)
      setTimeout(() => {
        onSuccess()
        onClose()
      }, 1500)
    } catch (error) {
      console.error('Upload failed:', error)
      setUploadStatus('Upload failed. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  const handleDownloadYoutube = async () => {
    if (youtubeUrls.length === 0) return
    
    setIsUploading(true)
    setUploadStatus('Starting downloads...')
    
    const urls = youtubeUrls.map(u => u.url)
    
    try {
      const response = await processingApi.batchDownloadYouTube(projectId, urls)
      
      setYoutubeUrls(prev => prev.map((item, index) => ({
        ...item,
        status: response.data.jobs[index]?.status === 'started' ? 'downloading' : 'error',
        message: response.data.jobs[index]?.status === 'started' ? 'Download started' : 'Failed to start'
      })))
      
      setUploadStatus(response.data.message)
      setTimeout(() => {
        onSuccess()
        onClose()
      }, 2000)
    } catch (error) {
      console.error('Download failed:', error)
      setUploadStatus('Failed to start downloads')
    } finally {
      setIsUploading(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4"
      onClick={(e) => e.target === e.currentTarget && !isUploading && onClose()}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="bg-dark-surface rounded-2xl w-full max-w-2xl max-h-[85vh] overflow-hidden shadow-2xl"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <Upload className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-semibold">Batch Upload</h2>
          </div>
          <button
            onClick={onClose}
            disabled={isUploading}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors disabled:opacity-50"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Mode Tabs */}
        <div className="flex border-b border-white/5">
          <button
            onClick={() => setMode('files')}
            disabled={isUploading}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-all flex items-center justify-center gap-2 ${
              mode === 'files'
                ? 'text-white bg-white/5 border-b-2 border-primary'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <FileVideo className="w-4 h-4" />
            Upload Files
          </button>
          <button
            onClick={() => setMode('youtube')}
            disabled={isUploading}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-all flex items-center justify-center gap-2 ${
              mode === 'youtube'
                ? 'text-white bg-white/5 border-b-2 border-red-500'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <Youtube className="w-4 h-4 text-red-500" />
            YouTube URLs
          </button>
        </div>

        <div className="p-4 space-y-4 max-h-[calc(85vh-200px)] overflow-y-auto">
          {mode === 'files' ? (
            <>
              {/* Drop Zone */}
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-white/20 rounded-xl p-8 text-center cursor-pointer hover:border-primary/50 hover:bg-primary/5 transition-all"
              >
                <Upload className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                <p className="text-sm font-medium mb-1">Drop video files here</p>
                <p className="text-xs text-gray-500">or click to browse</p>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept="video/*"
                  onChange={(e) => handleFilesSelect(e.target.files)}
                  className="hidden"
                />
              </div>

              {/* File List */}
              {files.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">{files.length} file(s) selected</span>
                    <button
                      onClick={() => setFiles([])}
                      className="text-red-400 hover:text-red-300 text-xs"
                    >
                      Clear all
                    </button>
                  </div>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {files.map((file, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-3 p-3 bg-white/5 rounded-lg"
                      >
                        <FileVideo className="w-8 h-8 text-primary flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{file.name}</p>
                          <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                        </div>
                        <button
                          onClick={() => removeFile(index)}
                          className="p-1.5 hover:bg-red-500/20 rounded-lg text-gray-400 hover:text-red-400 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <>
              {/* YouTube URL Input */}
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <Link2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="text"
                    value={newUrl}
                    onChange={(e) => setNewUrl(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && addYoutubeUrl()}
                    placeholder="Paste YouTube URL..."
                    className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:border-red-500/50 text-sm"
                  />
                </div>
                <button
                  onClick={addYoutubeUrl}
                  className="px-4 py-3 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-xl transition-colors"
                >
                  <Plus className="w-5 h-5" />
                </button>
              </div>

              {/* URL List */}
              {youtubeUrls.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">{youtubeUrls.length} URL(s) added</span>
                    <button
                      onClick={() => setYoutubeUrls([])}
                      className="text-red-400 hover:text-red-300 text-xs"
                    >
                      Clear all
                    </button>
                  </div>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {youtubeUrls.map((item) => (
                      <div
                        key={item.id}
                        className="flex items-center gap-3 p-3 bg-white/5 rounded-lg"
                      >
                        <Youtube className="w-6 h-6 text-red-500 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm truncate">{item.url}</p>
                          {item.message && (
                            <p className={`text-xs ${item.status === 'error' ? 'text-red-400' : 'text-green-400'}`}>
                              {item.message}
                            </p>
                          )}
                        </div>
                        {item.status === 'downloading' ? (
                          <Loader className="w-4 h-4 animate-spin text-primary" />
                        ) : item.status === 'success' ? (
                          <CheckCircle className="w-4 h-4 text-green-400" />
                        ) : item.status === 'error' ? (
                          <AlertCircle className="w-4 h-4 text-red-400" />
                        ) : (
                          <button
                            onClick={() => removeYoutubeUrl(item.id)}
                            className="p-1.5 hover:bg-red-500/20 rounded-lg text-gray-400 hover:text-red-400 transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {/* Progress */}
          {isUploading && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">{uploadStatus}</span>
                {mode === 'files' && <span className="text-primary font-bold">{uploadProgress}%</span>}
              </div>
              {mode === 'files' && (
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-primary to-accent-pink"
                    initial={{ width: 0 }}
                    animate={{ width: `${uploadProgress}%` }}
                  />
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-4 border-t border-white/10">
          <button
            onClick={onClose}
            disabled={isUploading}
            className="px-4 py-2 text-gray-400 hover:text-white transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={mode === 'files' ? handleUploadFiles : handleDownloadYoutube}
            disabled={isUploading || (mode === 'files' ? files.length === 0 : youtubeUrls.length === 0)}
            className="px-6 py-2 bg-gradient-to-r from-primary to-accent-pink rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isUploading ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                {mode === 'files' ? 'Uploading...' : 'Downloading...'}
              </>
            ) : (
              <>
                {mode === 'files' ? <Upload className="w-4 h-4" /> : <Youtube className="w-4 h-4" />}
                {mode === 'files' ? `Upload ${files.length} File(s)` : `Download ${youtubeUrls.length} Video(s)`}
              </>
            )}
          </button>
        </div>
      </motion.div>
    </motion.div>
  )
}
