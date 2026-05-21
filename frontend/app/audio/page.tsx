'use client'

import { useState } from 'react'
import { generateAudio } from '@/lib/api'

const DEFAULT_VOICES = [
  { id: '21m00Tcm4TlvDq8ikWAM', name: 'Rachel (calm, professional female)' },
  { id: 'AZnzlk1XvdvUeBnXmlld', name: 'Domi (warm, mature female)' },
  { id: 'EXAVITQu4vrVxn15xGnx', name: 'Bella (young, cheerful female)' },
  { id: 'ErXwobaYiN019PkySvjV', name: 'Antoni (deep, calm male)' },
  { id: 'MF3mGyEYCl7XYWbV9V6O', name: 'Elli (clear, articulate female)' },
  { id: 'TxGEqnHWrfWFTfGW9XjX', name: 'Josh (deep, American male)' },
  { id: 'VR6AewLTigWG4xSOuka', name: 'Sam (warm, friendly male)' },
  { id: 'pNInz6obpgDQGcFmaJgB', name: 'Adam (deep, British male)' },
]

export default function AudioPage() {
  const [type, setType] = useState('sound-effects')
  const [prompt, setPrompt] = useState('')
  const [duration, setDuration] = useState(5)
  const [voiceId, setVoiceId] = useState(DEFAULT_VOICES[0].id)
  const [stability, setStability] = useState(0.5)
  const [similarityBoost, setSimilarityBoost] = useState(0.2)
  const [speed, setSpeed] = useState(1.0)
  const [useSpeakerBoost, setUseSpeakerBoost] = useState(true)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  const isVoiceover = type === 'voiceover'

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const data = await generateAudio({
        prompt,
        type,
        ...(isVoiceover ? { voice_id: voiceId, stability, similarity_boost: similarityBoost, speed, use_speaker_boost: useSpeakerBoost } : { duration }),
      })
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
            <option value="voiceover">Voiceover (ElevenLabs)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm mb-1">Text</label>
          <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} className="w-full border rounded p-2" rows={4} required />
          <p className="text-xs text-gray-600 mt-1">
            {isVoiceover
              ? 'Text to convert to speech. Supports UTF-8, up to 40,000 characters.'
              : 'Text description of the sound effect to generate.'}
          </p>
        </div>

        {isVoiceover && (
          <>
            <div>
              <label className="block text-sm mb-1">Voice</label>
              <select value={voiceId} onChange={(e) => setVoiceId(e.target.value)} className="w-full border rounded p-2">
                {DEFAULT_VOICES.map(v => (
                  <option key={v.id} value={v.id}>{v.name}</option>
                ))}
              </select>
              <input
                value={voiceId}
                onChange={(e) => setVoiceId(e.target.value)}
                className="w-full border rounded p-2 mt-1 text-xs"
                placeholder="Or paste any ElevenLabs voice ID..."
              />
            </div>

            <div>
              <label className="block text-sm mb-1">Stability: {stability.toFixed(2)}</label>
              <input type="range" min={0} max={1} step={0.05} value={stability} onChange={(e) => setStability(Number(e.target.value))} className="w-full" />
              <p className="text-xs text-gray-600">0.0 = more expressive/varied, 1.0 = more consistent/stable</p>
            </div>

            <div>
              <label className="block text-sm mb-1">Similarity Boost: {similarityBoost.toFixed(2)}</label>
              <input type="range" min={0} max={1} step={0.05} value={similarityBoost} onChange={(e) => setSimilarityBoost(Number(e.target.value))} className="w-full" />
              <p className="text-xs text-gray-600">Higher values match voice more closely but may introduce artifacts</p>
            </div>

            <div>
              <label className="block text-sm mb-1">Speed: {speed.toFixed(2)}x</label>
              <input type="range" min={0.7} max={1.2} step={0.05} value={speed} onChange={(e) => setSpeed(Number(e.target.value))} className="w-full" />
              <p className="text-xs text-gray-600">0.7 = 30% slower, 1.0 = normal, 1.2 = 20% faster</p>
            </div>

            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={useSpeakerBoost} onChange={(e) => setUseSpeakerBoost(e.target.checked)} />
              Speaker Boost <span className="text-xs text-gray-500">(enhanced voice clarity)</span>
            </label>
          </>
        )}

        {!isVoiceover && (
          <div>
            <label className="block text-sm mb-1">Duration: {duration}s</label>
            <input type="range" min={1} max={22} value={duration} onChange={(e) => setDuration(Number(e.target.value))} className="w-full" />
          </div>
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
