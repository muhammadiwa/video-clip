'use client'

import { useState } from 'react'
import { Plus, FolderOpen, Clock, CheckCircle, Loader } from 'lucide-react'
import { motion } from 'framer-motion'
import NewProjectModal from '@/components/dashboard/NewProjectModal'
import ProjectCard from '@/components/dashboard/ProjectCard'

export default function Dashboard() {
  const [showNewProjectModal, setShowNewProjectModal] = useState(false)
  const [projects, setProjects] = useState([])

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-dark-border">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold gradient-text">Viral Clip AI</h1>
            
            <button
              onClick={() => setShowNewProjectModal(true)}
              className="glass-button glow-effect flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              New Project
            </button>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {[
            { label: 'Total Projects', value: '0', icon: FolderOpen, color: 'text-primary' },
            { label: 'Processing', value: '0', icon: Loader, color: 'text-accent-cyan' },
            { label: 'Ready', value: '0', icon: Clock, color: 'text-yellow-500' },
            { label: 'Completed', value: '0', icon: CheckCircle, color: 'text-green-500' },
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
          <h2 className="text-2xl font-bold mb-6">Your Projects</h2>
          
          {projects.length === 0 ? (
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
              {projects.map((project: any) => (
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
            setProjects([...projects, project] as any)
            setShowNewProjectModal(false)
          }}
        />
      )}
    </div>
  )
}
