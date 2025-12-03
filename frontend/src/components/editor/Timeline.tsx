'use client'

import { useRef, useState, useCallback } from 'react'
import { motion, Reorder, useDragControls } from 'framer-motion'
import { GripVertical, Scissors } from 'lucide-react'
import type { Clip } from '@/types'

interface TimelineProps {
  duration: number
  clips: Clip[]
  currentTime?: number
  selectedClip?: Clip | null
  onSeek?: (time: number) => void
  onClipSelect?: (clip: Clip) => void
  onClipReorder?: (clips: Clip[]) => void
  onClipTrim?: (clipId: number, startTime: number, endTime: number) => void
}

export default function Timeline({
  duration,
  clips,
  currentTime = 0,
  selectedClip,
  onSeek,
  onClipSelect,
  onClipReorder,
  onClipTrim,
}: TimelineProps) {
  const timelineRef = useRef<HTMLDivElement>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [trimming, setTrimming] = useState<{ clipId: number; edge: 'start' | 'end' } | null>(null)
  const [viewMode, setViewMode] = useState<'timeline' | 'list'>('timeline')

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const handleTimelineClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!timelineRef.current || !duration) return
    
    const rect = timelineRef.current.getBoundingClientRect()
    const pos = (e.clientX - rect.left) / rect.width
    const newTime = pos * duration
    onSeek?.(Math.max(0, Math.min(newTime, duration)))
  }

  const getClipPosition = (clip: Clip) => {
    if (!duration) return { left: 0, width: 0 }
    const left = (clip.start_time / duration) * 100
    const width = (clip.duration / duration) * 100
    return { left: `${left}%`, width: `${width}%` }
  }

  const getClipColor = (clip: Clip, index: number) => {
    const colors = [
      'from-primary/60 to-primary/40',
      'from-accent-cyan/60 to-accent-cyan/40',
      'from-accent-pink/60 to-accent-pink/40',
      'from-green-500/60 to-green-500/40',
      'from-yellow-500/60 to-yellow-500/40',
      'from-orange-500/60 to-orange-500/40',
    ]
    return colors[index % colors.length]
  }

  const timeMarkers = []
  const markerInterval = duration > 300 ? 60 : duration > 60 ? 30 : 10
  for (let i = 0; i <= duration; i += markerInterval) {
    timeMarkers.push(i)
  }

  const playheadPosition = duration > 0 ? (currentTime / duration) * 100 : 0

  const handleTrimStart = useCallback((clipId: number, edge: 'start' | 'end', e: React.MouseEvent) => {
    e.stopPropagation()
    setTrimming({ clipId, edge })
  }, [])

  const handleTrimMove = useCallback((e: React.MouseEvent) => {
    if (!trimming || !timelineRef.current || !duration) return
    
    const rect = timelineRef.current.getBoundingClientRect()
    const pos = (e.clientX - rect.left) / rect.width
    const time = pos * duration
    
    const clip = clips.find(c => c.id === trimming.clipId)
    if (!clip) return
    
    if (trimming.edge === 'start') {
      const newStart = Math.max(0, Math.min(time, clip.end_time - 1))
      onClipTrim?.(clip.id, newStart, clip.end_time)
    } else {
      const newEnd = Math.max(clip.start_time + 1, Math.min(time, duration))
      onClipTrim?.(clip.id, clip.start_time, newEnd)
    }
  }, [trimming, clips, duration, onClipTrim])

  const handleTrimEnd = useCallback(() => {
    setTrimming(null)
  }, [])

  return (
    <div className="glass-card p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-gray-400">Timeline</h3>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setViewMode('timeline')}
            className={`px-2 py-1 text-xs rounded ${viewMode === 'timeline' ? 'bg-primary/20 text-primary' : 'text-gray-500 hover:text-white'}`}
          >
            Timeline
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`px-2 py-1 text-xs rounded ${viewMode === 'list' ? 'bg-primary/20 text-primary' : 'text-gray-500 hover:text-white'}`}
          >
            List
          </button>
        </div>
      </div>

      {viewMode === 'list' && clips.length > 0 ? (
        <Reorder.Group 
          axis="y" 
          values={clips} 
          onReorder={(newOrder) => onClipReorder?.(newOrder)}
          className="space-y-2"
        >
          {clips.map((clip, index) => (
            <Reorder.Item
              key={clip.id}
              value={clip}
              className={`flex items-center gap-2 p-2 bg-white/5 rounded-lg cursor-grab active:cursor-grabbing ${
                selectedClip?.id === clip.id ? 'ring-2 ring-primary' : ''
              }`}
              onClick={() => onClipSelect?.(clip)}
            >
              <GripVertical className="w-4 h-4 text-gray-500" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{clip.title || `Clip ${index + 1}`}</p>
                <p className="text-xs text-gray-500">
                  {formatTime(clip.start_time)} - {formatTime(clip.end_time)} ({formatTime(clip.duration)})
                </p>
              </div>
              <div className="flex items-center gap-1">
                <span className="text-xs text-primary font-medium">{Math.round(clip.viral_score * 100)}%</span>
              </div>
            </Reorder.Item>
          ))}
        </Reorder.Group>
      ) : (
        <>
      {/* Time markers */}
      <div className="relative h-6 mb-2">
        {timeMarkers.map((time) => (
          <div
            key={time}
            className="absolute text-xs text-gray-500"
            style={{ left: `${(time / duration) * 100}%`, transform: 'translateX(-50%)' }}
          >
            {formatTime(time)}
          </div>
        ))}
      </div>

      {/* Timeline track */}
      <div
        ref={timelineRef}
        className="relative h-16 bg-white/5 rounded-lg cursor-pointer overflow-hidden"
        onClick={handleTimelineClick}
      >
        {/* Grid lines */}
        <div className="absolute inset-0 flex">
          {timeMarkers.map((time, i) => (
            <div
              key={time}
              className="absolute h-full border-l border-white/10"
              style={{ left: `${(time / duration) * 100}%` }}
            />
          ))}
        </div>

        {/* Clips */}
        {clips.map((clip, index) => {
          const pos = getClipPosition(clip)
          const isSelected = selectedClip?.id === clip.id
          
          return (
            <motion.div
              key={clip.id}
              initial={{ opacity: 0, scaleY: 0 }}
              animate={{ opacity: 1, scaleY: 1 }}
              className={`absolute top-2 bottom-2 rounded-md cursor-pointer transition-all ${
                isSelected ? 'ring-2 ring-white z-10' : 'hover:ring-1 hover:ring-white/50'
              }`}
              style={{ left: pos.left, width: pos.width }}
              onClick={(e) => {
                e.stopPropagation()
                onClipSelect?.(clip)
              }}
            >
              <div
                className={`w-full h-full rounded-md bg-gradient-to-r ${getClipColor(clip, index)} backdrop-blur-sm`}
              >
                <div className="px-2 py-1 h-full flex flex-col justify-between overflow-hidden">
                  <span className="text-xs font-medium truncate">
                    {clip.title || `Clip ${index + 1}`}
                  </span>
                  <div className="flex items-center gap-1">
                    <span className="text-[10px] text-white/60">
                      {Math.round(clip.viral_score * 100)}%
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          )
        })}

        {/* Playhead */}
        <motion.div
          className="absolute top-0 bottom-0 w-0.5 bg-white z-20 pointer-events-none"
          style={{ left: `${playheadPosition}%` }}
          animate={{ left: `${playheadPosition}%` }}
          transition={{ duration: 0.1 }}
        >
          <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-3 h-3 bg-white rounded-full" />
        </motion.div>
      </div>

      {/* Current time display */}
      <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
        <span>{formatTime(currentTime)}</span>
        <span>{formatTime(duration)}</span>
      </div>
        </>
      )}

      {/* Clip count */}
      <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between text-xs">
        <span className="text-gray-400">
          {clips.length} clip{clips.length !== 1 ? 's' : ''} detected
        </span>
        {selectedClip && (
          <span className="text-primary">
            Selected: {selectedClip.title || `Clip ${clips.findIndex(c => c.id === selectedClip.id) + 1}`}
          </span>
        )}
      </div>
    </div>
  )
}
