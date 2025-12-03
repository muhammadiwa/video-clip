'use client'

import { useState, useEffect } from 'react'
import { 
  HardDrive, 
  Trash2, 
  RefreshCw, 
  Loader, 
  AlertCircle,
  CheckCircle,
  Database,
  Film,
  Scissors,
  FolderOpen,
  X
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { storageApi, StorageStats, CleanupResult } from '@/lib/api'

interface StorageManagerProps {
  isOpen: boolean
  onClose: () => void
}

export default function StorageManager({ isOpen, onClose }: StorageManagerProps) {
  const [stats, setStats] = useState<StorageStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [cleaning, setCleaning] = useState<string | null>(null)
  const [result, setResult] = useState<CleanupResult | null>(null)

  useEffect(() => {
    if (isOpen) {
      loadStats()
    }
  }, [isOpen])

  const loadStats = async () => {
    setLoading(true)
    try {
      const res = await storageApi.getStats()
      setStats(res.data)
    } catch (error) {
      console.error('Failed to load storage stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCleanupTemp = async () => {
    setCleaning('temp')
    setResult(null)
    try {
      const res = await storageApi.cleanupTemp(24)
      setResult(res.data)
      loadStats()
    } catch (error) {
      console.error('Cleanup failed:', error)
    } finally {
      setCleaning(null)
    }
  }

  const handleCleanupOrphaned = async () => {
    setCleaning('orphaned')
    setResult(null)
    try {
      const res = await storageApi.cleanupOrphaned()
      setResult(res.data)
      loadStats()
    } catch (error) {
      console.error('Cleanup failed:', error)
    } finally {
      setCleaning(null)
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`
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
        className="bg-dark-surface rounded-2xl w-full max-w-lg max-h-[85vh] overflow-hidden shadow-2xl"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <HardDrive className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-semibold">Storage Manager</h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={loadStats}
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

        <div className="p-4 space-y-4 max-h-[calc(85vh-80px)] overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : stats ? (
            <>
              {/* Storage Overview */}
              <div className="glass-card p-4">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm text-gray-400">Total Storage Used</span>
                  <span className="text-2xl font-bold text-primary">{stats.total_size_formatted}</span>
                </div>
                
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="flex items-center gap-2 text-gray-400">
                      <Database className="w-4 h-4" />
                      Uploads
                    </span>
                    <span>{formatBytes(stats.uploads_size)}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="flex items-center gap-2 text-gray-400">
                      <FolderOpen className="w-4 h-4" />
                      Temp Files
                    </span>
                    <span>{formatBytes(stats.temp_size)}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="flex items-center gap-2 text-gray-400">
                      <Film className="w-4 h-4" />
                      Exports
                    </span>
                    <span>{formatBytes(stats.exports_size)}</span>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="mt-4">
                  <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-primary to-accent-pink"
                      style={{ 
                        width: `${Math.min(100, (stats.total_size_bytes / (10 * 1024 * 1024 * 1024)) * 100)}%` 
                      }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1 text-right">
                    Estimated 10GB limit
                  </p>
                </div>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-3 gap-3">
                <div className="glass-card p-3 text-center">
                  <FolderOpen className="w-5 h-5 mx-auto mb-1 text-primary" />
                  <p className="text-2xl font-bold">{stats.projects_count}</p>
                  <p className="text-xs text-gray-500">Projects</p>
                </div>
                <div className="glass-card p-3 text-center">
                  <Film className="w-5 h-5 mx-auto mb-1 text-accent-cyan" />
                  <p className="text-2xl font-bold">{stats.videos_count}</p>
                  <p className="text-xs text-gray-500">Videos</p>
                </div>
                <div className="glass-card p-3 text-center">
                  <Scissors className="w-5 h-5 mx-auto mb-1 text-accent-pink" />
                  <p className="text-2xl font-bold">{stats.clips_count}</p>
                  <p className="text-xs text-gray-500">Clips</p>
                </div>
              </div>

              {/* Cleanup Actions */}
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-gray-400">Cleanup Options</h3>
                
                <button
                  onClick={handleCleanupTemp}
                  disabled={!!cleaning}
                  className="w-full flex items-center justify-between p-3 bg-white/5 hover:bg-white/10 rounded-xl transition-colors disabled:opacity-50"
                >
                  <div className="flex items-center gap-3">
                    <Trash2 className="w-5 h-5 text-yellow-500" />
                    <div className="text-left">
                      <p className="text-sm font-medium">Clean Temp Files</p>
                      <p className="text-xs text-gray-500">Remove files older than 24 hours</p>
                    </div>
                  </div>
                  {cleaning === 'temp' ? (
                    <Loader className="w-4 h-4 animate-spin" />
                  ) : (
                    <span className="text-xs text-gray-400">Run</span>
                  )}
                </button>

                <button
                  onClick={handleCleanupOrphaned}
                  disabled={!!cleaning}
                  className="w-full flex items-center justify-between p-3 bg-white/5 hover:bg-white/10 rounded-xl transition-colors disabled:opacity-50"
                >
                  <div className="flex items-center gap-3">
                    <AlertCircle className="w-5 h-5 text-red-500" />
                    <div className="text-left">
                      <p className="text-sm font-medium">Clean Orphaned Files</p>
                      <p className="text-xs text-gray-500">Remove files not in database</p>
                    </div>
                  </div>
                  {cleaning === 'orphaned' ? (
                    <Loader className="w-4 h-4 animate-spin" />
                  ) : (
                    <span className="text-xs text-gray-400">Run</span>
                  )}
                </button>
              </div>

              {/* Cleanup Result */}
              <AnimatePresence>
                {result && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className={`p-4 rounded-xl ${
                      result.errors.length > 0 
                        ? 'bg-yellow-500/10 border border-yellow-500/30' 
                        : 'bg-green-500/10 border border-green-500/30'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle className={`w-4 h-4 ${
                        result.errors.length > 0 ? 'text-yellow-400' : 'text-green-400'
                      }`} />
                      <span className="text-sm font-medium">Cleanup Complete</span>
                    </div>
                    <div className="text-sm text-gray-400">
                      <p>Files deleted: {result.files_deleted}</p>
                      <p>Space freed: {result.space_freed_formatted}</p>
                    </div>
                    {result.errors.length > 0 && (
                      <div className="mt-2 text-xs text-yellow-400">
                        {result.errors.length} error(s) occurred
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </>
          ) : (
            <div className="text-center py-12 text-gray-500">
              Failed to load storage stats
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  )
}
