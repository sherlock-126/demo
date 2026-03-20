'use client'

import { useState, useEffect } from 'react'
import { Button } from '../ui/button'
import { Progress } from '../ui/progress'
import { apiClient } from '@/lib/api'

interface ImagePreviewProps {
  scriptData: any
  onComplete: (images: string[]) => void
}

export default function ImagePreview({ scriptData, onComplete }: ImagePreviewProps) {
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [images, setImages] = useState<string[]>([])
  const [error, setError] = useState('')

  const generateImages = async () => {
    setLoading(true)
    setError('')
    setProgress(0)

    try {
      const response = await apiClient.generateImages({
        script_id: scriptData.id,
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
        setImages(data.images || [])
      })

      eventSource.addEventListener('error', (e) => {
        eventSource.close()
        setLoading(false)
        setError('Failed to generate images')
      })

    } catch (err: any) {
      setLoading(false)
      setError(err.message || 'Failed to generate images')
    }
  }

  useEffect(() => {
    generateImages()
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-4">Image Preview</h2>
        <p className="text-gray-600">
          Review the generated images for your TikTok video.
        </p>
      </div>

      {loading && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-gray-600">
            <span>Generating images...</span>
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

      {images.length > 0 && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {images.map((image, index) => (
              <div key={index} className="aspect-[9/16] bg-gray-100 rounded-lg overflow-hidden">
                <img
                  src={`${process.env.NEXT_PUBLIC_API_URL}/api/v1/files/images/${image.split('/').pop()}`}
                  alt={`Slide ${index + 1}`}
                  className="w-full h-full object-cover"
                />
              </div>
            ))}
          </div>

          <div className="flex space-x-4">
            <Button onClick={() => onComplete(images)} className="flex-1">
              Continue to Video Creation
            </Button>
            <Button onClick={generateImages} variant="secondary">
              Regenerate Images
            </Button>
          </div>
        </>
      )}
    </div>
  )
}