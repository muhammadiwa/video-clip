'use client'

import { motion } from 'framer-motion'
import { Video, Clock, Trash2 } from 'lucide-react'
import Link from 'next/link'
import type { Project } from '@/types'

interface ProjectCardProps {
  project: Project
}

const statusColors = {
  created: 'text-gray-400',
  processing: 'text-accent-cyan',
  ready: 'text-yellow-500',
  edited: 'text-green-500',
}

export default function ProjectCard({ project }: ProjectCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5 }}
      className="glass-card p-6 hover:bg-white/10 transition-all duration-300"
    >
      <Link href={`/project/${project.id}`}>
        <div className="aspect-video bg-gradient-to-br from-primary to-accent-cyan rounded-lg mb-4 flex items-center justify-center">
          <Video className="w-12 h-12 text-white" />
        </div>
        
        <h3 className="text-xl font-bold mb-2 truncate">{project.name}</h3>
        
        {project.description && (
          <p className="text-gray-400 text-sm mb-3 line-clamp-2">
            {project.description}
          </p>
        )}
        
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-gray-500" />
            <span className="text-gray-400">
              {new Date(project.created_at).toLocaleDateString()}
            </span>
          </div>
          
          <span className={`font-medium ${statusColors[project.status]}`}>
            {project.status}
          </span>
        </div>
      </Link>
      
      <div className="flex gap-2 mt-4 pt-4 border-t border-dark-border">
        <button className="flex-1 px-4 py-2 bg-primary/10 hover:bg-primary/20 rounded-lg transition-colors text-sm">
          Open
        </button>
        <button className="p-2 hover:bg-red-500/10 rounded-lg transition-colors">
          <Trash2 className="w-4 h-4 text-red-500" />
        </button>
      </div>
    </motion.div>
  )
}
