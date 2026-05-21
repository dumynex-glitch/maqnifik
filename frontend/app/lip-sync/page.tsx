'use client'

import { useState } from 'react'
import { generateLipSync } from '@/lib/api'

type Model = 'latent-sync' | 'veed-fabric-1-0-fast' | 'veed-fabric-1-0'

export default function LipSyncPage() {
  const [model, setModel] = useState<Model>('veed-fabric-1-0-fast')
  const [audioUrl, setAudioUrl] = useState('')
  const [videoUrl, setVideoUrl] = useState('')
  const [imageUrl, setImageUrl] = useState('')
  const [resolution, setResolution] = useState('720p')
  const [seed, setSeed] = useState(0)
  const [guidanceScale, setGuidanceScale] = useState(1.0)
  const [useGuidance, setUseGuidance] = useState(false)
  const [useSeed, setUseSeed] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  const isLatent = model === 'latent-sync'

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    try {
      if (isLatent && !videoUrl) throw new Error('Latent Sync requires video_url.')
      if (!isLatent && !imageUrl) throw new Error('Veed models require image_url.')
      if (!audioUrl) throw new Error('audio_url is required.')

      const data = await generateLipSync({
        model,
        audio_url: audioUrl,
        video_url: isLatent ? (videoUrl || undefined) : undefined,
        image_url: !isLatent ? (imageUrl || undefined) : undefined,
        resolution: !isLatent ? resolution : undefined,
        seed: useSeed ? seed : undefined,
        guidance_scale: useGuidance ? guidanceScale : undefined,
      })
      setResult(data)
    } catch (err: any) {
      setError(err.message || 'Failed to generate lip-sync')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Lip Sync</h1>
      <form onSubmit={onSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow">
        <div>
          <label className="block text-sm mb-1">Model</label>
          <select value={model} onChange={(e) => setModel(e.target.value as Model)} className="w-full border rounded p-2">
            <option value="veed-fabric-1-0-fast">Veed Fabric 1.0 Fast</option>
            <option value="veed-fabric-1-0">Veed Fabric 1.0</option>
            <option value="latent-sync">Latent Sync</option>
          </select>
        </div>

        <div>
          <label className="block text-sm mb-1">
            {isLatent ? 'Video URL' : 'Image URL'} <span className="text-red-500">*</span>
          </label>
          <input value={isLatent ? videoUrl : imageUrl} onChange={(e) => isLatent ? setVideoUrl(e.target.value) : setImageUrl(e.target.value)} className="w-full border rounded p-2" placeholder="https://..." required />
          <p className="text-xs text-gray-600 mt-1">
            {isLatent
              ? 'URL of the video to lip-sync. Must be publicly accessible.'
              : 'URL of a front-facing portrait photo. Must be publicly accessible.'}
          </p>
        </div>

        <div>
          <label className="block text-sm mb-1">Audio URL <span className="text-red-500">*</span></label>
          <input value={audioUrl} onChange={(e) => setAudioUrl(e.target.value)} className="w-full border rounded p-2" placeholder="https://..." required />
          <p className="text-xs text-gray-600 mt-1">URL of the audio file (MP3, WAV, M4A). Must be publicly accessible.</p>
        </div>

        {!isLatent && (
          <div>
            <label className="block text-sm mb-1">Resolution <span className="text-red-500">*</span></label>
            <select value={resolution} onChange={(e) => setResolution(e.target.value)} className="w-full border rounded p-2">
              <option value="720p">720p (1280x720)</option>
              <option value="480p">480p (854x480)</option>
            </select>
          </div>
        )}

        {isLatent && (
          <>
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={useSeed} onChange={(e) => setUseSeed(e.target.checked)} />
              Custom Seed <span className="text-xs text-gray-500">(Optional)</span>
            </label>
            {useSeed && (
              <input type="number" value={seed} onChange={(e) => setSeed(Number(e.target.value))} className="w-full border rounded p-2 text-sm" />
            )}

            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={useGuidance} onChange={(e) => setUseGuidance(e.target.checked)} />
              Guidance Scale <span className="text-xs text-gray-500">(Optional, default 1.0)</span>
            </label>
            {useGuidance && (
              <input type="number" min={0} max={5} step={0.1} value={guidanceScale} onChange={(e) => setGuidanceScale(Number(e.target.value))} className="w-full border rounded p-2 text-sm" />
            )}
          </>
        )}

        <button disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50">
          {loading ? 'Submitting...' : 'Generate'}
        </button>
      </form>
      {error && <p className="mt-4 text-red-600">{error}</p>}
      {result && <pre className="mt-4 bg-black text-green-300 p-3 rounded text-xs overflow-auto">{JSON.stringify(result, null, 2)}</pre>}
    </div>
  )
}
