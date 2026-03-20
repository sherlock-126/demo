'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

export default function Videos() {
  const [videos, setVideos] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadVideos()
  }, [])

  const loadVideos = async () => {
    try {
      const data = await api.listVideos()
      setVideos(data.videos || [])
    } catch (error) {
      console.error('Error loading videos:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async (videoId: string) => {
    try {
      const url = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/videos/${videoId}/download`
      window.open(url, '_blank')
    } catch (error) {
      console.error('Error downloading video:', error)
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading videos...</div>
  }

  return (
    <div className="max-w-6xl mx-auto py-8">
      <h1 className="text-4xl font-bold mb-8">Generated Videos</h1>

      {videos.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <p className="text-gray-500 text-lg">No videos generated yet</p>
          <a href="/" className="inline-block mt-4 bg-primary-600 text-white px-6 py-2 rounded-md hover:bg-primary-700">
            Generate Your First Video
          </a>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map((video: any) => (
            <div key={video.id} className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="aspect-video bg-gray-200 flex items-center justify-center">
                <svg className="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="p-4">
                <h3 className="font-semibold mb-2">Video {video.id.slice(0, 8)}</h3>
                <div className="text-sm text-gray-600 mb-3">
                  <div>Status: <span className="font-medium">{video.status}</span></div>
                  {video.size && (
                    <div>Size: {(video.size / 1024 / 1024).toFixed(2)} MB</div>
                  )}
                </div>
                {video.status === 'completed' && (
                  <button
                    onClick={() => handleDownload(video.id)}
                    className="w-full bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"
                  >
                    Download
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}