'use client'

import { useState } from 'react'
import { Play, Download, Clock, Sparkles, CheckCircle, Loader, AlertCircle, FileText, TrendingUp, Edit3 } from 'lucide-react'
import { motion } from 'framer-motion'
import type { Clip } from '@/types'

interface ClipCardProps {
  clip: Clip
  index: number
  isSelected?: boolean
  onSelect?: (clip: Clip) => void
  onPreview?: (clip: Clip) => void
  onEdit?: (clip: Clip) => void
}

export default function ClipCard({
  clip,
  index,
  isSelected,
  onSelect,
  onPreview,
  onEdit,
}: ClipCardProps) {
  const [isHovered, setIsHovered] = useState(false)
  const [showDescription, setShowDescription] = useState(false)

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'from-green-500 to-emerald-400'
    if (score >= 0.6) return 'from-yellow-500 to-amber-400'
    return 'from-orange-500 to-red-400'
  }

  const getScoreTextColor = (score: number) => {
    if (score >= 0.8) return 'text-green-400'
    if (score >= 0.6) return 'text-yellow-400'
    return 'text-orange-400'
  }

  const getScoreBgColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-500/10'
    if (score >= 0.6) return 'bg-yellow-500/10'
    return 'bg-orange-500/10'
  }

  const scorePercent = Math.round(clip.viral_score * 100)

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.03 }}
      className={`relative rounded-xl transition-all duration-200 overflow-hidden ${
        isSelected 
          ? 'bg-primary/10 ring-2 ring-primary shadow-lg shadow-primary/10' 
          : 'bg-white/[0.03] hover:bg-white/[0.06] ring-1 ring-white/5 hover:ring-white/10'
      }`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => onSelect?.(clip)}
    >
      {/* Score indicator bar */}
      <div className="h-1 w-full">
        <div 
          className={`h-full bg-gradient-to-r ${getScoreColor(clip.viral_score)}`}
          style={{ width: `${scorePercent}%` }}
        />
      </div>

      <div className="p-3">
        {/* Header with score badge */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex-1 min-w-0">
            <h4 className="font-medium text-sm leading-tight line-clamp-2">
              {clip.title || `Viral Clip #${index + 1}`}
            </h4>
          </div>
          <div className={`shrink-0 flex items-center gap-1 px-2 py-1 rounded-lg ${getScoreBgColor(clip.viral_score)}`}>
            <TrendingUp className={`w-3 h-3 ${getScoreTextColor(clip.viral_score)}`} />
            <span className={`text-xs font-bold ${getScoreTextColor(clip.viral_score)}`}>
              {scorePercent}%
            </span>
          </div>
        </div>

        {/* Description (if available) */}
        {clip.description && (
          <p className="text-xs text-gray-400 line-clamp-2 mb-2 leading-relaxed">
            {clip.description}
          </p>
        )}

        {/* Time and status row */}
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-3 text-gray-500">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {formatTime(clip.duration)}
            </span>
            <span className="text-gray-600">
              {formatTime(clip.start_time)} - {formatTime(clip.end_time)}
            </span>
          </div>
          
          {clip.exported && (
            <span className="flex items-center gap-1 text-green-400">
              <CheckCircle className="w-3 h-3" />
            </span>
          )}
        </div>

        {/* Action buttons - show on hover */}
        <motion.div 
          initial={false}
          animate={{ 
            height: isHovered ? 'auto' : 0,
            opacity: isHovered ? 1 : 0,
            marginTop: isHovered ? 12 : 0
          }}
          transition={{ duration: 0.15 }}
          className="overflow-hidden"
        >
          <div className="flex gap-2">
            <button
              onClick={(e) => {
                e.stopPropagation()
                onPreview?.(clip)
              }}
              className="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 bg-white/5 hover:bg-white/10 rounded-lg text-xs font-medium transition-colors"
            >
              <Play className="w-3.5 h-3.5" />
              Preview
            </button>

            {onEdit && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onEdit(clip)
                }}
                className="flex items-center justify-center gap-1.5 py-2 px-3 bg-white/5 hover:bg-white/10 rounded-lg text-xs font-medium transition-colors"
              >
                <Edit3 className="w-3.5 h-3.5" />
              </button>
            )}
            
            {clip.exported && clip.export_path ? (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  // Create download link and trigger download
                  const link = document.createElement('a')
                  link.href = `http://localhost:8000/${clip.export_path}`
                  link.download = clip.title 
                    ? `${clip.title.replace(/[^a-z0-9]/gi, '_')}.mp4`
                    : `clip_${clip.id}.mp4`
                  document.body.appendChild(link)
                  link.click()
                  document.body.removeChild(link)
                }}
                className="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 bg-green-500/10 hover:bg-green-500/20 text-green-400 rounded-lg text-xs font-medium transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                Download
              </button>
            ) : (
              <span className="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 bg-gray-500/10 text-gray-500 rounded-lg text-xs font-medium">
                <Download className="w-3.5 h-3.5" />
                Not exported
              </span>
            )}
          </div>
        </motion.div>
      </div>
    </motion.div>
  )
}
