'use client'

import { useState } from 'react'
import { generateVideo } from '@/lib/api'

type Model =
  | 'kling-v3-pro'
  | 'kling-v3-std'
  | 'kling-v26-pro'
  | 'kling-v25-pro'
  | 'kling-v26-motion-control-pro'
  | 'kling-v26-motion-control-std'

export default function VideoPage() {
  const [model, setModel] = useState<Model>('kling-v26-pro')
  const [prompt, setPrompt] = useState('')
  const [negativePrompt, setNegativePrompt] = useState('')
  const [imageUrl, setImageUrl] = useState('')
  const [videoUrl, setVideoUrl] = useState('')
  const [imageMode, setImageMode] = useState<'url' | 'upload'>('url')
  const [duration, setDuration] = useState(5)
  const [cfgScale, setCfgScale] = useState(0.5)
  const [aspectRatio, setAspectRatio] = useState('widescreen_16_9')
  const [generateAudio, setGenerateAudio] = useState(false)
  const [characterOrientation, setCharacterOrientation] = useState<'video' | 'image'>('video')
  const [endImageUrl, setEndImageUrl] = useState('')
  const [multiShot, setMultiShot] = useState(false)
  const [shotType, setShotType] = useState('default')
  const [multiPrompt, setMultiPrompt] = useState('')

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<any>(null)

  const isKling3 = model === 'kling-v3-pro' || model === 'kling-v3-std'
  const isMotion = model === 'kling-v26-motion-control-pro' || model === 'kling-v26-motion-control-std'
  const is25 = model === 'kling-v25-pro'
  const is26 = model === 'kling-v26-pro'
  const isImageMode = Boolean(imageUrl)

  const onUploadImage = (file: File | null) => {
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      const value = String(reader.result || '')
      const base64 = value.includes(',') ? value.split(',')[1] : value
      setImageUrl(base64)
    }
    reader.readAsDataURL(file)
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    try {
      if (is25 && !imageUrl) throw new Error('Kling 2.5 Pro requires image input.')
      if (isMotion && (!imageUrl || !videoUrl)) throw new Error('Motion control requires image_url and video_url.')
      if ((is26 || !isMotion) && !isKling3 && !prompt && !imageUrl) throw new Error('Provide prompt or image input.')

      const data = await generateVideo({
        model,
        prompt,
        image_url: !isKling3 ? (imageUrl || undefined) : undefined,
        video_url: videoUrl || undefined,
        duration,
        mode: imageUrl ? 'image-to-video' : 'text-to-video',
        negative_prompt: !isMotion && !isKling3 ? (negativePrompt || undefined) : undefined,
        cfg_scale: !isKling3 ? cfgScale : undefined,
        aspect_ratio: (is26 || isKling3) ? aspectRatio : undefined,
        generate_audio: (is26 || isKling3) ? generateAudio : undefined,
        character_orientation: isMotion ? characterOrientation : undefined,
        start_image_url: isKling3 ? (imageUrl || undefined) : undefined,
        end_image_url: isKling3 ? (endImageUrl || undefined) : undefined,
        multi_shot: isKling3 ? multiShot || undefined : undefined,
        shot_type: isKling3 ? (multiShot ? shotType : undefined) : undefined,
        multi_prompt: isKling3 ? (multiShot ? (multiPrompt || undefined) : undefined) : undefined,
      })

      setResult(data)
    } catch (err: any) {
      setError(err.message || 'Failed to generate video')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold">Kling Video</h1>

      <form onSubmit={onSubmit} className="space-y-4 bg-white rounded-lg shadow p-6">
        <div>
          <label className="block text-sm mb-1">Model</label>
            <select value={model} onChange={(e) => setModel(e.target.value as Model)} className="w-full border rounded p-2">
            <option value="kling-v3-pro">Kling 3 Pro</option>
            <option value="kling-v3-std">Kling 3 Standard</option>
            <option value="kling-v26-pro">Kling 2.6 Pro</option>
            <option value="kling-v25-pro">Kling 2.5 Pro</option>
            <option value="kling-v26-motion-control-pro">Kling 2.6 Motion Control Pro</option>
            <option value="kling-v26-motion-control-std">Kling 2.6 Motion Control Std</option>
          </select>
        </div>

        {!isMotion && !isKling3 && (
          <div>
            <label className="block text-sm mb-1">
              Prompt <span className="text-xs text-gray-500">({is26 && !isImageMode ? 'Required' : 'Optional'})</span>
            </label>
            <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} rows={4} className="w-full border rounded p-2" />
            <p className="text-xs text-gray-600 mt-1">
              Text prompt describing desired motion in video, cannot exceed 2500 characters.
            </p>
          </div>
        )}

        {isMotion && (
          <>
            <div>
              <label className="block text-sm mb-1">Prompt (optional)</label>
              <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} rows={3} className="w-full border rounded p-2" />
              <p className="text-xs text-gray-600 mt-1">
                Optional text prompt to guide the motion transfer. Cannot exceed 2500 characters.
              </p>
            </div>
            <div>
              <label className="block text-sm mb-1">Video URL (required)</label>
              <input value={videoUrl} onChange={(e) => setVideoUrl(e.target.value)} className="w-full border rounded p-2" placeholder="https://..." />
              <p className="text-xs text-gray-600 mt-1">
                URL of the reference video containing the motion to transfer. Must be publicly accessible, 3-30 seconds, and MP4/MOV/WEBM/M4V.
              </p>
            </div>
          </>
        )}

        {isKling3 && (
          <div>
            <label className="block text-sm mb-1">
              Prompt <span className="text-xs text-gray-500">(Optional if image provided)</span>
            </label>
            <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} rows={4} className="w-full border rounded p-2" />
            <p className="text-xs text-gray-600 mt-1">
              Text prompt describing the video. Cannot exceed 2500 characters.
            </p>
          </div>
        )}

        <div>
          <label className="block text-sm mb-1">
            Image Input <span className="text-xs text-gray-500">({is25 || isMotion ? 'Required' : 'Optional'})</span>
          </label>
          {!isMotion && (
            <div className="flex gap-2 mb-2">
              <button type="button" onClick={() => { setImageMode('url'); setImageUrl('') }} className={`px-3 py-1 rounded ${imageMode === 'url' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>URL</button>
              <button type="button" onClick={() => { setImageMode('upload'); setImageUrl('') }} className={`px-3 py-1 rounded ${imageMode === 'upload' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>Upload File</button>
            </div>
          )}
          {isMotion ? (
            <input value={imageUrl} onChange={(e) => setImageUrl(e.target.value)} className="w-full border rounded p-2" placeholder="https://..." />
          ) : imageMode === 'url' ? (
            <input value={imageUrl} onChange={(e) => setImageUrl(e.target.value)} className="w-full border rounded p-2" placeholder="https://..." />
          ) : (
            <div>
              <input type="file" accept="image/png,image/jpeg,image/webp" onChange={(e) => onUploadImage(e.target.files?.[0] || null)} className="w-full border rounded p-2" />
              {imageUrl && <p className="text-xs text-green-700 mt-1">Image loaded as base64 ({Math.round(imageUrl.length / 1024)} KB)</p>}
            </div>
          )}
          <p className="text-xs text-gray-600 mt-1">
            {isMotion
              ? 'URL of the character/reference image. Must be publicly accessible, minimum 300x300, maximum 10MB, formats JPG/JPEG/PNG/WEBP.'
              : 'Reference image supports Base64 or URL. File size cannot exceed 10MB, resolution should not be less than 300x300, and aspect ratio should be between 1:2.5 and 2.5:1.'}
          </p>
        </div>

        {!isMotion && !isKling3 && (
          <div>
            <label className="block text-sm mb-1">Duration <span className="text-xs text-gray-500">(Required)</span></label>
            <select value={String(duration)} onChange={(e) => setDuration(Number(e.target.value))} className="w-full border rounded p-2">
              <option value="5">5</option>
              <option value="10">10</option>
            </select>
            <p className="text-xs text-gray-600 mt-1">Duration of the generated video in seconds. Allowed values: 5 or 10.</p>
          </div>
        )}

        {isKling3 && (
          <div>
            <label className="block text-sm mb-1">Duration <span className="text-xs text-gray-500">(Required)</span></label>
            <select value={String(duration)} onChange={(e) => setDuration(Number(e.target.value))} className="w-full border rounded p-2">
              {Array.from({length: 13}, (_, i) => i + 3).map(n => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
            <p className="text-xs text-gray-600 mt-1">Duration of the generated video in seconds. Allowed values: 3-15.</p>
          </div>
        )}

        {!isMotion && !isKling3 && (
          <div>
            <label className="block text-sm mb-1">Negative Prompt <span className="text-xs text-gray-500">(Optional)</span></label>
            <textarea value={negativePrompt} onChange={(e) => setNegativePrompt(e.target.value)} rows={3} className="w-full border rounded p-2" />
            <p className="text-xs text-gray-600 mt-1">
              Text prompt describing what to avoid in the generated video, cannot exceed 2500 characters.
            </p>
          </div>
        )}

        {!isKling3 && (
          <div>
            <label className="block text-sm mb-1">CFG Scale: {cfgScale} <span className="text-xs text-gray-500">(Optional)</span></label>
            <input type="range" min={0} max={1} step={0.05} value={cfgScale} onChange={(e) => setCfgScale(Number(e.target.value))} className="w-full" />
            <p className="text-xs text-gray-600 mt-1">
              {isMotion
                ? "The CFG (Classifier Free Guidance) scale controls how closely the model follows the prompt. Higher values mean stronger adherence to the prompt but less flexibility."
                : "Flexibility in generation; the higher the value, the lower the model's degree of flexibility, and the stronger the relevance to the prompt."}
            </p>
          </div>
        )}

        {(is26 || isKling3) && (
          <>
            <div>
              <label className="block text-sm mb-1">Aspect Ratio <span className="text-xs text-gray-500">(Optional)</span></label>
              <select value={aspectRatio} onChange={(e) => setAspectRatio(e.target.value)} className="w-full border rounded p-2">
                {isKling3 ? (
                  <>
                    <option value="16:9">16:9</option>
                    <option value="9:16">9:16</option>
                    <option value="1:1">1:1</option>
                  </>
                ) : (
                  <>
                    <option value="widescreen_16_9">Widescreen 16:9</option>
                    <option value="social_story_9_16">Social Story 9:16</option>
                    <option value="square_1_1">Square 1:1</option>
                  </>
                )}
              </select>
              <p className="text-xs text-gray-600 mt-1">
                Aspect ratio for the generated video.
              </p>
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={generateAudio} onChange={(e) => setGenerateAudio(e.target.checked)} />
              Generate Audio <span className="text-xs text-gray-500">(Optional)</span>
            </label>
            <p className="text-xs text-gray-600 -mt-2">
              Whether to generate audio for the video.
            </p>
          </>
        )}

        {isKling3 && (
          <>
            <div>
              <label className="block text-sm mb-1">End Image URL <span className="text-xs text-gray-500">(Optional)</span></label>
              <input value={endImageUrl} onChange={(e) => setEndImageUrl(e.target.value)} className="w-full border rounded p-2" placeholder="https://..." />
              <p className="text-xs text-gray-600 mt-1">
                URL of the last frame image. Must be publicly accessible.
              </p>
            </div>
            <div>
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={multiShot} onChange={(e) => setMultiShot(e.target.checked)} />
                Multi-Shot <span className="text-xs text-gray-500">(Optional)</span>
              </label>
              <p className="text-xs text-gray-600">Enable multi-shot generation.</p>
            </div>
            {multiShot && (
              <div>
                <label className="block text-sm mb-1">Shot Type</label>
                <select value={shotType} onChange={(e) => setShotType(e.target.value)} className="w-full border rounded p-2">
                  <option value="default">Default</option>
                  <option value="close_up">Close Up</option>
                  <option value="medium_shot">Medium Shot</option>
                  <option value="long_shot">Long Shot</option>
                  <option value="extreme_close_up">Extreme Close Up</option>
                  <option value="extreme_long_shot">Extreme Long Shot</option>
                  <option value="over_the_shoulder">Over The Shoulder</option>
                  <option value="point_of_view">Point of View</option>
                </select>
              </div>
            )}
            {multiShot && (
              <div>
                <label className="block text-sm mb-1">Multi Prompt <span className="text-xs text-gray-500">(Optional)</span></label>
                <textarea value={multiPrompt} onChange={(e) => setMultiPrompt(e.target.value)} rows={3} className="w-full border rounded p-2" placeholder="Prompt for multi-shot generation" />
              </div>
            )}
          </>
        )}

        {isMotion && (
          <div>
            <label className="block text-sm mb-1">Character Orientation <span className="text-xs text-gray-500">(Optional)</span></label>
            <select value={characterOrientation} onChange={(e) => setCharacterOrientation(e.target.value as 'video' | 'image')} className="w-full border rounded p-2">
              <option value="video">Match Video Orientation</option>
              <option value="image">Match Image Orientation</option>
            </select>
            <p className="text-xs text-gray-600 mt-1">
              How the model interprets spatial information and constrains output duration. video: orientation matches reference video (max output 30s). image: orientation matches reference image (max output 10s).
            </p>
          </div>
        )}

        <button disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50">
          {loading ? 'Submitting...' : 'Generate'}
        </button>
      </form>

      {error && <p className="text-red-600">{error}</p>}
      {result && <pre className="bg-black text-green-300 p-3 rounded text-xs overflow-auto">{JSON.stringify(result, null, 2)}</pre>}
    </div>
  )
}
