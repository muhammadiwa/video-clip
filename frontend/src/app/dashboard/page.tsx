'use client'

import { useState, useEffect } from 'react'
import { Plus, FolderOpen, Clock, CheckCircle, Loader, RefreshCw, HardDrive, BarChart3 } from 'lucide-react'
import { motion } from 'framer-motion'
import NewProjectModal from '@/components/dashboard/NewProjectModal'
import ProjectCard from '@/components/dashboard/ProjectCard'
import ThemeToggle from '@/components/ThemeToggle'
import StorageManager from '@/components/StorageManager'
import AnalyticsDashboard from '@/components/AnalyticsDashboard'
import { projectsApi } from '@/lib/api'
import type { Project } from '@/types'

export default function Dashboard() {
  const [showNewProjectModal, setShowNewProjectModal] = useState(false)
  const [showStorageManager, setShowStorageManager] = useState(false)
  const [showAnalytics, setShowAnalytics] = useState(false)
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const loadProjects = async () => {
    try {
      const res = await projectsApi.getAll()
      setProjects(res.data)
    } catch (error) {
      console.error('Failed to load projects:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadProjects()
  }, [])

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-dark-border">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold gradient-text">Viral Clip AI</h1>
            
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowAnalytics(true)}
                className="p-2.5 hover:bg-white/10 rounded-lg transition-colors"
                title="Analytics"
              >
                <BarChart3 className="w-5 h-5" />
              </button>
              <button
                onClick={() => setShowStorageManager(true)}
                className="p-2.5 hover:bg-white/10 rounded-lg transition-colors"
                title="Storage Manager"
              >
                <HardDrive className="w-5 h-5" />
              </button>
              <ThemeToggle />
              <button
                onClick={() => setShowNewProjectModal(true)}
                className="glass-button glow-effect flex items-center gap-2"
              >
                <Plus className="w-5 h-5" />
                New Project
              </button>
            </div>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {[
            { label: 'Total Projects', value: projects.length.toString(), icon: FolderOpen, color: 'text-primary' },
            { label: 'Processing', value: projects.filter(p => p.status === 'processing').length.toString(), icon: Loader, color: 'text-accent-cyan' },
            { label: 'Ready', value: projects.filter(p => p.status === 'ready').length.toString(), icon: Clock, color: 'text-yellow-500' },
            { label: 'Completed', value: projects.filter(p => p.status === 'edited').length.toString(), icon: CheckCircle, color: 'text-green-500' },
          ].map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass-card p-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
                  <p className="text-3xl font-bold">{stat.value}</p>
                </div>
                <stat.icon className={`w-10 h-10 ${stat.color}`} />
              </div>
            </motion.div>
          ))}
        </div>
        
        {/* Projects Grid */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Your Projects</h2>
            <button
              onClick={loadProjects}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              title="Refresh"
            >
              <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
          
          {isLoading ? (
            <div className="glass-card p-12 text-center">
              <Loader className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
              <p className="text-gray-400">Loading projects...</p>
            </div>
          ) : projects.length === 0 ? (
            <div className="glass-card p-12 text-center">
              <FolderOpen className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">No projects yet</h3>
              <p className="text-gray-400 mb-6">Create your first project to get started</p>
              <button
                onClick={() => setShowNewProjectModal(true)}
                className="glass-button glow-effect flex items-center gap-2 mx-auto"
              >
                <Plus className="w-5 h-5" />
                Create Project
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map((project) => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </div>
          )}
        </div>
      </main>
      
      {/* New Project Modal */}
      {showNewProjectModal && (
        <NewProjectModal
          onClose={() => setShowNewProjectModal(false)}
          onSuccess={(project) => {
            setProjects([...projects, project])
            setShowNewProjectModal(false)
          }}
        />
      )}

      {/* Storage Manager Modal */}
      <StorageManager
        isOpen={showStorageManager}
        onClose={() => setShowStorageManager(false)}
      />

      {/* Analytics Dashboard */}
      <AnalyticsDashboard
        isOpen={showAnalytics}
        onClose={() => setShowAnalytics(false)}
      />
    </div>
  )
}
