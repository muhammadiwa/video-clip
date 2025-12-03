'use client'

import { useState, useEffect, useRef } from 'react'
import { 
  X, 
  Save, 
  Play, 
  Pause, 
  Scissors, 
  Clock, 
  Type,
  ChevronLeft,
  ChevronRight,
  RotateCcw
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import type { Clip } from '@/types'

interface ClipEditorProps {
  clip: Clip
  videoSrc: string
  videoDuration: number
  onSave: (updatedClip: Partial<Clip>) => Promise<void>
  onClose: () => void
}

export default function ClipEditor({
  clip,
  videoSrc,
  videoDuration,
  onSave,
  onClose,
}: ClipEditorProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(clip.start_time)
  const [startTime, setStartTime] = useState(clip.start_time)
  const [endTime, setEndTime] = useState(clip.end_time)
  const [title, setTitle] = useState(clip.title || '')
  const [description, setDescription] = useState(clip.description || '')
  const [isSaving, setIsSaving] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)

  // Update duration whenever start/end changes
  const duration = endTime - startTime

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const handleTimeUpdate = () => {
      setCurrentTime(video.currentTime)
      if (video.currentTime >= endTime) {
        video.pause()
        setIsPlaying(false)
      }
    }

    video.addEventListener('timeupdate', handleTimeUpdate)
    return () => video.removeEventListener('timeupdate', handleTimeUpdate)
  }, [endTime])

  useEffect(() => {
    // Check if there are changes
    const changed = 
      startTime !== clip.start_time ||
      endTime !== clip.end_time ||
      title !== (clip.title || '') ||
      description !== (clip.description || '')
    setHasChanges(changed)
  }, [startTime, endTime, title, description, clip])

  const togglePlay = () => {
    const video = videoRef.current
    if (!video) return

    if (isPlaying) {
      video.pause()
    } else {
      if (video.currentTime < startTime || video.currentTime >= endTime) {
        video.currentTime = startTime
      }
      video.play()
    }
    setIsPlaying(!isPlaying)
  }

  const seekTo = (time: number) => {
    const video = videoRef.current
    if (!video) return
    video.currentTime = Math.max(0, Math.min(time, videoDuration))
    setCurrentTime(time)
  }

  const setInPoint = () => {
    if (currentTime < endTime - 1) {
      setStartTime(currentTime)
    }
  }

  const setOutPoint = () => {
    if (currentTime > startTime + 1) {
      setEndTime(currentTime)
    }
  }

  const resetTimes = () => {
    setStartTime(clip.start_time)
    setEndTime(clip.end_time)
    seekTo(clip.start_time)
  }

  const handleSave = async () => {
    setIsSaving(true)
    try {
      await onSave({
        start_time: startTime,
        end_time: endTime,
        duration: endTime - startTime,
        title,
        description,
      })
      onClose()
    } catch (error) {
      console.error('Failed to save clip:', error)
    } finally {
      setIsSaving(false)
    }
  }

  const formatTime = (time: number) => {
    const mins = Math.floor(time / 60)
    const secs = Math.floor(time % 60)
    const ms = Math.floor((time % 1) * 100)
    return `${mins}:${secs.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`
  }

  const progressPercent = ((currentTime - startTime) / duration) * 100

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="bg-dark-surface rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden shadow-2xl"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <Scissors className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-semibold">Edit Clip</h2>
            {hasChanges && (
              <span className="text-xs px-2 py-0.5 bg-yellow-500/20 text-yellow-400 rounded">
                Unsaved changes
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 space-y-4 max-h-[calc(90vh-140px)] overflow-y-auto">
          {/* Video Preview */}
          <div className="relative bg-black rounded-xl overflow-hidden aspect-video">
            <video
              ref={videoRef}
              src={videoSrc}
              className="w-full h-full object-contain"
              playsInline
            />
            
            {/* Overlay controls */}
            <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
              {/* Progress bar */}
              <div className="relative h-2 bg-white/20 rounded-full mb-3 cursor-pointer"
                onClick={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect()
                  const pos = (e.clientX - rect.left) / rect.width
                  const newTime = startTime + (pos * duration)
                  seekTo(Math.max(startTime, Math.min(newTime, endTime)))
                }}
              >
                <div 
                  className="absolute h-full bg-primary rounded-full"
                  style={{ width: `${Math.max(0, Math.min(100, progressPercent))}%` }}
                />
                <div 
                  className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-lg"
                  style={{ left: `${Math.max(0, Math.min(100, progressPercent))}%`, transform: 'translate(-50%, -50%)' }}
                />
              </div>

              {/* Controls */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => seekTo(startTime)}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                    title="Go to start"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => seekTo(currentTime - 1)}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                  <button
                    onClick={togglePlay}
                    className="p-3 bg-white/10 hover:bg-white/20 rounded-full transition-colors"
                  >
                    {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6 ml-0.5" />}
                  </button>
                  <button
                    onClick={() => seekTo(currentTime + 1)}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>

                <div className="text-sm font-mono text-white/80">
                  {formatTime(currentTime)} / {formatTime(duration)}
                </div>
              </div>
            </div>
          </div>

          {/* Trim Controls */}
          <div className="grid grid-cols-2 gap-4">
            <div className="glass-card p-4">
              <label className="text-xs text-gray-400 mb-2 block">Start Time (In Point)</label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  value={startTime.toFixed(2)}
                  onChange={(e) => {
                    const val = parseFloat(e.target.value)
                    if (!isNaN(val) && val >= 0 && val < endTime - 1) {
                      setStartTime(val)
                    }
                  }}
                  step="0.1"
                  className="flex-1 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm font-mono focus:outline-none focus:border-primary"
                />
                <button
                  onClick={setInPoint}
                  className="px-3 py-2 bg-primary/20 hover:bg-primary/30 text-primary rounded-lg text-sm font-medium transition-colors"
                  title="Set current position as In point"
                >
                  Set In
                </button>
              </div>
            </div>

            <div className="glass-card p-4">
              <label className="text-xs text-gray-400 mb-2 block">End Time (Out Point)</label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  value={endTime.toFixed(2)}
                  onChange={(e) => {
                    const val = parseFloat(e.target.value)
                    if (!isNaN(val) && val > startTime + 1 && val <= videoDuration) {
                      setEndTime(val)
                    }
                  }}
                  step="0.1"
                  className="flex-1 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm font-mono focus:outline-none focus:border-primary"
                />
                <button
                  onClick={setOutPoint}
                  className="px-3 py-2 bg-accent-pink/20 hover:bg-accent-pink/30 text-accent-pink rounded-lg text-sm font-medium transition-colors"
                  title="Set current position as Out point"
                >
                  Set Out
                </button>
              </div>
            </div>
          </div>

          {/* Duration display */}
          <div className="flex items-center justify-center gap-4 py-2">
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <Clock className="w-4 h-4" />
              <span>Duration: <span className="text-white font-mono">{formatTime(duration)}</span></span>
            </div>
            <button
              onClick={resetTimes}
              className="text-xs text-gray-400 hover:text-white transition-colors underline"
            >
              Reset to original
            </button>
          </div>

          {/* Metadata */}
          <div className="space-y-4">
            <div>
              <label className="text-xs text-gray-400 mb-2 flex items-center gap-1.5">
                <Type className="w-3.5 h-3.5" />
                Title
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter clip title..."
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:border-primary transition-colors"
              />
            </div>

            <div>
              <label className="text-xs text-gray-400 mb-2 block">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Enter clip description..."
                rows={3}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:border-primary transition-colors resize-none"
              />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-4 border-t border-white/10">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={!hasChanges || isSaving}
            className="px-6 py-2 bg-gradient-to-r from-primary to-accent-pink rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all hover:shadow-lg hover:shadow-primary/20"
          >
            {isSaving ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Save Changes
              </>
            )}
          </button>
        </div>
      </motion.div>
    </motion.div>
  )
}
