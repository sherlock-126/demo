'use client'

import { useState } from 'react'
import ScriptGenerator from '@/components/dashboard/ScriptGenerator'
import ImagePreview from '@/components/dashboard/ImagePreview'
import VideoPlayer from '@/components/dashboard/VideoPlayer'
import ProgressTracker from '@/components/dashboard/ProgressTracker'

export default function Dashboard() {
  const [currentStep, setCurrentStep] = useState(1)
  const [scriptData, setScriptData] = useState(null)
  const [images, setImages] = useState<string[]>([])
  const [videoPath, setVideoPath] = useState<string | null>(null)

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <ProgressTracker currentStep={currentStep} />
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        {currentStep === 1 && (
          <ScriptGenerator
            onComplete={(data) => {
              setScriptData(data)
              setCurrentStep(2)
            }}
          />
        )}

        {currentStep === 2 && scriptData && (
          <ImagePreview
            scriptData={scriptData}
            onComplete={(imagePaths) => {
              setImages(imagePaths)
              setCurrentStep(3)
            }}
          />
        )}

        {currentStep === 3 && images.length > 0 && (
          <VideoPlayer
            images={images}
            onComplete={(path) => {
              setVideoPath(path)
              setCurrentStep(4)
            }}
          />
        )}

        {currentStep === 4 && videoPath && (
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">Video Ready!</h2>
            <p className="text-gray-600 mb-6">
              Your TikTok video has been generated successfully.
            </p>
            <div className="flex justify-center space-x-4">
              <a
                href={`${process.env.NEXT_PUBLIC_API_URL}/api/v1/files/videos/${videoPath.split('/').pop()}`}
                download
                className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-opacity-90"
              >
                Download Video
              </a>
              <button
                onClick={() => {
                  setCurrentStep(1)
                  setScriptData(null)
                  setImages([])
                  setVideoPath(null)
                }}
                className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
              >
                Create Another
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}