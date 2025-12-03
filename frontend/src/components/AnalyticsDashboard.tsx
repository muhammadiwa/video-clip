'use client'

import { useState, useEffect } from 'react'
import { 
  X, 
  TrendingUp, 
  Film, 
  Scissors, 
  Download, 
  Clock, 
  Zap, 
  CheckCircle,
  Loader,
  BarChart3,
  RefreshCw
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { analyticsApi, OverviewStats, DailyStats, TopClip } from '@/lib/api'

interface AnalyticsDashboardProps {
  isOpen: boolean
  onClose: () => void
}

export default function AnalyticsDashboard({ isOpen, onClose }: AnalyticsDashboardProps) {
  const [overview, setOverview] = useState<OverviewStats | null>(null)
  const [dailyStats, setDailyStats] = useState<DailyStats[]>([])
  const [topClips, setTopClips] = useState<TopClip[]>([])
  const [viralDistribution, setViralDistribution] = useState<Array<{ range: string; count: number }>>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen) {
      loadAnalytics()
    }
  }, [isOpen])

  const loadAnalytics = async () => {
    setLoading(true)
    try {
      const [overviewRes, dailyRes, topClipsRes, viralRes] = await Promise.all([
        analyticsApi.getOverview(),
        analyticsApi.getDaily(7),
        analyticsApi.getTopClips(5),
        analyticsApi.getViralDistribution()
      ])
      setOverview(overviewRes.data)
      setDailyStats(dailyRes.data)
      setTopClips(topClipsRes.data)
      setViralDistribution(viralRes.data)
    } catch (error) {
      console.error('Failed to load analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDuration = (seconds: number) => {
    const m = Math.floor(seconds / 60)
    const s = Math.floor(seconds % 60)
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  if (!isOpen) return null

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
            <BarChart3 className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-semibold">Analytics Dashboard</h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={loadAnalytics}
              disabled={loading}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              title="Refresh"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6 max-h-[calc(90vh-80px)] overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : overview ? (
            <>
              {/* Overview Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                  icon={<Film className="w-5 h-5 text-blue-400" />}
                  label="Total Videos"
                  value={overview.total_videos.toString()}
                  color="blue"
                />
                <StatCard
                  icon={<Scissors className="w-5 h-5 text-purple-400" />}
                  label="Total Clips"
                  value={overview.total_clips.toString()}
                  color="purple"
                />
                <StatCard
                  icon={<Download className="w-5 h-5 text-green-400" />}
                  label="Exported"
                  value={overview.total_exported.toString()}
                  color="green"
                />
                <StatCard
                  icon={<Clock className="w-5 h-5 text-yellow-400" />}
                  label="Hours Processed"
                  value={overview.total_duration_hours.toFixed(1)}
                  color="yellow"
                />
              </div>

              {/* Secondary Stats */}
              <div className="grid grid-cols-3 gap-4">
                <div className="glass-card p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">Avg Viral Score</span>
                    <Zap className="w-4 h-4 text-primary" />
                  </div>
                  <div className="flex items-end gap-2">
                    <span className="text-3xl font-bold text-primary">{overview.avg_viral_score}</span>
                    <span className="text-gray-500 text-sm mb-1">/ 10</span>
                  </div>
                </div>
                <div className="glass-card p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">Success Rate</span>
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  </div>
                  <div className="flex items-end gap-2">
                    <span className="text-3xl font-bold text-green-400">{overview.processing_success_rate}%</span>
                  </div>
                </div>
                <div className="glass-card p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">Total Projects</span>
                    <TrendingUp className="w-4 h-4 text-accent-cyan" />
                  </div>
                  <div className="flex items-end gap-2">
                    <span className="text-3xl font-bold text-accent-cyan">{overview.total_projects}</span>
                  </div>
                </div>
              </div>

              {/* Viral Score Distribution */}
              {viralDistribution.length > 0 && (
                <div className="glass-card p-4">
                  <h3 className="text-sm font-medium mb-4">Viral Score Distribution</h3>
                  <div className="flex items-end gap-2 h-32">
                    {viralDistribution.map((item, i) => {
                      const maxCount = Math.max(...viralDistribution.map(d => d.count))
                      const height = maxCount > 0 ? (item.count / maxCount) * 100 : 0
                      return (
                        <div key={i} className="flex-1 flex flex-col items-center gap-1">
                          <motion.div
                            initial={{ height: 0 }}
                            animate={{ height: `${height}%` }}
                            transition={{ delay: i * 0.1 }}
                            className="w-full bg-gradient-to-t from-primary to-accent-pink rounded-t-lg min-h-[4px]"
                          />
                          <span className="text-[10px] text-gray-500">{item.range}</span>
                          <span className="text-xs font-medium">{item.count}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Daily Activity */}
              {dailyStats.length > 0 && (
                <div className="glass-card p-4">
                  <h3 className="text-sm font-medium mb-4">Last 7 Days Activity</h3>
                  <div className="space-y-2">
                    {dailyStats.slice().reverse().map((day, i) => (
                      <div key={i} className="flex items-center gap-4">
                        <span className="text-xs text-gray-500 w-20">
                          {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                        </span>
                        <div className="flex-1 flex items-center gap-2">
                          <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-blue-500 rounded-full"
                              style={{ width: `${(day.videos_processed / Math.max(...dailyStats.map(d => d.videos_processed || 1))) * 100}%` }}
                            />
                          </div>
                          <span className="text-xs text-gray-400 w-8">{day.videos_processed}v</span>
                        </div>
                        <div className="flex-1 flex items-center gap-2">
                          <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-purple-500 rounded-full"
                              style={{ width: `${(day.clips_generated / Math.max(...dailyStats.map(d => d.clips_generated || 1))) * 100}%` }}
                            />
                          </div>
                          <span className="text-xs text-gray-400 w-8">{day.clips_generated}c</span>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="flex items-center gap-4 mt-3 pt-3 border-t border-white/5">
                    <div className="flex items-center gap-1.5">
                      <div className="w-2 h-2 rounded-full bg-blue-500" />
                      <span className="text-[10px] text-gray-500">Videos</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-2 h-2 rounded-full bg-purple-500" />
                      <span className="text-[10px] text-gray-500">Clips</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Top Clips */}
              {topClips.length > 0 && (
                <div className="glass-card p-4">
                  <h3 className="text-sm font-medium mb-4">Top Performing Clips</h3>
                  <div className="space-y-2">
                    {topClips.map((clip, i) => (
                      <div 
                        key={clip.id}
                        className="flex items-center gap-3 p-2 bg-white/5 rounded-lg"
                      >
                        <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                          i === 0 ? 'bg-yellow-500/20 text-yellow-400' :
                          i === 1 ? 'bg-gray-400/20 text-gray-300' :
                          i === 2 ? 'bg-orange-500/20 text-orange-400' :
                          'bg-white/10 text-gray-400'
                        }`}>
                          {i + 1}
                        </span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm truncate">{clip.title || `Clip ${clip.id}`}</p>
                          <p className="text-[10px] text-gray-500">{formatDuration(clip.duration)}</p>
                        </div>
                        <div className="flex items-center gap-1">
                          <Zap className="w-3.5 h-3.5 text-primary" />
                          <span className="text-sm font-bold text-primary">{clip.viral_score.toFixed(1)}</span>
                        </div>
                        {clip.exported && (
                          <CheckCircle className="w-4 h-4 text-green-400" />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-20 text-gray-500">
              Failed to load analytics data
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  )
}

function StatCard({ 
  icon, 
  label, 
  value, 
  color 
}: { 
  icon: React.ReactNode
  label: string
  value: string
  color: 'blue' | 'purple' | 'green' | 'yellow'
}) {
  const colors = {
    blue: 'from-blue-500/20 to-blue-500/5',
    purple: 'from-purple-500/20 to-purple-500/5',
    green: 'from-green-500/20 to-green-500/5',
    yellow: 'from-yellow-500/20 to-yellow-500/5'
  }

  return (
    <div className={`glass-card p-4 bg-gradient-to-br ${colors[color]}`}>
      <div className="flex items-center justify-between mb-2">
        {icon}
      </div>
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-xs text-gray-400">{label}</p>
    </div>
  )
}
