'use client'

import Link from 'next/link'
import { ArrowRight, Video, Image, FileText } from 'lucide-react'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="max-w-5xl w-full">
        <h1 className="text-5xl font-bold text-center mb-8">
          TikTok Content Generator
        </h1>
        <p className="text-xl text-gray-600 text-center mb-12">
          Generate AI-powered content for TikTok in minutes
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <FileText className="w-12 h-12 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Generate Script</h3>
            <p className="text-gray-600">
              AI generates engaging scripts from your topic
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-lg">
            <Image className="w-12 h-12 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Create Images</h3>
            <p className="text-gray-600">
              Auto-generate split-screen images with text
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-lg">
            <Video className="w-12 h-12 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Assemble Video</h3>
            <p className="text-gray-600">
              Combine images into a TikTok-ready video
            </p>
          </div>
        </div>

        <div className="flex justify-center">
          <Link
            href="/dashboard"
            className="inline-flex items-center px-8 py-4 bg-primary text-white font-semibold rounded-lg hover:bg-opacity-90 transition"
          >
            Start Creating
            <ArrowRight className="ml-2 w-5 h-5" />
          </Link>
        </div>
      </div>
    </main>
  )
}