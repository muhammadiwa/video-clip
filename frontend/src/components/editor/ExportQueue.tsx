'use client'

import { useState, useEffect, useCallback } from 'react'
import { 
  Download, 
  Loader, 
  CheckCircle, 
  AlertCircle, 
  X, 
  Bell,
  BellOff,
  Trash2,
  ChevronDown,
  ChevronUp,
  Play,
  Pause,
  RefreshCw
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { processingApi, clipsApi } from '@/lib/api'
import { useNotifications } from '@/hooks/useNotifications'
import type { Clip } from '@/types'

export interface ExportJob {
  id: string
  clipId: number
  clipName: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  progress: number
  jobId?: string
  error?: string
  exportPath?: string
  startedAt?: Date
  completedAt?: Date
}

interface ExportQueueProps {
  projectId: number
  clips: Clip[]
  onExportComplete?: (clipId: number, exportPath: string) => void
}

export default function ExportQueue({ projectId, clips, onExportComplete }: ExportQueueProps) {
  const [queue, setQueue] = useState<ExportJob[]>([])
  const [isExpanded, setIsExpanded] = useState(true)
  const [isPaused, setIsPaused] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  
  const { 
    supported: notificationsSupported, 
    permission, 
    requestPermission, 
    notifyExportComplete 
  } = useNotifications()

  // Process queue
  useEffect(() => {
    if (isPaused || isProcessing) return

    const nextJob = queue.find(job => job.status === 'queued')
    if (!nextJob) return

    processJob(nextJob)
  }, [queue, isPaused, isProcessing])

  const processJob = async (job: ExportJob) => {
    setIsProcessing(true)
    
    // Update job status to processing
    setQueue(prev => prev.map(j => 
      j.id === job.id ? { ...j, status: 'processing' as const, startedAt: new Date() } : j
    ))

    try {
      // Start export
      const response = await processingApi.exportClip(job.clipId)
      const jobId = response.data.job_id

      // Update with job ID
      setQueue(prev => prev.map(j => 
        j.id === job.id ? { ...j, jobId } : j
      ))

      // Poll for completion
      await pollJobStatus(job.id, jobId)
    } catch (error: any) {
      setQueue(prev => prev.map(j => 
        j.id === job.id ? { 
          ...j, 
          status: 'failed' as const, 
          error: error.message || 'Export failed',
          completedAt: new Date()
        } : j
      ))
    } finally {
      setIsProcessing(false)
    }
  }

  const pollJobStatus = async (queueId: string, jobId: string) => {
    const poll = async (): Promise<void> => {
      try {
        const res = await processingApi.getJobStatus(jobId)
        const { status, progress, result, error } = res.data

        if (status === 'SUCCESS') {
          setQueue(prev => prev.map(j => 
            j.id === queueId ? { 
              ...j, 
              status: 'completed' as const, 
              progress: 100,
              exportPath: result?.export_path,
              completedAt: new Date()
            } : j
          ))

          // Notify
          const job = queue.find(j => j.id === queueId)
          if (job) {
            notifyExportComplete(job.clipName)
            onExportComplete?.(job.clipId, result?.export_path)
          }
          return
        } 
        
        if (status === 'FAILURE') {
          setQueue(prev => prev.map(j => 
            j.id === queueId ? { 
              ...j, 
              status: 'failed' as const, 
              error: error?.error || 'Export failed',
              completedAt: new Date()
            } : j
          ))
          return
        }

        // Update progress
        if (progress) {
          setQueue(prev => prev.map(j => 
            j.id === queueId ? { ...j, progress: progress.current || 0 } : j
          ))
        }

        // Continue polling
        await new Promise(resolve => setTimeout(resolve, 1500))
        return poll()
      } catch (error) {
        console.error('Poll error:', error)
        throw error
      }
    }

    return poll()
  }

  const addToQueue = useCallback((clip: Clip) => {
    const newJob: ExportJob = {
      id: `export-${clip.id}-${Date.now()}`,
      clipId: clip.id,
      clipName: clip.title || clip.name || `Clip ${clip.id}`,
      status: 'queued',
      progress: 0
    }
    setQueue(prev => [...prev, newJob])
  }, [])

  const addAllToQueue = useCallback(() => {
    const unexportedClips = clips.filter(c => !c.exported)
    unexportedClips.forEach(clip => addToQueue(clip))
  }, [clips, addToQueue])

  const removeFromQueue = (id: string) => {
    setQueue(prev => prev.filter(j => j.id !== id))
  }

  const retryJob = (job: ExportJob) => {
    setQueue(prev => prev.map(j => 
      j.id === job.id ? { ...j, status: 'queued' as const, progress: 0, error: undefined } : j
    ))
  }

  const clearCompleted = () => {
    setQueue(prev => prev.filter(j => j.status !== 'completed'))
  }

  const clearAll = () => {
    setQueue(prev => prev.filter(j => j.status === 'processing'))
  }

  const queuedCount = queue.filter(j => j.status === 'queued').length
  const processingCount = queue.filter(j => j.status === 'processing').length
  const completedCount = queue.filter(j => j.status === 'completed').length
  const failedCount = queue.filter(j => j.status === 'failed').length

  if (queue.length === 0) {
    return (
      <div className="glass-card p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Download className="w-5 h-5 text-primary" />
            <h3 className="font-semibold text-sm">Export Queue</h3>
          </div>
          {notificationsSupported && permission !== 'granted' && (
            <button
              onClick={requestPermission}
              className="text-xs text-gray-400 hover:text-white flex items-center gap-1"
            >
              <Bell className="w-3.5 h-3.5" />
              Enable notifications
            </button>
          )}
        </div>
        
        <div className="text-center py-6">
          <Download className="w-8 h-8 mx-auto mb-2 text-gray-600" />
          <p className="text-sm text-gray-500 mb-3">No exports in queue</p>
          {clips.filter(c => !c.exported).length > 0 && (
            <button
              onClick={addAllToQueue}
              className="px-4 py-2 bg-primary/20 hover:bg-primary/30 text-primary rounded-lg text-sm font-medium transition-colors"
            >
              Export All Clips ({clips.filter(c => !c.exported).length})
            </button>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="glass-card overflow-hidden">
      {/* Header */}
      <div 
        className="p-4 bg-gradient-to-r from-primary/10 to-accent-cyan/10 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Download className="w-5 h-5 text-primary" />
            <h3 className="font-semibold text-sm">Export Queue</h3>
            <span className="text-xs px-2 py-0.5 bg-white/10 rounded-full">
              {queue.length}
            </span>
          </div>
          <div className="flex items-center gap-2">
            {/* Status indicators */}
            {processingCount > 0 && (
              <span className="flex items-center gap-1 text-xs text-yellow-400">
                <Loader className="w-3 h-3 animate-spin" />
                {processingCount}
              </span>
            )}
            {completedCount > 0 && (
              <span className="flex items-center gap-1 text-xs text-green-400">
                <CheckCircle className="w-3 h-3" />
                {completedCount}
              </span>
            )}
            {failedCount > 0 && (
              <span className="flex items-center gap-1 text-xs text-red-400">
                <AlertCircle className="w-3 h-3" />
                {failedCount}
              </span>
            )}
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </div>
        </div>

        {/* Progress bar */}
        {processingCount > 0 && (
          <div className="mt-2 h-1.5 bg-white/10 rounded-full overflow-hidden">
            <motion.div 
              className="h-full bg-gradient-to-r from-primary to-accent-cyan"
              initial={{ width: 0 }}
              animate={{ 
                width: `${queue.find(j => j.status === 'processing')?.progress || 0}%` 
              }}
            />
          </div>
        )}
      </div>

      {/* Queue List */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: 'auto' }}
            exit={{ height: 0 }}
            className="overflow-hidden"
          >
            {/* Controls */}
            <div className="px-4 py-2 border-b border-white/5 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setIsPaused(!isPaused)}
                  className={`p-1.5 rounded-lg transition-colors ${
                    isPaused ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                  }`}
                  title={isPaused ? 'Resume' : 'Pause'}
                >
                  {isPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
                </button>
                {notificationsSupported && (
                  <button
                    onClick={requestPermission}
                    className={`p-1.5 rounded-lg transition-colors ${
                      permission === 'granted' ? 'text-green-400' : 'text-gray-500 hover:text-white'
                    }`}
                    title={permission === 'granted' ? 'Notifications enabled' : 'Enable notifications'}
                  >
                    {permission === 'granted' ? <Bell className="w-3.5 h-3.5" /> : <BellOff className="w-3.5 h-3.5" />}
                  </button>
                )}
              </div>
              <div className="flex items-center gap-1">
                {completedCount > 0 && (
                  <button
                    onClick={clearCompleted}
                    className="text-xs text-gray-400 hover:text-white px-2 py-1"
                  >
                    Clear done
                  </button>
                )}
                <button
                  onClick={clearAll}
                  className="text-xs text-red-400 hover:text-red-300 px-2 py-1"
                >
                  Clear all
                </button>
              </div>
            </div>

            {/* Job list */}
            <div className="max-h-64 overflow-y-auto">
              {queue.map((job, index) => (
                <motion.div
                  key={job.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`px-4 py-3 border-b border-white/5 last:border-0 ${
                    job.status === 'processing' ? 'bg-primary/5' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 min-w-0">
                      {job.status === 'queued' && (
                        <div className="w-4 h-4 rounded-full border-2 border-gray-500" />
                      )}
                      {job.status === 'processing' && (
                        <Loader className="w-4 h-4 text-primary animate-spin" />
                      )}
                      {job.status === 'completed' && (
                        <CheckCircle className="w-4 h-4 text-green-400" />
                      )}
                      {job.status === 'failed' && (
                        <AlertCircle className="w-4 h-4 text-red-400" />
                      )}
                      <span className="text-sm truncate">{job.clipName}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      {job.status === 'processing' && (
                        <span className="text-xs text-primary font-mono">{job.progress}%</span>
                      )}
                      {job.status === 'failed' && (
                        <button
                          onClick={() => retryJob(job)}
                          className="p-1 hover:bg-white/10 rounded text-gray-400 hover:text-white"
                          title="Retry"
                        >
                          <RefreshCw className="w-3.5 h-3.5" />
                        </button>
                      )}
                      {job.status !== 'processing' && (
                        <button
                          onClick={() => removeFromQueue(job.id)}
                          className="p-1 hover:bg-white/10 rounded text-gray-400 hover:text-red-400"
                          title="Remove"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  </div>
                  {job.status === 'failed' && job.error && (
                    <p className="text-xs text-red-400 mt-1 truncate">{job.error}</p>
                  )}
                  {job.status === 'processing' && (
                    <div className="mt-2 h-1 bg-white/10 rounded-full overflow-hidden">
                      <motion.div 
                        className="h-full bg-primary"
                        animate={{ width: `${job.progress}%` }}
                      />
                    </div>
                  )}
                </motion.div>
              ))}
            </div>

            {/* Add more button */}
            {clips.filter(c => !c.exported && !queue.find(j => j.clipId === c.id)).length > 0 && (
              <div className="p-3 border-t border-white/5">
                <button
                  onClick={addAllToQueue}
                  className="w-full py-2 text-xs text-primary hover:bg-primary/10 rounded-lg transition-colors"
                >
                  Add remaining clips to queue
                </button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export { useNotifications }
