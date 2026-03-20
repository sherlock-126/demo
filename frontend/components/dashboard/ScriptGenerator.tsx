'use client'

import { useState } from 'react'
import { Button } from '../ui/button'
import { Progress } from '../ui/progress'
import { useSSE } from '@/lib/hooks/useSSE'
import { apiClient } from '@/lib/api'

interface ScriptGeneratorProps {
  onComplete: (data: any) => void
}

export default function ScriptGenerator({ onComplete }: ScriptGeneratorProps) {
  const [topic, setTopic] = useState('')
  const [numSlides, setNumSlides] = useState(5)
  const [language, setLanguage] = useState('vi')
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    if (!topic || topic.length < 10) {
      setError('Topic must be at least 10 characters')
      return
    }

    setLoading(true)
    setError('')
    setProgress(0)

    try {
      const response = await apiClient.generateScript({
        topic,
        num_slides: numSlides,
        language,
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
        onComplete(data.result)
      })

      eventSource.addEventListener('error', (e) => {
        eventSource.close()
        setLoading(false)
        setError('Failed to generate script')
      })

    } catch (err: any) {
      setLoading(false)
      setError(err.message || 'Failed to generate script')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-4">Generate Script</h2>
        <p className="text-gray-600">
          Enter a topic and let AI generate an engaging script for your TikTok video.
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Topic
          </label>
          <textarea
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter your topic (e.g., 'Cách dạy con học đi')"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            rows={3}
            disabled={loading}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Number of Slides
            </label>
            <select
              value={numSlides}
              onChange={(e) => setNumSlides(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              disabled={loading}
            >
              {[3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
                <option key={n} value={n}>
                  {n} slides
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Language
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              disabled={loading}
            >
              <option value="vi">Vietnamese</option>
              <option value="en">English</option>
            </select>
          </div>
        </div>

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {loading && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-gray-600">
              <span>Generating script...</span>
              <span>{progress}%</span>
            </div>
            <Progress value={progress} />
          </div>
        )}

        <Button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full"
        >
          {loading ? 'Generating...' : 'Generate Script'}
        </Button>
      </div>
    </div>
  )
}