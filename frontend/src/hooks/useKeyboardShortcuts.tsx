'use client'

import { useEffect, useCallback } from 'react'

interface ShortcutHandlers {
  onPlayPause?: () => void
  onSkipBack?: (seconds?: number) => void
  onSkipForward?: (seconds?: number) => void
  onSetInPoint?: () => void
  onSetOutPoint?: () => void
  onNextClip?: () => void
  onPrevClip?: () => void
  onFullscreen?: () => void
  onMute?: () => void
}

export function useKeyboardShortcuts(handlers: ShortcutHandlers, enabled: boolean = true) {
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (!enabled) return
    
    // Ignore if typing in input/textarea
    const target = e.target as HTMLElement
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
      return
    }

    switch (e.key.toLowerCase()) {
      case ' ':
        e.preventDefault()
        handlers.onPlayPause?.()
        break
      case 'k':
        e.preventDefault()
        handlers.onPlayPause?.()
        break
      case 'j':
        e.preventDefault()
        handlers.onSkipBack?.(10)
        break
      case 'l':
        e.preventDefault()
        handlers.onSkipForward?.(10)
        break
      case 'arrowleft':
        e.preventDefault()
        handlers.onSkipBack?.(5)
        break
      case 'arrowright':
        e.preventDefault()
        handlers.onSkipForward?.(5)
        break
      case 'i':
        e.preventDefault()
        handlers.onSetInPoint?.()
        break
      case 'o':
        e.preventDefault()
        handlers.onSetOutPoint?.()
        break
      case 'n':
        if (e.shiftKey) {
          e.preventDefault()
          handlers.onNextClip?.()
        }
        break
      case 'p':
        if (e.shiftKey) {
          e.preventDefault()
          handlers.onPrevClip?.()
        }
        break
      case 'f':
        e.preventDefault()
        handlers.onFullscreen?.()
        break
      case 'm':
        e.preventDefault()
        handlers.onMute?.()
        break
    }
  }, [handlers, enabled])

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])
}

export const KEYBOARD_SHORTCUTS = [
  { key: 'Space / K', action: 'Play/Pause' },
  { key: 'J', action: 'Skip back 10s' },
  { key: 'L', action: 'Skip forward 10s' },
  { key: '← / →', action: 'Skip 5s' },
  { key: 'I', action: 'Set In point' },
  { key: 'O', action: 'Set Out point' },
  { key: 'Shift+N', action: 'Next clip' },
  { key: 'Shift+P', action: 'Previous clip' },
  { key: 'F', action: 'Fullscreen' },
  { key: 'M', action: 'Mute/Unmute' },
]
