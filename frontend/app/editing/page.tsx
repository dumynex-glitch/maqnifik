'use client'

import { useState } from 'react'
import { upscaleImage, removeBackground, relightImage } from '@/lib/api'

export default function EditingPage() {
  const [imageUrl, setImageUrl] = useState('')
  const [op, setOp] = useState<'upscale' | 'remove-background' | 'relight'>('upscale')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const data = op === 'upscale'
        ? await upscaleImage(imageUrl)
        : op === 'remove-background'
        ? await removeBackground(imageUrl)
        : await relightImage(imageUrl)
      setResult(data)
    } catch (err: any) {
      setError(err.message || 'Failed to submit editing task')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Image Editing</h1>
      <form onSubmit={onSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow">
        <div>
          <label className="block text-sm mb-1">Operation</label>
          <select value={op} onChange={(e) => setOp(e.target.value as any)} className="w-full border rounded p-2">
            <option value="upscale">Upscale</option>
            <option value="remove-background">Remove Background</option>
            <option value="relight">Relight</option>
          </select>
        </div>
        <div>
          <label className="block text-sm mb-1">Image URL</label>
          <input value={imageUrl} onChange={(e) => setImageUrl(e.target.value)} className="w-full border rounded p-2" required />
        </div>
        <button disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50">{loading ? 'Submitting...' : 'Run'}</button>
      </form>
      {error && <p className="mt-4 text-red-600">{error}</p>}
      {result && <pre className="mt-4 bg-black text-green-300 p-3 rounded text-xs overflow-auto">{JSON.stringify(result, null, 2)}</pre>}
    </div>
  )
}
