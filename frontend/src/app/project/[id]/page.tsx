'use client'

import { useState, useEffect, useCallback } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  ArrowLeft, 
  Youtube, 
  Loader, 
  CheckCircle,
  Video,
  Scissors,
  Download,
  RefreshCw,
  Play,
  Clock,
  Zap,
  Film,
  ChevronRight,
  MoreVertical,
  Sparkles,
  TrendingUp,
  FileText
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import VideoPlayer from '@/components/editor/VideoPlayer'
import ClipCard from '@/components/editor/ClipCard'
import Timeline from '@/components/editor/Timeline'
import ProcessingPanel, { ProcessingOptions } from '@/components/editor/ProcessingPanel'
import ClipEditor from '@/components/editor/ClipEditor'
import BatchUploadModal from '@/components/editor/BatchUploadModal'
import ExportQueue from '@/components/editor/ExportQueue'
import ThemeToggle from '@/components/ThemeToggle'
import { projectsApi, videosApi, clipsApi, processingApi } from '@/lib/api'
import type { Project, Video as VideoType, Clip } from '@/types'

interface ProcessingStep {
  id: string
  label: string
  status: 'pending' | 'running' | 'completed' | 'error'
  progress?: number
  message?: string
}

export default function ProjectPage() {
  const params = useParams()
  const router = useRouter()
  const projectId = parseInt(params.id as string)

  const [project, setProject] = useState<Project | null>(null)
  const [videos, setVideos] = useState<VideoType[]>([])
  const [clips, setClips] = useState<Clip[]>([])
  const [selectedVideo, setSelectedVideo] = useState<VideoType | null>(null)
  const [selectedClip, setSelectedClip] = useState<Clip | null>(null)
  const [currentTime, setCurrentTime] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingSteps, setProcessingSteps] = useState<ProcessingStep[]>([])
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [showYoutubeInput, setShowYoutubeInput] = useState(false)
  const [showBatchUpload, setShowBatchUpload] = useState(false)
  const [activeTab, setActiveTab] = useState<'clips' | 'videos'>('clips')
  const [editingClip, setEditingClip] = useState<Clip | null>(null)

  // Load project data
  useEffect(() => {
    const loadProject = async () => {
      try {
        const [projectRes, videosRes] = await Promise.all([
          projectsApi.getById(projectId),
          videosApi.getByProjectId(projectId),
        ])
        setProject(projectRes.data)
        setVideos(videosRes.data)
        
        if (videosRes.data.length > 0) {
          setSelectedVideo(videosRes.data[0])
          const clipsRes = await clipsApi.getByVideoId(videosRes.data[0].id)
          setClips(clipsRes.data)
        }
      } catch (error) {
        console.error('Failed to load project:', error)
      } finally {
        setIsLoading(false)
      }
    }
    loadProject()
  }, [projectId])

  // Load clips when video changes
  useEffect(() => {
    const loadClips = async () => {
      if (!selectedVideo) return
      try {
        const res = await clipsApi.getByVideoId(selectedVideo.id)
        setClips(res.data)
      } catch (error) {
        console.error('Failed to load clips:', error)
      }
    }
    loadClips()
  }, [selectedVideo])

  // Poll job status - uses actual task progress
  const pollJobStatus = useCallback(async (jobId: string, stepId: string) => {
    const poll = async () => {
      try {
        const res = await processingApi.getJobStatus(jobId)
        const { status, progress, result, error } = res.data

        setProcessingSteps(prev => prev.map(step => {
          if (step.id !== stepId) return step
          
          if (status === 'SUCCESS') {
            return { ...step, status: 'completed', progress: 100, message: 'Completed' }
          } else if (status === 'FAILURE') {
            return { ...step, status: 'error', message: error?.error || 'Failed' }
          } else if (status === 'PROGRESS' && progress) {
            // Use actual progress from task
            return { 
              ...step, 
              status: 'running', 
              progress: progress.current || 0,
              message: progress.status || 'Processing...'
            }
          } else if (status === 'PENDING') {
            return { ...step, status: 'running', progress: 0, message: 'Waiting...' }
          }
          return step
        }))

        if (status === 'SUCCESS' || status === 'FAILURE') {
          return { status, result, error }
        }
        
        await new Promise(resolve => setTimeout(resolve, 1500))
        return poll()
      } catch (error) {
        console.error('Poll error:', error)
        return { status: 'FAILURE', error }
      }
    }
    return poll()
  }, [])

  // Auto-refresh video status (for background pipeline updates)
  useEffect(() => {
    if (!selectedVideo || isProcessing) return

    // If video is still being processed in background, poll for updates
    const shouldPoll = !selectedVideo.has_transcription || !selectedVideo.has_scenes
    if (!shouldPoll) return

    const interval = setInterval(async () => {
      try {
        const res = await videosApi.getById(selectedVideo.id)
        const updatedVideo = res.data
        
        // Update if status changed
        if (updatedVideo.has_transcription !== selectedVideo.has_transcription ||
            updatedVideo.has_scenes !== selectedVideo.has_scenes) {
          setSelectedVideo(updatedVideo)
          
          // Also update in videos list
          setVideos(prev => prev.map(v => 
            v.id === updatedVideo.id ? updatedVideo : v
          ))
        }
        
        // Stop polling if both are done
        if (updatedVideo.has_transcription && updatedVideo.has_scenes) {
          clearInterval(interval)
        }
      } catch (error) {
        console.error('Failed to refresh video status:', error)
      }
    }, 3000) // Poll every 3 seconds

    return () => clearInterval(interval)
  }, [selectedVideo?.id, selectedVideo?.has_transcription, selectedVideo?.has_scenes, isProcessing])

  // Handle YouTube download
  const handleYoutubeDownload = async () => {
    if (!youtubeUrl) return
    
    setIsProcessing(true)
    setProcessingSteps([
      { id: 'download', label: 'Downloading from YouTube', status: 'running', progress: 0 },
      { id: 'background', label: 'Background processing (auto)', status: 'pending' }
    ])

    try {
      const res = await processingApi.downloadYouTube(projectId, youtubeUrl)
      const result = await pollJobStatus(res.data.job_id, 'download')
      
      if (result.status === 'SUCCESS') {
        // Mark download complete, background still running
        setProcessingSteps(prev => prev.map(s => 
          s.id === 'download' ? { ...s, status: 'completed', progress: 100 } :
          s.id === 'background' ? { ...s, status: 'running', message: 'Transcribing & detecting scenes...' } : s
        ))

        const videosRes = await videosApi.getByProjectId(projectId)
        setVideos(videosRes.data)
        if (videosRes.data.length > 0) {
          const newVideo = videosRes.data[videosRes.data.length - 1]
          setSelectedVideo(newVideo)
        }
        setYoutubeUrl('')
        setShowYoutubeInput(false)
        
        // Clear processing after a moment (background will be polled separately)
        setTimeout(() => {
          setProcessingSteps([])
        }, 2000)
      }
    } catch (error) {
      console.error('Download failed:', error)
    } finally {
      setIsProcessing(false)
    }
  }

  // Handle full processing pipeline - skip steps that are already done
  const handleStartProcessing = async (options: ProcessingOptions) => {
    if (!selectedVideo) return

    setIsProcessing(true)
    
    // Check what steps are needed based on video status
    const needsTranscription = !selectedVideo.has_transcription
    const needsScenes = !selectedVideo.has_scenes
    const initialSteps: ProcessingStep[] = []
    
    if (needsTranscription) {
      initialSteps.push({ id: 'transcribe', label: 'Transcribing audio', status: 'pending' })
    }
    if (needsScenes) {
      initialSteps.push({ id: 'scenes', label: 'Detecting scenes', status: 'pending' })
    }
    initialSteps.push({ id: 'viral', label: 'Generating viral clips', status: 'pending' })
    
    setProcessingSteps(initialSteps)

    try {
      // Step 1: Transcribe (only if needed)
      if (needsTranscription) {
        setProcessingSteps(prev => prev.map(s => 
          s.id === 'transcribe' ? { ...s, status: 'running', progress: 0 } : s
        ))
        const transcribeRes = await processingApi.transcribe(selectedVideo.id)
        await pollJobStatus(transcribeRes.data.job_id, 'transcribe')
        setSelectedVideo(prev => prev ? { ...prev, has_transcription: true } : null)
      }

      // Step 2: Detect scenes (only if needed)
      if (needsScenes) {
        setProcessingSteps(prev => prev.map(s => 
          s.id === 'scenes' ? { ...s, status: 'running', progress: 0 } : s
        ))
        const scenesRes = await processingApi.detectScenes(selectedVideo.id)
        await pollJobStatus(scenesRes.data.job_id, 'scenes')
        setSelectedVideo(prev => prev ? { ...prev, has_scenes: true } : null)
      }

      // Step 3: Detect and export viral clips
      setProcessingSteps(prev => prev.map(s => 
        s.id === 'viral' ? { ...s, status: 'running', progress: 0 } : s
      ))
      const viralRes = await processingApi.detectAndExport(selectedVideo.id, {
        topN: options.topN,
        targetPlatform: options.targetPlatform,
        aspectRatio: options.aspectRatio,
        burnSubtitles: options.burnSubtitles,
        subtitleStyle: options.subtitleStyle,
        minDuration: options.minDuration,
        maxDuration: options.maxDuration,
      })
      await pollJobStatus(viralRes.data.job_id, 'viral')

      // Refresh clips and video data
      const [clipsRes, videoRes] = await Promise.all([
        clipsApi.getByVideoId(selectedVideo.id),
        videosApi.getById(selectedVideo.id)
      ])
      setClips(clipsRes.data)
      setSelectedVideo(videoRes.data)

    } catch (error) {
      console.error('Processing failed:', error)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleClipSelect = (clip: Clip) => {
    setSelectedClip(clip)
  }

  const handleClipPreview = (clip: Clip) => {
    setSelectedClip(clip)
    setCurrentTime(clip.start_time)
  }

  const handleClipEdit = (clip: Clip) => {
    setEditingClip(clip)
  }

  const handleSaveClipEdit = async (updatedClip: Partial<Clip>) => {
    if (!editingClip) return
    
    await clipsApi.update(editingClip.id, updatedClip)
    
    // Refresh clips
    if (selectedVideo) {
      const res = await clipsApi.getByVideoId(selectedVideo.id)
      setClips(res.data)
    }
  }

  const handleRefreshClips = async () => {
    if (!selectedVideo) return
    try {
      const res = await clipsApi.getByVideoId(selectedVideo.id)
      setClips(res.data)
    } catch (error) {
      console.error('Failed to refresh clips:', error)
    }
  }

  const handleSelectVideo = async (video: VideoType) => {
    setSelectedVideo(video)
    setSelectedClip(null)
    setCurrentTime(0)
  }

  const formatDuration = (seconds: number) => {
    const m = Math.floor(seconds / 60)
    const s = Math.floor(seconds % 60)
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-dark-bg via-dark-surface to-dark-bg">
        <div className="flex flex-col items-center gap-4">
          <div className="relative">
            <div className="w-16 h-16 border-4 border-primary/30 rounded-full" />
            <div className="absolute top-0 left-0 w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
          <p className="text-gray-400">Loading project...</p>
        </div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-dark-bg via-dark-surface to-dark-bg">
        <div className="glass-card p-8 text-center max-w-md">
          <Video className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Project not found</h2>
          <p className="text-gray-400 mb-6">The project you're looking for doesn't exist.</p>
          <Link href="/dashboard" className="glass-button glow-effect inline-flex items-center gap-2">
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  const videoUrl = selectedVideo 
    ? `http://localhost:8000/${selectedVideo.file_path}`
    : ''

  const exportedClips = clips.filter(c => c.exported)
  const totalViralScore = clips.length > 0 
    ? Math.round(clips.reduce((acc, c) => acc + c.viral_score, 0) / clips.length * 100)
    : 0

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-bg via-dark-surface to-dark-bg">
      {/* Header */}
      <header className="border-b border-white/5 sticky top-0 z-50 bg-dark-bg/80 backdrop-blur-xl">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                href="/dashboard"
                className="p-2 hover:bg-white/5 rounded-xl transition-all duration-200 group"
              >
                <ArrowLeft className="w-5 h-5 group-hover:-translate-x-0.5 transition-transform" />
              </Link>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                  {project.name}
                </h1>
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-xs text-gray-500 flex items-center gap-1">
                    <Film className="w-3 h-3" /> {videos.length} video{videos.length !== 1 ? 's' : ''}
                  </span>
                  <span className="text-xs text-gray-500 flex items-center gap-1">
                    <Scissors className="w-3 h-3" /> {clips.length} clips
                  </span>
                  {totalViralScore > 0 && (
                    <span className="text-xs text-accent-cyan flex items-center gap-1">
                      <TrendingUp className="w-3 h-3" /> {totalViralScore}% avg viral
                    </span>
                  )}
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <ThemeToggle />
              
              <button
                onClick={handleRefreshClips}
                className="p-2.5 hover:bg-white/5 rounded-xl transition-all duration-200"
                title="Refresh clips"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
              
              <button
                onClick={() => setShowBatchUpload(true)}
                className="px-4 py-2.5 rounded-xl font-medium transition-all duration-200 flex items-center gap-2 bg-gradient-to-r from-primary/20 to-accent-pink/20 hover:from-primary/30 hover:to-accent-pink/30 border border-primary/30"
              >
                <Video className="w-5 h-5 text-primary" />
                Batch Upload
              </button>
              
              <button
                onClick={() => setShowYoutubeInput(!showYoutubeInput)}
                className={`px-4 py-2.5 rounded-xl font-medium transition-all duration-200 flex items-center gap-2 ${
                  showYoutubeInput 
                    ? 'bg-red-500/20 text-red-400 border border-red-500/30' 
                    : 'bg-white/5 hover:bg-white/10 border border-white/10'
                }`}
              >
                <Youtube className="w-5 h-5 text-red-500" />
                Add Video
              </button>
            </div>
          </div>

          {/* YouTube URL Input */}
          <AnimatePresence>
            {showYoutubeInput && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="mt-4 flex gap-3">
                  <div className="flex-1 relative">
                    <input
                      type="text"
                      value={youtubeUrl}
                      onChange={(e) => setYoutubeUrl(e.target.value)}
                      placeholder="Paste YouTube URL (e.g., https://youtube.com/watch?v=...)"
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:border-red-500/50 focus:ring-2 focus:ring-red-500/20 transition-all duration-200 placeholder:text-gray-500"
                    />
                  </div>
                  <button
                    onClick={handleYoutubeDownload}
                    disabled={!youtubeUrl || isProcessing}
                    className="px-6 py-3 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-red-500/20"
                  >
                    {isProcessing ? <Loader className="w-5 h-5 animate-spin" /> : 'Download'}
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-6">
        {videos.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card p-16 text-center max-w-2xl mx-auto"
          >
            <div className="w-24 h-24 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-red-500/20 to-purple-500/20 flex items-center justify-center">
              <Youtube className="w-12 h-12 text-red-400" />
            </div>
            <h2 className="text-2xl font-bold mb-3">Add your first video</h2>
            <p className="text-gray-400 mb-8 max-w-md mx-auto">
              Paste a YouTube URL to get started. Our AI will analyze the video and find the most viral-worthy moments.
            </p>
            <button
              onClick={() => setShowYoutubeInput(true)}
              className="px-8 py-4 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 rounded-xl font-semibold transition-all duration-200 shadow-lg shadow-red-500/20 inline-flex items-center gap-2"
            >
              <Youtube className="w-5 h-5" />
              Add from YouTube
            </button>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-6">
            {/* Left Column - Video & Timeline */}
            <div className="lg:col-span-8 space-y-4">
              {/* Video Player Card */}
              <div className="glass-card overflow-hidden">
                <VideoPlayer
                  src={videoUrl}
                  className="aspect-video"
                  onTimeUpdate={setCurrentTime}
                  startTime={selectedClip?.start_time}
                  endTime={selectedClip?.end_time}
                />
              </div>

              {/* Timeline */}
              {selectedVideo && selectedVideo.duration && (
                <div className="glass-card p-4">
                  <Timeline
                    duration={selectedVideo.duration || 0}
                    clips={clips}
                    currentTime={currentTime}
                    selectedClip={selectedClip}
                    onSeek={setCurrentTime}
                    onClipSelect={handleClipSelect}
                  />
                </div>
              )}

              {/* Video Info Card */}
              {selectedVideo && (
                <div className="glass-card p-5">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg mb-1 line-clamp-1">
                        {selectedVideo.original_filename}
                      </h3>
                      <div className="flex flex-wrap items-center gap-3 text-sm text-gray-400">
                        <span className="flex items-center gap-1">
                          <Film className="w-4 h-4" />
                          {selectedVideo.width}x{selectedVideo.height}
                        </span>
                        {selectedVideo.duration && (
                          <span className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            {formatDuration(selectedVideo.duration)}
                          </span>
                        )}
                        <span className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ${
                          selectedVideo.source_type === 'youtube' 
                            ? 'bg-red-500/20 text-red-400' 
                            : 'bg-blue-500/20 text-blue-400'
                        }`}>
                          {selectedVideo.source_type === 'youtube' ? 'YouTube' : 'Upload'}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {/* Background processing indicator */}
                      {(!selectedVideo.has_transcription || !selectedVideo.has_scenes) && (
                        <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-yellow-500/10 text-yellow-400 text-xs font-medium animate-pulse">
                          <Loader className="w-3.5 h-3.5 animate-spin" />
                          Processing...
                        </span>
                      )}
                      {selectedVideo.has_transcription && (
                        <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-500/10 text-blue-400 text-xs font-medium">
                          <FileText className="w-3.5 h-3.5" />
                          Transcribed
                        </span>
                      )}
                      {selectedVideo.has_scenes && (
                        <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-500/10 text-purple-400 text-xs font-medium">
                          <Film className="w-3.5 h-3.5" />
                          Scenes
                        </span>
                      )}
                      {clips.length > 0 && (
                        <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-green-500/10 text-green-400 text-xs font-medium">
                          <Sparkles className="w-3.5 h-3.5" />
                          {clips.length} Clips
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Right Column - Sidebar */}
            <div className="lg:col-span-4 space-y-4">
              {/* Processing Panel */}
              {selectedVideo && (
                <ProcessingPanel
                  videoId={selectedVideo.id}
                  onStartProcessing={handleStartProcessing}
                  isProcessing={isProcessing}
                  steps={processingSteps}
                />
              )}

              {/* Export Queue */}
              {clips.length > 0 && (
                <ExportQueue
                  projectId={projectId}
                  clips={clips}
                  onExportComplete={async (clipId, exportPath) => {
                    // Refresh clips to update exported status
                    if (selectedVideo) {
                      const res = await clipsApi.getByVideoId(selectedVideo.id)
                      setClips(res.data)
                    }
                  }}
                />
              )}

              {/* Tabs for Clips/Videos */}
              <div className="glass-card overflow-hidden">
                <div className="flex border-b border-white/5">
                  <button
                    onClick={() => setActiveTab('clips')}
                    className={`flex-1 px-4 py-3 text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2 ${
                      activeTab === 'clips'
                        ? 'text-white bg-white/5 border-b-2 border-primary'
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <Scissors className="w-4 h-4" />
                    Clips ({clips.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('videos')}
                    className={`flex-1 px-4 py-3 text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2 ${
                      activeTab === 'videos'
                        ? 'text-white bg-white/5 border-b-2 border-primary'
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <Film className="w-4 h-4" />
                    Videos ({videos.length})
                  </button>
                </div>

                <div className="p-4">
                  <AnimatePresence mode="wait">
                    {activeTab === 'clips' ? (
                      <motion.div
                        key="clips"
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 10 }}
                        transition={{ duration: 0.2 }}
                      >
                        {clips.length === 0 ? (
                          <div className="text-center py-12">
                            <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-white/5 flex items-center justify-center">
                              <Sparkles className="w-8 h-8 text-gray-600" />
                            </div>
                            <p className="text-sm text-gray-400 mb-1">No clips yet</p>
                            <p className="text-xs text-gray-500">
                              Run AI processing to find viral moments
                            </p>
                          </div>
                        ) : (
                          <div className="space-y-3 max-h-[500px] overflow-y-auto custom-scrollbar pr-1">
                            {clips.map((clip, index) => (
                              <ClipCard
                                key={clip.id}
                                clip={clip}
                                index={index}
                                isSelected={selectedClip?.id === clip.id}
                                onSelect={handleClipSelect}
                                onPreview={handleClipPreview}
                                onEdit={handleClipEdit}
                              />
                            ))}
                          </div>
                        )}

                        {exportedClips.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-white/5">
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-gray-400">
                                {exportedClips.length} clip{exportedClips.length !== 1 ? 's' : ''} exported
                              </span>
                              <span className="flex items-center gap-1 text-green-400">
                                <Download className="w-4 h-4" />
                                Ready to download
                              </span>
                            </div>
                          </div>
                        )}
                      </motion.div>
                    ) : (
                      <motion.div
                        key="videos"
                        initial={{ opacity: 0, x: 10 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -10 }}
                        transition={{ duration: 0.2 }}
                        className="space-y-2"
                      >
                        {videos.map((video) => (
                          <button
                            key={video.id}
                            onClick={() => handleSelectVideo(video)}
                            className={`w-full p-3 rounded-xl text-left transition-all duration-200 group ${
                              selectedVideo?.id === video.id
                                ? 'bg-primary/20 border border-primary/30'
                                : 'bg-white/5 hover:bg-white/10 border border-transparent'
                            }`}
                          >
                            <div className="flex items-center gap-3">
                              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                                selectedVideo?.id === video.id
                                  ? 'bg-primary/30'
                                  : 'bg-white/10'
                              }`}>
                                {video.source_type === 'youtube' ? (
                                  <Youtube className="w-5 h-5 text-red-400" />
                                ) : (
                                  <Video className="w-5 h-5" />
                                )}
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="font-medium text-sm truncate">
                                  {video.original_filename}
                                </p>
                                <div className="flex items-center gap-1.5 text-xs text-gray-400 mt-0.5">
                                  {video.duration && <span>{formatDuration(video.duration)}</span>}
                                  {video.has_transcription && (
                                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400" title="Transcribed" />
                                  )}
                                  {video.has_scenes && (
                                    <span className="w-1.5 h-1.5 rounded-full bg-purple-400" title="Scenes detected" />
                                  )}
                                </div>
                              </div>
                              <ChevronRight className={`w-4 h-4 transition-transform ${
                                selectedVideo?.id === video.id ? 'text-primary' : 'text-gray-500'
                              }`} />
                            </div>
                          </button>
                        ))}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Clip Editor Modal */}
      <AnimatePresence>
        {editingClip && selectedVideo && (
          <ClipEditor
            clip={editingClip}
            videoSrc={videoUrl}
            videoDuration={selectedVideo.duration || 0}
            onSave={handleSaveClipEdit}
            onClose={() => setEditingClip(null)}
          />
        )}
      </AnimatePresence>

      {/* Batch Upload Modal */}
      <AnimatePresence>
        {showBatchUpload && (
          <BatchUploadModal
            projectId={projectId}
            onClose={() => setShowBatchUpload(false)}
            onSuccess={async () => {
              const videosRes = await videosApi.getByProjectId(projectId)
              setVideos(videosRes.data)
              if (videosRes.data.length > 0 && !selectedVideo) {
                setSelectedVideo(videosRes.data[0])
              }
            }}
          />
        )}
      </AnimatePresence>

      {/* Custom Scrollbar Styles */}
      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.2);
        }
      `}</style>
    </div>
  )
}
