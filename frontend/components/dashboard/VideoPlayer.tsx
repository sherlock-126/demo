'use client'

import { useState } from 'react'
import { Button } from '../ui/button'
import { Progress } from '../ui/progress'
import { apiClient } from '@/lib/api'

interface VideoPlayerProps {
  images: string[]
  onComplete: (videoPath: string) => void
}

export default function VideoPlayer({ images, onComplete }: VideoPlayerProps) {
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [videoPath, setVideoPath] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [duration, setDuration] = useState(3)
  const [transition, setTransition] = useState(0.5)

  const createVideo = async () => {
    setLoading(true)
    setError('')
    setProgress(0)

    try {
      const response = await apiClient.createVideo({
        image_paths: images,
        duration_per_slide: duration,
        transition_duration: transition,
      })

      // Listen to SSE events
      const eventSource = new EventSource(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/events/${response.task_id}`
      )

      eventSource.addEventListener('progress', (e) => {
        const data = JSON.parse(e.data)
        setProgress(data.progress || 0)
      })

      eventSource.addEventListener('complete', (e) => {
        const data = JSON.parse(e.data)
        eventSource.close()
        setLoading(false)
        const path = data.video_path
        setVideoPath(path)
        onComplete(path)
      })

      eventSource.addEventListener('error', (e) => {
        eventSource.close()
        setLoading(false)
        setError('Failed to create video')
      })

    } catch (err: any) {
      setLoading(false)
      setError(err.message || 'Failed to create video')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-4">Create Video</h2>
        <p className="text-gray-600">
          Configure video settings and generate your final TikTok video.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Duration per Slide (seconds)
          </label>
          <input
            type="number"
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            min="1"
            max="10"
            step="0.5"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={loading}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Transition Duration (seconds)
          </label>
          <input
            type="number"
            value={transition}
            onChange={(e) => setTransition(Number(e.target.value))}
            min="0"
            max="2"
            step="0.1"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={loading}
          />
        </div>
      </div>

      {loading && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-gray-600">
            <span>Creating video...</span>
            <span>{progress}%</span>
          </div>
          <Progress value={progress} />
        </div>
      )}

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {videoPath && (
        <div className="aspect-[9/16] max-w-sm mx-auto bg-black rounded-lg overflow-hidden">
          <video
            src={`${process.env.NEXT_PUBLIC_API_URL}/api/v1/files/videos/${videoPath.split('/').pop()}`}
            controls
            className="w-full h-full"
          />
        </div>
      )}

      {!videoPath && (
        <Button onClick={createVideo} disabled={loading} className="w-full">
          {loading ? 'Creating Video...' : 'Create Video'}
        </Button>
      )}
    </div>
  )
}