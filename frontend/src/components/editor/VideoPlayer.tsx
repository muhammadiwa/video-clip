'use client'

import { useRef, useState, useEffect, useCallback } from 'react'
import { Play, Pause, Volume2, VolumeX, Maximize, SkipBack, SkipForward, RotateCcw, Keyboard, X } from 'lucide-react'
import { useKeyboardShortcuts, KEYBOARD_SHORTCUTS } from '@/hooks/useKeyboardShortcuts'

interface VideoPlayerProps {
  src: string
  poster?: string
  onTimeUpdate?: (currentTime: number) => void
  onDurationChange?: (duration: number) => void
  startTime?: number
  endTime?: number
  autoSeekToStart?: boolean
  className?: string
}

export default function VideoPlayer({
  src,
  poster,
  onTimeUpdate,
  onDurationChange,
  startTime,
  endTime,
  autoSeekToStart = true,
  className = '',
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const progressRef = useRef<HTMLDivElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [isClipMode, setIsClipMode] = useState(false)
  const [showShortcuts, setShowShortcuts] = useState(false)

  // Check if we're in clip preview mode
  useEffect(() => {
    setIsClipMode(startTime !== undefined && endTime !== undefined)
  }, [startTime, endTime])

  // Seek to start time when clip changes
  useEffect(() => {
    const video = videoRef.current
    if (!video || !autoSeekToStart) return

    if (startTime !== undefined) {
      const seekToStart = () => {
        video.pause()
        video.currentTime = startTime
        setCurrentTime(startTime)
        setIsPlaying(false)
        console.log(`[VideoPlayer] Seeked to clip start: ${startTime}s`)
      }

      // If video is ready, seek immediately
      if (video.readyState >= 2) {
        seekToStart()
      } else {
        // Wait for video to be ready
        const handleCanPlay = () => {
          seekToStart()
          video.removeEventListener('canplay', handleCanPlay)
        }
        video.addEventListener('canplay', handleCanPlay)
        
        // Also try seeking after loadedmetadata
        const handleLoadedMetadata = () => {
          seekToStart()
          video.removeEventListener('loadedmetadata', handleLoadedMetadata)
        }
        video.addEventListener('loadedmetadata', handleLoadedMetadata)
        
        return () => {
          video.removeEventListener('canplay', handleCanPlay)
          video.removeEventListener('loadedmetadata', handleLoadedMetadata)
        }
      }
    }
  }, [startTime, endTime, autoSeekToStart])

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const handleTimeUpdate = () => {
      const time = video.currentTime
      setCurrentTime(time)
      onTimeUpdate?.(time)

      // Auto-stop at endTime in clip mode
      if (isClipMode && endTime !== undefined && time >= endTime) {
        video.pause()
        setIsPlaying(false)
        // Optionally loop back to start
        // video.currentTime = startTime || 0
      }
    }

    const handleDurationChange = () => {
      setDuration(video.duration)
      onDurationChange?.(video.duration)
    }

    const handleEnded = () => {
      setIsPlaying(false)
    }

    const handlePlay = () => setIsPlaying(true)
    const handlePause = () => setIsPlaying(false)

    video.addEventListener('timeupdate', handleTimeUpdate)
    video.addEventListener('durationchange', handleDurationChange)
    video.addEventListener('ended', handleEnded)
    video.addEventListener('play', handlePlay)
    video.addEventListener('pause', handlePause)

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate)
      video.removeEventListener('durationchange', handleDurationChange)
      video.removeEventListener('ended', handleEnded)
      video.removeEventListener('play', handlePlay)
      video.removeEventListener('pause', handlePause)
    }
  }, [endTime, startTime, isClipMode, onTimeUpdate, onDurationChange])

  const togglePlay = useCallback(() => {
    const video = videoRef.current
    if (!video) return

    if (isPlaying) {
      video.pause()
    } else {
      // In clip mode, ensure we start from clip's startTime
      if (isClipMode && startTime !== undefined && endTime !== undefined) {
        const clipStart = startTime
        const clipEnd = endTime
        
        // If current time is outside clip boundaries, reset to start
        if (video.currentTime < clipStart - 0.5 || video.currentTime >= clipEnd) {
          video.currentTime = clipStart
        }
      }
      video.play()
    }
  }, [isPlaying, isClipMode, startTime, endTime])

  const toggleMute = () => {
    const video = videoRef.current
    if (!video) return
    video.muted = !video.muted
    setIsMuted(!isMuted)
  }

  const toggleFullscreen = () => {
    const container = videoRef.current?.parentElement
    if (!container) return

    if (!document.fullscreenElement) {
      container.requestFullscreen()
      setIsFullscreen(true)
    } else {
      document.exitFullscreen()
      setIsFullscreen(false)
    }
  }

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const video = videoRef.current
    const progress = progressRef.current
    if (!video || !progress) return

    const rect = progress.getBoundingClientRect()
    const clickPos = (e.clientX - rect.left) / rect.width

    if (isClipMode && startTime !== undefined && endTime !== undefined) {
      // In clip mode, progress bar represents clip duration
      const clipDuration = endTime - startTime
      const newTime = startTime + (clickPos * clipDuration)
      video.currentTime = Math.max(startTime, Math.min(newTime, endTime))
    } else {
      // Full video mode
      video.currentTime = clickPos * duration
    }
  }

  const skip = (seconds: number) => {
    const video = videoRef.current
    if (!video) return
    
    const newTime = video.currentTime + seconds
    
    if (isClipMode && startTime !== undefined && endTime !== undefined) {
      // In clip mode, constrain to clip boundaries
      video.currentTime = Math.max(startTime, Math.min(newTime, endTime))
    } else {
      // Full video mode
      video.currentTime = Math.max(0, Math.min(newTime, duration))
    }
  }

  const resetToStart = useCallback(() => {
    const video = videoRef.current
    if (!video) return
    
    if (isClipMode && startTime !== undefined) {
      video.currentTime = startTime
    } else {
      video.currentTime = 0
    }
  }, [isClipMode, startTime])

  const skipCallback = useCallback((seconds: number) => {
    skip(seconds)
  }, [isClipMode, startTime, endTime, duration])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if user is typing in an input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return
      }

      switch (e.key.toLowerCase()) {
        case ' ':
        case 'k':
          e.preventDefault()
          togglePlay()
          break
        case 'j':
          e.preventDefault()
          skip(-5)
          break
        case 'l':
          e.preventDefault()
          skip(5)
          break
        case 'arrowleft':
          e.preventDefault()
          skip(-5)
          break
        case 'arrowright':
          e.preventDefault()
          skip(5)
          break
        case 'arrowup':
          e.preventDefault()
          if (videoRef.current) {
            videoRef.current.volume = Math.min(1, videoRef.current.volume + 0.1)
          }
          break
        case 'arrowdown':
          e.preventDefault()
          if (videoRef.current) {
            videoRef.current.volume = Math.max(0, videoRef.current.volume - 0.1)
          }
          break
        case 'm':
          e.preventDefault()
          toggleMute()
          break
        case 'f':
          e.preventDefault()
          toggleFullscreen()
          break
        case 'r':
          e.preventDefault()
          resetToStart()
          break
        case '0':
        case 'home':
          e.preventDefault()
          resetToStart()
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [togglePlay, resetToStart])

  const formatTime = (time: number) => {
    const mins = Math.floor(time / 60)
    const secs = Math.floor(time % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  // Calculate progress based on mode
  let progress = 0
  let displayCurrentTime = currentTime
  let displayDuration = duration

  if (isClipMode && startTime !== undefined && endTime !== undefined) {
    const clipDuration = endTime - startTime
    const clipProgress = currentTime - startTime
    progress = clipDuration > 0 ? (clipProgress / clipDuration) * 100 : 0
    displayCurrentTime = Math.max(0, currentTime - startTime)
    displayDuration = clipDuration
  } else {
    progress = duration > 0 ? (currentTime / duration) * 100 : 0
  }

  // Clamp progress
  progress = Math.max(0, Math.min(100, progress))

  return (
    <div className={`relative group bg-black rounded-xl overflow-hidden ${className}`}>
      <video
        ref={videoRef}
        src={src}
        poster={poster}
        className="w-full h-full object-contain"
        playsInline
      />

      {/* Clip mode indicator */}
      {isClipMode && (
        <div className="absolute top-3 left-3 px-2 py-1 bg-primary/80 backdrop-blur-sm rounded-lg text-xs font-medium flex items-center gap-1.5">
          <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
          Clip Preview
        </div>
      )}

      {/* Controls overlay */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        {/* Progress bar */}
        <div
          ref={progressRef}
          className="w-full h-2 bg-white/20 rounded-full cursor-pointer mb-3 group/progress hover:h-3 transition-all"
          onClick={handleProgressClick}
        >
          <div
            className="h-full bg-gradient-to-r from-primary to-accent-pink rounded-full relative transition-all"
            style={{ width: `${progress}%` }}
          >
            <div className="absolute right-0 top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-lg opacity-0 group-hover/progress:opacity-100 transition-opacity transform scale-0 group-hover/progress:scale-100" />
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {/* Reset button */}
            <button
              onClick={resetToStart}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              title="Reset to start"
            >
              <RotateCcw className="w-4 h-4" />
            </button>

            {/* Skip back */}
            <button
              onClick={() => skip(-5)}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              title="Back 5s"
            >
              <SkipBack className="w-5 h-5" />
            </button>
            
            {/* Play/Pause */}
            <button
              onClick={togglePlay}
              className="p-3 bg-white/10 hover:bg-white/20 rounded-full transition-colors"
            >
              {isPlaying ? (
                <Pause className="w-6 h-6" />
              ) : (
                <Play className="w-6 h-6 ml-0.5" />
              )}
            </button>

            {/* Skip forward */}
            <button
              onClick={() => skip(5)}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              title="Forward 5s"
            >
              <SkipForward className="w-5 h-5" />
            </button>

            {/* Time display */}
            <div className="text-sm text-white/80 ml-2 font-mono">
              <span>{formatTime(displayCurrentTime)}</span>
              <span className="text-white/40 mx-1">/</span>
              <span className="text-white/60">{formatTime(displayDuration)}</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Keyboard shortcuts button */}
            <button
              onClick={() => setShowShortcuts(true)}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors hidden md:flex"
              title="Keyboard shortcuts (?)"
            >
              <Keyboard className="w-4 h-4 text-white/60" />
            </button>

            {/* Volume */}
            <button
              onClick={toggleMute}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              title="Mute (M)"
            >
              {isMuted ? (
                <VolumeX className="w-5 h-5" />
              ) : (
                <Volume2 className="w-5 h-5" />
              )}
            </button>

            {/* Fullscreen */}
            <button
              onClick={toggleFullscreen}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              title="Fullscreen (F)"
            >
              <Maximize className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Center play button when paused */}
      {!isPlaying && (
        <button
          onClick={togglePlay}
          className="absolute inset-0 flex items-center justify-center bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <div className="w-20 h-20 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center hover:bg-white/30 hover:scale-110 transition-all">
            <Play className="w-10 h-10 ml-1" />
          </div>
        </button>
      )}

      {/* Keyboard Shortcuts Modal */}
      {showShortcuts && (
        <div 
          className="absolute inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50"
          onClick={() => setShowShortcuts(false)}
        >
          <div 
            className="bg-dark-surface rounded-xl p-6 max-w-sm w-full mx-4"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Keyboard className="w-5 h-5 text-primary" />
                Keyboard Shortcuts
              </h3>
              <button
                onClick={() => setShowShortcuts(false)}
                className="p-1 hover:bg-white/10 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="space-y-2">
              {KEYBOARD_SHORTCUTS.map((shortcut, i) => (
                <div key={i} className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">{shortcut.action}</span>
                  <kbd className="px-2 py-1 bg-white/10 rounded text-xs font-mono">{shortcut.key}</kbd>
                </div>
              ))}
            </div>
            <p className="text-[10px] text-gray-500 mt-4 text-center">
              Press any key or click outside to close
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
