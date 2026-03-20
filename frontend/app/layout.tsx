import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'TikTok Content Generator',
  description: 'Generate TikTok content with AI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="bg-primary-600 text-white p-4">
          <div className="container mx-auto flex justify-between items-center">
            <h1 className="text-2xl font-bold">TikTok Generator</h1>
            <div className="space-x-4">
              <a href="/" className="hover:text-primary-200">Home</a>
              <a href="/dashboard" className="hover:text-primary-200">Dashboard</a>
              <a href="/videos" className="hover:text-primary-200">Videos</a>
            </div>
          </div>
        </nav>
        <main className="container mx-auto p-4">
          {children}
        </main>
      </body>
    </html>
  )
}