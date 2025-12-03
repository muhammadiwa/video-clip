'use client'

import { useState, useEffect } from 'react'
import { 
  Wand2, 
  Subtitles, 
  Loader, 
  CheckCircle, 
  AlertCircle,
  Settings,
  Sparkles,
  Zap,
  Clock,
  Ratio,
  Type,
  Save,
  FolderOpen,
  Star,
  Trash2
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { templatesApi } from '@/lib/api'
import type { ProcessingTemplate } from '@/types'

interface ProcessingStep {
  id: string
  label: string
  status: 'pending' | 'running' | 'completed' | 'error'
  progress?: number
  message?: string
}

interface ProcessingPanelProps {
  videoId: number
  onStartProcessing: (options: ProcessingOptions) => void
  isProcessing: boolean
  steps: ProcessingStep[]
}

export interface ProcessingOptions {
  topN: number
  targetPlatform: string
  aspectRatio: string
  burnSubtitles: boolean
  subtitleStyle: string
  minDuration: number
  maxDuration: number
  // Custom AI options
  titleTone: string
  customPrompt: string
  language: string
}

const SUBTITLE_STYLES = [
  { id: 'viral_white', name: 'Viral White', desc: 'White bold with black outline', preview: 'text-white font-bold' },
  { id: 'viral_yellow', name: 'Viral Yellow', desc: 'Yellow Impact style', preview: 'text-yellow-400 font-bold' },
  { id: 'mrbeast', name: 'MrBeast', desc: 'Large Impact font', preview: 'text-white font-black text-lg' },
  { id: 'minimal', name: 'Minimal', desc: 'Clean & subtle', preview: 'text-white/80 font-medium' },
  { id: 'neon', name: 'Neon Glow', desc: 'Glowing neon effect', preview: 'text-cyan-400 font-bold' },
  { id: 'shadow', name: 'Drop Shadow', desc: 'Heavy shadow effect', preview: 'text-white font-bold drop-shadow-lg' },
]

const PLATFORMS = [
  { id: 'shorts', name: 'YouTube Shorts', icon: '📱', aspect: '9:16' },
  { id: 'tiktok', name: 'TikTok', icon: '🎵', aspect: '9:16' },
  { id: 'reels', name: 'Instagram Reels', icon: '📸', aspect: '9:16' },
  { id: 'youtube', name: 'YouTube', icon: '▶️', aspect: '16:9' },
  { id: 'square', name: 'Square', icon: '⬜', aspect: '1:1' },
]

const ASPECT_RATIOS = [
  { id: '9:16', name: 'Portrait', desc: '9:16 (Vertical)', icon: '📱' },
  { id: '16:9', name: 'Landscape', desc: '16:9 (Horizontal)', icon: '🖥️' },
  { id: '1:1', name: 'Square', desc: '1:1 (Square)', icon: '⬜' },
  { id: '4:5', name: 'Instagram', desc: '4:5 (IG Feed)', icon: '📷' },
]

const DURATION_PRESETS = [
  { min: 15, max: 30, label: '15-30s', desc: 'Quick hooks' },
  { min: 30, max: 60, label: '30-60s', desc: 'Standard viral' },
  { min: 45, max: 90, label: '45-90s', desc: 'Extended story' },
  { min: 60, max: 180, label: '1-3min', desc: 'Full content' },
]

const TITLE_TONES = [
  { id: 'engaging', name: 'Engaging', desc: 'Balanced & compelling' },
  { id: 'clickbait', name: 'Clickbait', desc: 'High-impact hooks' },
  { id: 'professional', name: 'Professional', desc: 'Clean & credible' },
  { id: 'casual', name: 'Casual', desc: 'Friendly & relatable' },
  { id: 'formal', name: 'Formal', desc: 'Business appropriate' },
]

const LANGUAGES = [
  { id: 'en', name: 'English' },
  { id: 'id', name: 'Indonesian' },
  { id: 'es', name: 'Spanish' },
  { id: 'pt', name: 'Portuguese' },
  { id: 'fr', name: 'French' },
  { id: 'de', name: 'German' },
  { id: 'ja', name: 'Japanese' },
  { id: 'ko', name: 'Korean' },
  { id: 'zh', name: 'Chinese' },
  { id: 'ar', name: 'Arabic' },
]

export default function ProcessingPanel({
  videoId,
  onStartProcessing,
  isProcessing,
  steps,
}: ProcessingPanelProps) {
  const [showSettings, setShowSettings] = useState(true)
  const [activeSettingsTab, setActiveSettingsTab] = useState<'basic' | 'subtitle' | 'ai' | 'templates' | 'advanced'>('basic')
  const [options, setOptions] = useState<ProcessingOptions>({
    topN: 5,
    targetPlatform: 'shorts',
    aspectRatio: '9:16',
    burnSubtitles: true,
    subtitleStyle: 'viral_white',
    minDuration: 30,
    maxDuration: 60,
    titleTone: 'engaging',
    customPrompt: '',
    language: 'en',
  })
  const [templates, setTemplates] = useState<ProcessingTemplate[]>([])
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null)
  const [showSaveTemplate, setShowSaveTemplate] = useState(false)
  const [newTemplateName, setNewTemplateName] = useState('')
  const [loadingTemplates, setLoadingTemplates] = useState(false)

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    try {
      setLoadingTemplates(true)
      const res = await templatesApi.getAll()
      setTemplates(res.data)
      const defaultTemplate = res.data.find(t => t.is_default)
      if (defaultTemplate) {
        applyTemplate(defaultTemplate)
        setSelectedTemplateId(defaultTemplate.id)
      }
    } catch (error) {
      console.error('Failed to load templates:', error)
    } finally {
      setLoadingTemplates(false)
    }
  }

  const applyTemplate = (template: ProcessingTemplate) => {
    setOptions({
      topN: template.top_n,
      targetPlatform: template.target_platform,
      aspectRatio: template.aspect_ratio,
      burnSubtitles: template.burn_subtitles,
      subtitleStyle: template.subtitle_style,
      minDuration: template.min_duration,
      maxDuration: template.max_duration,
      titleTone: template.settings?.titleTone || 'engaging',
      customPrompt: template.settings?.customPrompt || '',
      language: template.settings?.language || 'en',
    })
    setSelectedTemplateId(template.id)
  }

  const saveTemplate = async () => {
    if (!newTemplateName.trim()) return
    try {
      const res = await templatesApi.create({
        name: newTemplateName,
        top_n: options.topN,
        target_platform: options.targetPlatform,
        aspect_ratio: options.aspectRatio,
        burn_subtitles: options.burnSubtitles,
        subtitle_style: options.subtitleStyle,
        min_duration: options.minDuration,
        max_duration: options.maxDuration,
      })
      setTemplates([...templates, res.data])
      setSelectedTemplateId(res.data.id)
      setNewTemplateName('')
      setShowSaveTemplate(false)
    } catch (error) {
      console.error('Failed to save template:', error)
    }
  }

  const deleteTemplate = async (id: number) => {
    try {
      await templatesApi.delete(id)
      setTemplates(templates.filter(t => t.id !== id))
      if (selectedTemplateId === id) setSelectedTemplateId(null)
    } catch (error) {
      console.error('Failed to delete template:', error)
    }
  }

  const setDefaultTemplate = async (id: number) => {
    try {
      await templatesApi.setDefault(id)
      setTemplates(templates.map(t => ({ ...t, is_default: t.id === id })))
    } catch (error) {
      console.error('Failed to set default template:', error)
    }
  }

  const getStepIcon = (status: ProcessingStep['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'running':
        return <Loader className="w-4 h-4 text-primary animate-spin" />
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400" />
      default:
        return <div className="w-4 h-4 rounded-full border-2 border-gray-600" />
    }
  }

  const totalProgress = steps.length > 0
    ? Math.round(steps.reduce((acc, step) => {
        if (step.status === 'completed') return acc + 100
        if (step.status === 'running') return acc + (step.progress || 0)
        return acc
      }, 0) / steps.length)
    : 0

  const handlePlatformChange = (platformId: string) => {
    const platform = PLATFORMS.find(p => p.id === platformId)
    setOptions({
      ...options,
      targetPlatform: platformId,
      aspectRatio: platform?.aspect || '9:16'
    })
  }

  const handleDurationPreset = (min: number, max: number) => {
    setOptions({ ...options, minDuration: min, maxDuration: max })
  }

  return (
    <div className="glass-card overflow-hidden">
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-primary/10 via-accent-pink/10 to-accent-cyan/10 border-b border-white/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-accent-pink/30 flex items-center justify-center">
              <Zap className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold">AI Clip Generator</h3>
              <p className="text-xs text-gray-400">Configure & generate viral clips</p>
            </div>
          </div>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className={`p-2 rounded-lg transition-all duration-200 ${
              showSettings ? 'bg-white/10 text-white rotate-90' : 'hover:bg-white/5 text-gray-400'
            }`}
          >
            <Settings className="w-5 h-5 transition-transform" />
          </button>
        </div>
      </div>

      <div className="p-4">
        {/* Settings Panel */}
        <AnimatePresence>
          {showSettings && !isProcessing && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              {/* Settings Tabs */}
              <div className="flex gap-1 p-1 bg-white/5 rounded-lg mb-4 overflow-x-auto">
                {[
                  { id: 'basic', label: 'Basic', icon: Wand2 },
                  { id: 'subtitle', label: 'Subs', icon: Type },
                  { id: 'ai', label: 'AI', icon: Sparkles },
                  { id: 'templates', label: 'Presets', icon: FolderOpen },
                  { id: 'advanced', label: 'More', icon: Settings },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveSettingsTab(tab.id as any)}
                    className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-2 rounded-md text-xs font-medium transition-all ${
                      activeSettingsTab === tab.id
                        ? 'bg-primary text-white'
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <tab.icon className="w-3.5 h-3.5" />
                    <span className="hidden sm:inline">{tab.label}</span>
                  </button>
                ))}
              </div>

              {/* Basic Settings */}
              {activeSettingsTab === 'basic' && (
                <div className="space-y-4">
                  {/* Number of clips */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-xs text-gray-400 flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5" />
                        Number of Clips
                      </label>
                      <span className="text-sm font-bold text-primary px-2 py-0.5 bg-primary/10 rounded">
                        {options.topN}
                      </span>
                    </div>
                    <input
                      type="range"
                      min="1"
                      max="20"
                      value={options.topN}
                      onChange={(e) => setOptions({ ...options, topN: parseInt(e.target.value) })}
                      className="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer
                        [&::-webkit-slider-thumb]:appearance-none
                        [&::-webkit-slider-thumb]:w-5
                        [&::-webkit-slider-thumb]:h-5
                        [&::-webkit-slider-thumb]:bg-gradient-to-r
                        [&::-webkit-slider-thumb]:from-primary
                        [&::-webkit-slider-thumb]:to-accent-pink
                        [&::-webkit-slider-thumb]:rounded-full
                        [&::-webkit-slider-thumb]:shadow-lg
                        [&::-webkit-slider-thumb]:cursor-pointer
                        [&::-webkit-slider-thumb]:border-2
                        [&::-webkit-slider-thumb]:border-white/20"
                    />
                    <div className="flex justify-between text-[10px] text-gray-500 mt-1">
                      <span>1</span>
                      <span>10</span>
                      <span>20</span>
                    </div>
                  </div>

                  {/* Platform */}
                  <div>
                    <label className="text-xs text-gray-400 mb-2 block">Target Platform</label>
                    <div className="grid grid-cols-3 gap-2">
                      {PLATFORMS.slice(0, 3).map((platform) => (
                        <button
                          key={platform.id}
                          onClick={() => handlePlatformChange(platform.id)}
                          className={`py-2.5 px-3 text-xs rounded-xl transition-all duration-200 flex flex-col items-center gap-1 ${
                            options.targetPlatform === platform.id
                              ? 'bg-primary/20 text-primary ring-2 ring-primary/50'
                              : 'bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white'
                          }`}
                        >
                          <span className="text-lg">{platform.icon}</span>
                          <span className="font-medium">{platform.name.split(' ')[0]}</span>
                        </button>
                      ))}
                    </div>
                    <div className="grid grid-cols-2 gap-2 mt-2">
                      {PLATFORMS.slice(3).map((platform) => (
                        <button
                          key={platform.id}
                          onClick={() => handlePlatformChange(platform.id)}
                          className={`py-2 px-3 text-xs rounded-xl transition-all duration-200 flex items-center justify-center gap-2 ${
                            options.targetPlatform === platform.id
                              ? 'bg-primary/20 text-primary ring-2 ring-primary/50'
                              : 'bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white'
                          }`}
                        >
                          <span>{platform.icon}</span>
                          <span className="font-medium">{platform.name}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Aspect Ratio */}
                  <div>
                    <label className="text-xs text-gray-400 mb-2 flex items-center gap-1.5">
                      <Ratio className="w-3.5 h-3.5" />
                      Aspect Ratio
                    </label>
                    <div className="grid grid-cols-4 gap-2">
                      {ASPECT_RATIOS.map((ratio) => (
                        <button
                          key={ratio.id}
                          onClick={() => setOptions({ ...options, aspectRatio: ratio.id })}
                          className={`py-2 px-2 text-xs rounded-lg transition-all duration-200 flex flex-col items-center gap-1 ${
                            options.aspectRatio === ratio.id
                              ? 'bg-accent-cyan/20 text-accent-cyan ring-1 ring-accent-cyan/50'
                              : 'bg-white/5 hover:bg-white/10 text-gray-400'
                          }`}
                        >
                          <span>{ratio.icon}</span>
                          <span className="font-medium">{ratio.id}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Duration Range */}
                  <div>
                    <label className="text-xs text-gray-400 mb-2 flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5" />
                      Clip Duration
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      {DURATION_PRESETS.map((preset) => (
                        <button
                          key={preset.label}
                          onClick={() => handleDurationPreset(preset.min, preset.max)}
                          className={`py-2.5 px-3 text-xs rounded-lg transition-all duration-200 text-left ${
                            options.minDuration === preset.min && options.maxDuration === preset.max
                              ? 'bg-accent-pink/20 text-accent-pink ring-1 ring-accent-pink/50'
                              : 'bg-white/5 hover:bg-white/10 text-gray-400'
                          }`}
                        >
                          <div className="font-bold">{preset.label}</div>
                          <div className="text-[10px] opacity-70">{preset.desc}</div>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Subtitle Settings */}
              {activeSettingsTab === 'subtitle' && (
                <div className="space-y-4">
                  {/* Toggle */}
                  <button
                    onClick={() => setOptions({ ...options, burnSubtitles: !options.burnSubtitles })}
                    className={`w-full flex items-center justify-between p-3 rounded-xl transition-all duration-200 ${
                      options.burnSubtitles 
                        ? 'bg-accent-cyan/10 ring-1 ring-accent-cyan/30' 
                        : 'bg-white/5'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Subtitles className={`w-5 h-5 ${options.burnSubtitles ? 'text-accent-cyan' : 'text-gray-400'}`} />
                      <div className="text-left">
                        <p className="text-sm font-medium">Burn Subtitles</p>
                        <p className="text-[10px] text-gray-400">Embed captions into video</p>
                      </div>
                    </div>
                    <div className={`w-10 h-6 rounded-full transition-colors duration-200 ${
                      options.burnSubtitles ? 'bg-accent-cyan' : 'bg-gray-600'
                    }`}>
                      <div className={`w-5 h-5 mt-0.5 rounded-full bg-white transition-transform duration-200 shadow-lg ${
                        options.burnSubtitles ? 'translate-x-4.5 ml-0.5' : 'translate-x-0.5'
                      }`} />
                    </div>
                  </button>

                  {/* Style selector */}
                  {options.burnSubtitles && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="space-y-2"
                    >
                      <label className="text-xs text-gray-400">Subtitle Style</label>
                      <div className="grid grid-cols-2 gap-2">
                        {SUBTITLE_STYLES.map((style) => (
                          <button
                            key={style.id}
                            onClick={() => setOptions({ ...options, subtitleStyle: style.id })}
                            className={`p-3 text-left rounded-xl transition-all duration-200 ${
                              options.subtitleStyle === style.id
                                ? 'bg-primary/15 ring-2 ring-primary/50'
                                : 'bg-white/5 hover:bg-white/10'
                            }`}
                          >
                            <div className={`text-sm mb-1 ${style.preview}`}>Aa</div>
                            <p className="text-xs font-medium">{style.name}</p>
                            <p className="text-[10px] text-gray-500">{style.desc}</p>
                          </button>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </div>
              )}

              {/* AI Settings Tab */}
              {activeSettingsTab === 'ai' && (
                <div className="space-y-4">
                  {/* Title Tone */}
                  <div>
                    <label className="text-xs text-gray-400 mb-2 block">Title & Description Tone</label>
                    <div className="grid grid-cols-2 gap-2">
                      {TITLE_TONES.map((tone) => (
                        <button
                          key={tone.id}
                          onClick={() => setOptions({ ...options, titleTone: tone.id })}
                          className={`p-2.5 text-left rounded-lg transition-all ${
                            options.titleTone === tone.id
                              ? 'bg-primary/20 ring-1 ring-primary/50'
                              : 'bg-white/5 hover:bg-white/10'
                          }`}
                        >
                          <p className="text-xs font-medium">{tone.name}</p>
                          <p className="text-[10px] text-gray-500">{tone.desc}</p>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Output Language */}
                  <div>
                    <label className="text-xs text-gray-400 mb-2 block">Output Language</label>
                    <select
                      value={options.language}
                      onChange={(e) => setOptions({ ...options, language: e.target.value })}
                      className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm focus:outline-none focus:border-primary"
                    >
                      {LANGUAGES.map((lang) => (
                        <option key={lang.id} value={lang.id} className="bg-dark-surface">
                          {lang.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Custom Prompt */}
                  <div>
                    <label className="text-xs text-gray-400 mb-2 block">Custom Prompt (Optional)</label>
                    <textarea
                      value={options.customPrompt}
                      onChange={(e) => setOptions({ ...options, customPrompt: e.target.value })}
                      placeholder="Add specific instructions for AI title/description generation..."
                      rows={3}
                      className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm focus:outline-none focus:border-primary resize-none"
                    />
                    <p className="text-[10px] text-gray-500 mt-1">
                      E.g., "Focus on educational value" or "Include call-to-action"
                    </p>
                  </div>
                </div>
              )}

              {/* Templates Tab */}
              {activeSettingsTab === 'templates' && (
                <div className="space-y-4">
                  {/* Save Current Settings */}
                  {showSaveTemplate ? (
                    <div className="p-3 bg-white/5 rounded-xl space-y-2">
                      <input
                        type="text"
                        value={newTemplateName}
                        onChange={(e) => setNewTemplateName(e.target.value)}
                        placeholder="Template name..."
                        className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm focus:outline-none focus:border-primary"
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={saveTemplate}
                          disabled={!newTemplateName.trim()}
                          className="flex-1 py-2 bg-primary/20 hover:bg-primary/30 text-primary rounded-lg text-xs font-medium disabled:opacity-50"
                        >
                          Save
                        </button>
                        <button
                          onClick={() => setShowSaveTemplate(false)}
                          className="flex-1 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-xs"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => setShowSaveTemplate(true)}
                      className="w-full flex items-center justify-center gap-2 p-3 bg-white/5 hover:bg-white/10 rounded-xl transition-colors"
                    >
                      <Save className="w-4 h-4 text-primary" />
                      <span className="text-sm font-medium">Save Current Settings as Template</span>
                    </button>
                  )}

                  {/* Template List */}
                  {loadingTemplates ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader className="w-5 h-5 animate-spin text-primary" />
                    </div>
                  ) : templates.length === 0 ? (
                    <div className="text-center py-8 text-gray-500 text-sm">
                      No templates saved yet
                    </div>
                  ) : (
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {templates.map((template) => (
                        <div
                          key={template.id}
                          className={`p-3 rounded-xl transition-all cursor-pointer ${
                            selectedTemplateId === template.id
                              ? 'bg-primary/20 ring-1 ring-primary/50'
                              : 'bg-white/5 hover:bg-white/10'
                          }`}
                          onClick={() => applyTemplate(template)}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              {template.is_default && (
                                <Star className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400" />
                              )}
                              <span className="text-sm font-medium">{template.name}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <button
                                onClick={(e) => { e.stopPropagation(); setDefaultTemplate(template.id); }}
                                className={`p-1.5 rounded-lg transition-colors ${
                                  template.is_default ? 'text-yellow-400' : 'text-gray-500 hover:text-yellow-400'
                                }`}
                                title="Set as default"
                              >
                                <Star className="w-3.5 h-3.5" />
                              </button>
                              <button
                                onClick={(e) => { e.stopPropagation(); deleteTemplate(template.id); }}
                                className="p-1.5 text-gray-500 hover:text-red-400 rounded-lg transition-colors"
                                title="Delete"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </div>
                          <div className="flex gap-2 mt-1.5 text-[10px] text-gray-500">
                            <span>{template.target_platform}</span>
                            <span>{template.aspect_ratio}</span>
                            <span>{template.min_duration}-{template.max_duration}s</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Advanced Settings */}
              {activeSettingsTab === 'advanced' && (
                <div className="space-y-4">
                  <div className="p-4 bg-white/5 rounded-xl">
                    <h4 className="text-sm font-medium mb-2">AI Detection Mode</h4>
                    <p className="text-xs text-gray-400 mb-3">
                      Uses GPT-4 Vision to analyze frames and detect viral-worthy moments based on visual engagement, emotional impact, and hook potential.
                    </p>
                    <div className="flex items-center gap-2 text-xs text-green-400">
                      <CheckCircle className="w-4 h-4" />
                      AI Detection Active
                    </div>
                  </div>

                  <div className="p-4 bg-white/5 rounded-xl">
                    <h4 className="text-sm font-medium mb-2">Processing Info</h4>
                    <div className="space-y-2 text-xs text-gray-400">
                      <div className="flex justify-between">
                        <span>Transcription</span>
                        <span className="text-white">Whisper Base</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Scene Detection</span>
                        <span className="text-white">Smart Keyframe</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Export Format</span>
                        <span className="text-white">H.264 MP4</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="border-t border-white/5 mt-4 pt-4" />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Processing Steps */}
        {steps.length > 0 && (
          <div className="mb-4">
            {/* Overall progress */}
            <div className="mb-3">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs text-gray-400">Overall Progress</span>
                <span className="text-sm font-bold text-primary">{totalProgress}%</span>
              </div>
              <div className="h-2.5 bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-primary via-accent-pink to-accent-cyan rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${totalProgress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            </div>

            {/* Step list */}
            <div className="space-y-2">
              {steps.map((step, index) => (
                <motion.div 
                  key={step.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`flex items-center gap-3 p-3 rounded-xl transition-colors ${
                    step.status === 'running' ? 'bg-primary/10' : 'bg-white/[0.02]'
                  }`}
                >
                  {getStepIcon(step.status)}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className={`text-sm font-medium ${
                        step.status === 'running' ? 'text-white' : 
                        step.status === 'completed' ? 'text-green-400' :
                        step.status === 'error' ? 'text-red-400' : 'text-gray-400'
                      }`}>
                        {step.label}
                      </p>
                      {step.status === 'running' && step.progress !== undefined && (
                        <span className="text-xs text-primary font-bold">{step.progress}%</span>
                      )}
                    </div>
                    {step.message && step.status === 'running' && (
                      <p className="text-[10px] text-gray-500 truncate mt-0.5">{step.message}</p>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Start Button */}
        <button
          onClick={() => onStartProcessing(options)}
          disabled={isProcessing}
          className={`w-full py-3.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-all duration-300 ${
            isProcessing
              ? 'bg-white/5 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-primary via-accent-pink to-accent-cyan text-white shadow-lg shadow-primary/30 hover:shadow-primary/50 hover:scale-[1.02] active:scale-[0.98]'
          }`}
        >
          {isProcessing ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              Generate {options.topN} Viral Clips
            </>
          )}
        </button>

        {!isProcessing && steps.length === 0 && (
          <p className="text-[10px] text-gray-500 text-center mt-3 leading-relaxed">
            AI detects scenes, analyzes viral potential, generates titles & descriptions, and exports clips with subtitles
          </p>
        )}
      </div>
    </div>
  )
}
