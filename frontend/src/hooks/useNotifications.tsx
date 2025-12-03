'use client'

import { useState, useEffect, useCallback } from 'react'

export interface NotificationOptions {
  title: string
  body: string
  icon?: string
  tag?: string
  requireInteraction?: boolean
  onClick?: () => void
}

export function useNotifications() {
  const [permission, setPermission] = useState<NotificationPermission>('default')
  const [supported, setSupported] = useState(false)

  useEffect(() => {
    setSupported('Notification' in window)
    if ('Notification' in window) {
      setPermission(Notification.permission)
    }
  }, [])

  const requestPermission = useCallback(async () => {
    if (!supported) return false
    
    try {
      const result = await Notification.requestPermission()
      setPermission(result)
      return result === 'granted'
    } catch (error) {
      console.error('Failed to request notification permission:', error)
      return false
    }
  }, [supported])

  const showNotification = useCallback((options: NotificationOptions) => {
    if (!supported || permission !== 'granted') {
      console.log('Notifications not available or not permitted')
      return null
    }

    try {
      const notification = new Notification(options.title, {
        body: options.body,
        icon: options.icon || '/favicon.ico',
        tag: options.tag,
        requireInteraction: options.requireInteraction,
      })

      if (options.onClick) {
        notification.onclick = () => {
          window.focus()
          options.onClick?.()
          notification.close()
        }
      }

      return notification
    } catch (error) {
      console.error('Failed to show notification:', error)
      return null
    }
  }, [supported, permission])

  const notifyExportComplete = useCallback((clipName: string, clipCount?: number) => {
    const title = clipCount 
      ? `${clipCount} Clips Exported!`
      : 'Export Complete!'
    const body = clipCount
      ? `Successfully exported ${clipCount} viral clips`
      : `${clipName} has been exported successfully`
    
    showNotification({
      title,
      body,
      tag: 'export-complete',
      onClick: () => window.focus()
    })
  }, [showNotification])

  const notifyProcessingComplete = useCallback((videoName: string) => {
    showNotification({
      title: 'Processing Complete!',
      body: `${videoName} has finished processing`,
      tag: 'processing-complete',
      onClick: () => window.focus()
    })
  }, [showNotification])

  const notifyError = useCallback((message: string) => {
    showNotification({
      title: 'Error Occurred',
      body: message,
      tag: 'error',
      requireInteraction: true
    })
  }, [showNotification])

  return {
    supported,
    permission,
    requestPermission,
    showNotification,
    notifyExportComplete,
    notifyProcessingComplete,
    notifyError
  }
}
