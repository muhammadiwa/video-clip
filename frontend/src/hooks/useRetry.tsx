'use client'

import { useState, useCallback } from 'react'

interface RetryOptions {
  maxRetries?: number
  retryDelay?: number
  backoffMultiplier?: number
  onRetry?: (attempt: number, error: Error) => void
  onMaxRetriesReached?: (error: Error) => void
}

interface RetryState {
  isRetrying: boolean
  attempt: number
  lastError: Error | null
}

export function useRetry<T>(
  asyncFn: () => Promise<T>,
  options: RetryOptions = {}
) {
  const {
    maxRetries = 3,
    retryDelay = 1000,
    backoffMultiplier = 2,
    onRetry,
    onMaxRetriesReached
  } = options

  const [state, setState] = useState<RetryState>({
    isRetrying: false,
    attempt: 0,
    lastError: null
  })

  const execute = useCallback(async (): Promise<T> => {
    let lastError: Error | null = null
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        setState({ isRetrying: attempt > 0, attempt, lastError: null })
        const result = await asyncFn()
        setState({ isRetrying: false, attempt: 0, lastError: null })
        return result
      } catch (error: any) {
        lastError = error
        setState({ isRetrying: true, attempt, lastError: error })
        
        if (attempt < maxRetries) {
          const delay = retryDelay * Math.pow(backoffMultiplier, attempt)
          onRetry?.(attempt + 1, error)
          await new Promise(resolve => setTimeout(resolve, delay))
        }
      }
    }

    setState({ isRetrying: false, attempt: maxRetries, lastError })
    onMaxRetriesReached?.(lastError!)
    throw lastError
  }, [asyncFn, maxRetries, retryDelay, backoffMultiplier, onRetry, onMaxRetriesReached])

  const reset = useCallback(() => {
    setState({ isRetrying: false, attempt: 0, lastError: null })
  }, [])

  return {
    execute,
    reset,
    ...state
  }
}

// Utility function for one-off retries
export async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const {
    maxRetries = 3,
    retryDelay = 1000,
    backoffMultiplier = 2,
    onRetry,
    onMaxRetriesReached
  } = options

  let lastError: Error | null = null

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error: any) {
      lastError = error
      
      if (attempt < maxRetries) {
        const delay = retryDelay * Math.pow(backoffMultiplier, attempt)
        onRetry?.(attempt + 1, error)
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }
  }

  onMaxRetriesReached?.(lastError!)
  throw lastError
}

// Error boundary wrapper for async operations
export function createRetryWrapper(defaultOptions: RetryOptions = {}) {
  return function wrap<T extends (...args: any[]) => Promise<any>>(fn: T): T {
    return (async (...args: Parameters<T>): Promise<ReturnType<T>> => {
      return withRetry(() => fn(...args), defaultOptions)
    }) as T
  }
}
