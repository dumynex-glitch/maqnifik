import type { Metadata } from 'next'
import Link from 'next/link'
import './globals.css'

export const metadata: Metadata = {
  title: 'Magnific API Integration',
  description: 'Multi-key API integration with quota tracking and webhook handling',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
          <nav className="max-w-6xl mx-auto px-4 py-3 flex flex-wrap gap-3 text-sm">
            <Link className="font-semibold text-blue-700" href="/">Home</Link>
            <Link className="text-gray-700 hover:text-blue-700" href="/settings">Settings</Link>
            <Link className="text-gray-700 hover:text-blue-700" href="/video">Video</Link>
            <Link className="text-gray-700 hover:text-blue-700" href="/image">Image</Link>
            <Link className="text-gray-700 hover:text-blue-700" href="/editing">Editing</Link>
            <Link className="text-gray-700 hover:text-blue-700" href="/audio">Audio</Link>
            <Link className="text-gray-700 hover:text-blue-700" href="/gallery">Gallery</Link>
            <Link className="text-gray-700 hover:text-blue-700" href="/logs">Logs</Link>
          </nav>
        </header>
        {children}
      </body>
    </html>
  )
}
