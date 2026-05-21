'use client'

import { useEffect, useState } from 'react'
import { deleteGalleryItem, getGallery, toggleFavorite } from '@/lib/api'

export default function GalleryPage() {
  const [items, setItems] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await getGallery({ limit: 100 })
      setItems(Array.isArray(data) ? data : [])
    } catch (err: any) {
      setError(err.message || 'Failed to load gallery')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Gallery</h1>
      {loading && <p>Loading...</p>}
      {error && <p className="text-red-600">{error}</p>}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {items.map((item) => (
          <div key={item.id} className="bg-white rounded-lg shadow p-4">
            <p className="font-semibold">{item.title || item.type}</p>
            <p className="text-xs text-gray-500 mb-2">{item.task_id}</p>
            <a href={item.result_url} target="_blank" className="text-blue-700 text-sm underline">Open result</a>
            <div className="mt-3 flex gap-2">
              <button onClick={async () => { await toggleFavorite(item.id); load() }} className="px-3 py-1 text-sm bg-gray-800 text-white rounded">{item.favorited ? 'Unfavorite' : 'Favorite'}</button>
              <button onClick={async () => { await deleteGalleryItem(item.id); load() }} className="px-3 py-1 text-sm bg-red-600 text-white rounded">Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
