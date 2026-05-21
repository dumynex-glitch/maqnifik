export default function HomePage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Magnific API Integration
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Multi-key API management with quota tracking and webhook handling
        </p>
        <div className="space-y-4">
          <div className="bg-white rounded-lg shadow-md p-6 max-w-md mx-auto">
            <h2 className="text-xl font-semibold mb-2">Getting Started</h2>
            <p className="text-gray-600 mb-4">
              Configure your API keys and webhook URL in Settings to begin.
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              <a
                href="/settings"
                className="inline-block bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
              >
                Settings
              </a>
              <a href="/video" className="inline-block bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-black transition">Video</a>
              <a href="/image" className="inline-block bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-black transition">Image</a>
              <a href="/editing" className="inline-block bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-black transition">Editing</a>
              <a href="/audio" className="inline-block bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-black transition">Audio</a>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6 max-w-md mx-auto">
            <h2 className="text-xl font-semibold mb-2">Features</h2>
            <ul className="text-left text-gray-600 space-y-2">
              <li>✓ Multi-API key support (up to 5 keys)</li>
              <li>✓ Automatic key rotation with quota tracking</li>
              <li>✓ Webhook-based async task handling</li>
              <li>✓ Video, image, and audio generation</li>
              <li>✓ Image editing tools</li>
              <li>✓ Gallery with favorites</li>
              <li>✓ Real-time logging</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
