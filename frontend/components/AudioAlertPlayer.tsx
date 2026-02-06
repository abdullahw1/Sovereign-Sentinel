'use client'

import { useEffect, useRef, useState } from 'react'

interface AudioAlertPlayerProps {
  audioUrl: string
  alertId: string
  script: string
  onApprove: (alertId: string) => void
  onDismiss: (alertId: string) => void
}

export default function AudioAlertPlayer({
  audioUrl,
  alertId,
  script,
  onApprove,
  onDismiss,
}: AudioAlertPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [hasResponded, setHasResponded] = useState(false)

  useEffect(() => {
    // Auto-play audio when component mounts
    if (audioRef.current && audioUrl) {
      audioRef.current.play().catch((error) => {
        console.error('Failed to auto-play audio:', error)
      })
      setIsPlaying(true)
    }
  }, [audioUrl])

  const handleApprove = () => {
    setHasResponded(true)
    onApprove(alertId)
  }

  const handleDismiss = () => {
    setHasResponded(true)
    if (audioRef.current) {
      audioRef.current.pause()
    }
    onDismiss(alertId)
  }

  const togglePlayback = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
      } else {
        audioRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  return (
    <div className="bg-red-900 bg-opacity-50 border-2 border-red-500 rounded-lg p-6 animate-pulse">
      <div className="flex items-start gap-4">
        <span className="text-4xl">🔊</span>
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-red-100 mb-2">VOICE ALERT</h2>
          
          {/* Audio Player */}
          <div className="bg-red-800 bg-opacity-50 rounded p-4 mb-4">
            <audio
              ref={audioRef}
              src={audioUrl}
              onEnded={() => setIsPlaying(false)}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
            />
            
            <div className="flex items-center gap-3 mb-3">
              <button
                onClick={togglePlayback}
                className="px-4 py-2 bg-red-700 hover:bg-red-600 rounded text-white font-semibold"
              >
                {isPlaying ? '⏸ Pause' : '▶ Play'}
              </button>
              <span className="text-red-200 text-sm">
                {isPlaying ? 'Playing alert...' : 'Click to replay'}
              </span>
            </div>
            
            {/* Script Display */}
            <div className="bg-red-900 bg-opacity-50 rounded p-3">
              <p className="text-sm text-red-100 font-mono">{script}</p>
            </div>
          </div>

          {/* Authorization Buttons */}
          {!hasResponded ? (
            <div className="flex gap-3">
              <button
                onClick={handleApprove}
                className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-500 rounded-lg text-white font-bold text-lg transition-colors"
              >
                ✓ APPROVE
              </button>
              <button
                onClick={handleDismiss}
                className="flex-1 px-6 py-3 bg-gray-600 hover:bg-gray-500 rounded-lg text-white font-bold text-lg transition-colors"
              >
                ✕ DISMISS
              </button>
            </div>
          ) : (
            <div className="bg-gray-800 rounded-lg p-4 text-center">
              <p className="text-gray-300">
                Response recorded. {hasResponded ? 'Thank you.' : ''}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
