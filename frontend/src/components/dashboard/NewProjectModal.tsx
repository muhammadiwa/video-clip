'use client'

import { useState } from 'react'
import { X, Upload, Link as LinkIcon } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { projectsApi } from '@/lib/api'

interface NewProjectModalProps {
  onClose: () => void
  onSuccess: (project: any) => void
}

export default function NewProjectModal({ onClose, onSuccess }: NewProjectModalProps) {
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    source_type: 'upload' as 'upload' | 'youtube',
    source_language: 'en',
    target_platform: 'shorts' as 'shorts' | 'reels' | 'tiktok',
    target_duration: 60,
    aspect_ratio: '9:16',
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    setLoading(true)
    try {
      const response = await projectsApi.create(formData)
      onSuccess(response.data)
    } catch (error) {
      console.error('Error creating project:', error)
      alert('Failed to create project')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        />
        
        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          className="relative glass-card p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Create New Project</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
          
          {/* Form */}
          <div className="space-y-6">
            {/* Project Name */}
            <div>
              <label className="block text-sm font-medium mb-2">Project Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="My Viral Video Project"
                className="w-full px-4 py-3 bg-dark-lighter border border-dark-border rounded-lg focus:outline-none focus:border-primary"
              />
            </div>
            
            {/* Description */}
            <div>
              <label className="block text-sm font-medium mb-2">Description (optional)</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Brief description of your project"
                rows={3}
                className="w-full px-4 py-3 bg-dark-lighter border border-dark-border rounded-lg focus:outline-none focus:border-primary"
              />
            </div>
            
            {/* Source Type */}
            <div>
              <label className="block text-sm font-medium mb-2">Video Source</label>
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => setFormData({ ...formData, source_type: 'upload' })}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    formData.source_type === 'upload'
                      ? 'border-primary bg-primary/10'
                      : 'border-dark-border hover:border-primary/50'
                  }`}
                >
                  <Upload className="w-8 h-8 mx-auto mb-2" />
                  <div className="font-medium">Upload File</div>
                </button>
                
                <button
                  onClick={() => setFormData({ ...formData, source_type: 'youtube' })}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    formData.source_type === 'youtube'
                      ? 'border-primary bg-primary/10'
                      : 'border-dark-border hover:border-primary/50'
                  }`}
                >
                  <LinkIcon className="w-8 h-8 mx-auto mb-2" />
                  <div className="font-medium">YouTube Link</div>
                </button>
              </div>
            </div>
            
            {/* Target Platform */}
            <div>
              <label className="block text-sm font-medium mb-2">Target Platform</label>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { value: 'shorts', label: 'YouTube Shorts' },
                  { value: 'reels', label: 'Instagram Reels' },
                  { value: 'tiktok', label: 'TikTok' },
                ].map((platform) => (
                  <button
                    key={platform.value}
                    onClick={() => setFormData({ ...formData, target_platform: platform.value as any })}
                    className={`p-3 rounded-lg border-2 transition-all text-sm ${
                      formData.target_platform === platform.value
                        ? 'border-primary bg-primary/10'
                        : 'border-dark-border hover:border-primary/50'
                    }`}
                  >
                    {platform.label}
                  </button>
                ))}
              </div>
            </div>
            
            {/* Duration */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Target Duration: {formData.target_duration}s
              </label>
              <input
                type="range"
                min="15"
                max="90"
                step="15"
                value={formData.target_duration}
                onChange={(e) => setFormData({ ...formData, target_duration: parseInt(e.target.value) })}
                className="w-full accent-primary"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>15s</span>
                <span>30s</span>
                <span>60s</span>
                <span>90s</span>
              </div>
            </div>
          </div>
          
          {/* Actions */}
          <div className="flex gap-4 mt-8">
            <button
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-dark-border rounded-lg hover:bg-white/5 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={!formData.name || loading}
              className="flex-1 glass-button glow-effect disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : 'Create Project'}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
