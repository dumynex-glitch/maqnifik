'use client'

import { useState } from 'react'
import { generateAudio } from '@/lib/api'

export default function AudioPage() {
  const [prompt, setPrompt] = useState('')
  const [type, setType] = useState('sound-effects')
  const [duration, setDuration] = useState(5)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const data = await generateAudio({ prompt, type, duration })
      setResult(data)
    } catch (err: any) {
      setError(err.message || 'Failed to generate audio')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Audio Generation</h1>
      <form onSubmit={onSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow">
        <div>
          <label className="block text-sm mb-1">Type</label>
          <select value={type} onChange={(e) => setType(e.target.value)} className="w-full border rounded p-2">
            <option value="sound-effects">Sound Effects</option>
            <option value="voiceover">Voiceover</option>
          </select>
        </div>
        <div>
          <label className="block text-sm mb-1">Prompt</label>
          <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} className="w-full border rounded p-2" rows={4} required />
        </div>
        <div>
          <label className="block text-sm mb-1">Duration: {duration}s</label>
          <input type="range" min={1} max={22} value={duration} onChange={(e) => setDuration(Number(e.target.value))} className="w-full" />
        </div>
        <button disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50">{loading ? 'Submitting...' : 'Generate'}</button>
      </form>
      {error && <p className="mt-4 text-red-600">{error}</p>}
      {result && <pre className="mt-4 bg-black text-green-300 p-3 rounded text-xs overflow-auto">{JSON.stringify(result, null, 2)}</pre>}
    </div>
  )
}
