'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { saveApiKeys, getApiKeys, verifyApiKey } from '@/lib/api'

export default function SettingsPage() {
  const [keys, setKeys] = useState<string[]>([''])
  const [webhookUrl, setWebhookUrl] = useState('')
  const [webhookSecret, setWebhookSecret] = useState('')
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [verifyMessage, setVerifyMessage] = useState('')
  const [verifyDetails, setVerifyDetails] = useState<any>(null)
  const [verifyingIndex, setVerifyingIndex] = useState<number | null>(null)

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      const config = await getApiKeys()
      setKeys(config.keys.length > 0 ? config.keys : [''])
      setWebhookUrl(config.webhook_url || '')
    } catch (error) {
      console.error('Failed to load config:', error)
    }
  }

  const addKey = () => {
    if (keys.length < 5) {
      setKeys([...keys, ''])
    }
  }

  const updateKey = (index: number, value: string) => {
    const newKeys = [...keys]
    newKeys[index] = value
    setKeys(newKeys)
  }

  const removeKey = (index: number) => {
    setKeys(keys.filter((_, i) => i !== index))
  }

  const handleSave = async () => {
    setSaving(true)
    setMessage('')

    try {
      const filteredKeys = keys.filter(k => k.trim())
      
      if (filteredKeys.length === 0) {
        setMessage('At least one API key is required')
        setSaving(false)
        return
      }

      await saveApiKeys({
        keys: filteredKeys,
        webhook_url: webhookUrl,
        webhook_secret: webhookSecret
      })

      setMessage('Configuration saved successfully!')
      setTimeout(() => setMessage(''), 3000)
    } catch (error: any) {
      setMessage(`Error: ${error.message}`)
    } finally {
      setSaving(false)
    }
  }

  const handleVerifyKey = async (index: number) => {
    const key = keys[index]?.trim()
    if (!key || key.startsWith('****')) {
      setVerifyMessage('Enter a full API key to verify (masked keys cannot be verified).')
      return
    }

    setVerifyingIndex(index)
    setVerifyMessage('')
    setVerifyDetails(null)
    try {
      const result = await verifyApiKey(key)
      setVerifyMessage(result.message || (result.valid ? 'API key is valid' : 'API key is invalid'))
      setVerifyDetails(result)
    } catch (error: any) {
      setVerifyMessage(`Verification error: ${error.message}`)
    } finally {
      setVerifyingIndex(null)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="mb-4">
          <Link href="/" className="inline-block text-sm text-blue-700 hover:underline">← Back to Home</Link>
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Settings</h1>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">API Keys (Max 5)</h2>
            <span className="text-sm text-gray-500">{keys.length}/5 keys</span>
          </div>

          <div className="space-y-3 mb-4">
            {keys.map((key, index) => (
              <div key={index} className="flex gap-2">
                <input
                  type="password"
                  value={key}
                  onChange={(e) => updateKey(index, e.target.value)}
                  placeholder={`API Key ${index + 1}`}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  onClick={() => handleVerifyKey(index)}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition"
                >
                  {verifyingIndex === index ? 'Verifying...' : 'Verify'}
                </button>
                <button
                  onClick={() => removeKey(index)}
                  className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>

          {keys.length < 5 && (
            <button
              onClick={addKey}
              className="w-full py-2 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 text-gray-600 hover:text-blue-500 transition"
            >
              + Add API Key
            </button>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Webhook Configuration</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Webhook URL
              </label>
              <input
                type="url"
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                placeholder="https://yourdomain.com/api/webhooks/magnific"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-sm text-gray-500 mt-1">
                This URL will receive webhook notifications when tasks complete
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Webhook Secret (Optional)
              </label>
              <input
                type="password"
                value={webhookSecret}
                onChange={(e) => setWebhookSecret(e.target.value)}
                placeholder="Your webhook secret for HMAC verification"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-sm text-gray-500 mt-1">
                Used for HMAC-SHA256 signature verification
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {saving ? 'Saving...' : 'Save Configuration'}
          </button>

          {message && (
            <span className={`text-sm ${message.includes('Error') ? 'text-red-600' : 'text-green-600'}`}>
              {message}
            </span>
          )}
          {verifyMessage && (
            <span className={`text-sm ${verifyMessage.toLowerCase().includes('valid') ? 'text-green-600' : 'text-red-600'}`}>
              {verifyMessage}
            </span>
          )}
        </div>

        {verifyDetails && (
          <div className="mt-3 rounded-lg border border-gray-200 bg-gray-50 p-3">
            <p className="text-sm text-gray-800">
              <strong>Status:</strong> {String(verifyDetails.status_code ?? 'n/a')} {verifyDetails.reason ?? ''}
            </p>
            <p className="text-sm text-gray-800 mt-1">
              <strong>Raw response from Magnific:</strong>
            </p>
            <pre className="mt-2 max-h-56 overflow-auto rounded bg-black text-green-300 p-3 text-xs whitespace-pre-wrap break-words">
{verifyDetails.raw_response ? String(verifyDetails.raw_response) : 'No response body'}
            </pre>
          </div>
        )}

        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">Important Notes:</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• API keys are hashed and stored securely</li>
            <li>• Keys are rotated automatically based on quota availability</li>
            <li>• Webhook URL must be publicly accessible for notifications</li>
            <li>• For local testing, use ngrok to expose your webhook endpoint</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
