'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Play, Sparkles, Video, Wand2 } from 'lucide-react'

export default function Home() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-dark to-accent-cyan/20" />
        
        {/* Grid pattern overlay */}
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20" />
        
        <div className="relative z-10 container mx-auto px-6 py-20">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left: Text Content */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card mb-6">
                <Sparkles className="w-4 h-4 text-accent-cyan" />
                <span className="text-sm">AI-Powered Video Editing</span>
              </div>
              
              <h1 className="text-6xl font-bold mb-6 leading-tight">
                Turn <span className="gradient-text">1 Long Video</span>
                <br />
                into <span className="gradient-text">10 Viral Clips</span>
              </h1>
              
              <p className="text-xl text-gray-400 mb-8">
                Automatically detect viral moments, add stunning subtitles, 
                and export ready-to-post content for YouTube Shorts, TikTok, and Reels.
              </p>
              
              <div className="flex gap-4">
                <Link href="/dashboard">
                  <button className="glass-button glow-effect flex items-center gap-2 text-lg font-semibold">
                    <Play className="w-5 h-5" />
                    Get Started Free
                  </button>
                </Link>
                
                <button className="glass-button flex items-center gap-2 text-lg">
                  <Video className="w-5 h-5" />
                  Try Sample Project
                </button>
              </div>
            </motion.div>
            
            {/* Right: 3D Visual (placeholder) */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="relative"
            >
              <div className="glass-card p-8 glow-effect">
                <div className="aspect-video bg-gradient-to-br from-primary to-accent-cyan rounded-lg flex items-center justify-center">
                  <Wand2 className="w-24 h-24 text-white animate-pulse" />
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>
      
      {/* How it works */}
      <section className="py-20 relative">
        <div className="container mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-5xl font-bold mb-4">How It Works</h2>
            <p className="text-xl text-gray-400">3 Simple Steps to Viral Content</p>
          </motion.div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: '01',
                title: 'Upload Video',
                description: 'Upload your long-form video or paste a YouTube link',
                icon: Video
              },
              {
                step: '02',
                title: 'AI Detection',
                description: 'AI finds viral moments and generates clips automatically',
                icon: Sparkles
              },
              {
                step: '03',
                title: 'Edit & Export',
                description: 'Customize subtitles, add effects, and export for all platforms',
                icon: Play
              }
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                viewport={{ once: true }}
                className="glass-card p-8 hover:bg-white/10 transition-all duration-300"
              >
                <div className="text-6xl font-bold text-primary/20 mb-4">{item.step}</div>
                <item.icon className="w-12 h-12 text-primary mb-4" />
                <h3 className="text-2xl font-bold mb-3">{item.title}</h3>
                <p className="text-gray-400">{item.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </main>
  )
}
