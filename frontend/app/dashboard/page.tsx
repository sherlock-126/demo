'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

export default function Dashboard() {
  const [scripts, setScripts] = useState([])
  const [videos, setVideos] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [scriptsData, videosData] = await Promise.all([
        api.listScripts(),
        api.listVideos()
      ])
      setScripts(scriptsData.scripts || [])
      setVideos(videosData.videos || [])
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading...</div>
  }

  return (
    <div className="max-w-6xl mx-auto py-8">
      <h1 className="text-4xl font-bold mb-8">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4">Recent Scripts</h2>
          {scripts.length === 0 ? (
            <p className="text-gray-500">No scripts generated yet</p>
          ) : (
            <ul className="space-y-2">
              {scripts.slice(0, 5).map((script: any) => (
                <li key={script.id} className="border-b pb-2">
                  <div className="font-medium">{script.topic}</div>
                  <div className="text-sm text-gray-500">
                    Status: {script.status}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4">Recent Videos</h2>
          {videos.length === 0 ? (
            <p className="text-gray-500">No videos generated yet</p>
          ) : (
            <ul className="space-y-2">
              {videos.slice(0, 5).map((video: any) => (
                <li key={video.id} className="border-b pb-2">
                  <div className="font-medium">Video {video.id.slice(0, 8)}</div>
                  <div className="text-sm text-gray-500">
                    Status: {video.status}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="mt-8 bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <a href="/" className="bg-primary-100 text-primary-800 p-4 rounded-lg text-center hover:bg-primary-200">
            Generate Script
          </a>
          <a href="/videos" className="bg-green-100 text-green-800 p-4 rounded-lg text-center hover:bg-green-200">
            View Videos
          </a>
          <button className="bg-purple-100 text-purple-800 p-4 rounded-lg hover:bg-purple-200">
            Create Images
          </button>
          <button className="bg-orange-100 text-orange-800 p-4 rounded-lg hover:bg-orange-200">
            Export Content
          </button>
        </div>
      </div>
    </div>
  )
}