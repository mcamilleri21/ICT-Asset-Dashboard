import { useState, useRef } from 'react'
import { ExternalLink, Activity } from 'lucide-react'

export default function AssetMap() {
  const iframeRef               = useRef(null)
  const [doraActive, setDoraActive] = useState(false)

  const handleIframeLoad = () => {
    if (doraActive) triggerDoraOverlay()
  }

  const triggerDoraOverlay = () => {
    try {
      iframeRef.current?.contentWindow?.fetchDoraScores?.()
    } catch (e) { /* cross-origin guard */ }
  }

  const toggleDora = () => {
    const next = !doraActive
    setDoraActive(next)
    if (next) triggerDoraOverlay()
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Top bar */}
      <div
        className="bg-white border-b border-gray-200 px-4 flex items-center justify-between flex-shrink-0"
        style={{ height: 40 }}
      >
        <span className="text-sm font-medium text-gray-600">
          ICT Asset Relationship Dashboard
        </span>
        <div className="flex items-center gap-2">
          <button
            onClick={toggleDora}
            className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium border transition-colors ${
              doraActive
                ? 'bg-blue-50 border-blue-300 text-blue-700'
                : 'bg-white border-gray-300 text-gray-600 hover:bg-gray-50'
            }`}
            title="Overlay DORA compliance scores on provider nodes"
          >
            <Activity size={13} />
            DORA scores
          </button>
          <a
            href="/asset-dashboard.html"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium border border-gray-300 bg-white text-gray-600 hover:bg-gray-50 transition-colors"
            title="Open in full browser tab"
          >
            <ExternalLink size={13} />
            Full tab
          </a>
        </div>
      </div>

      {/* Full-height iframe */}
      <iframe
        ref={iframeRef}
        src="/asset-dashboard.html"
        title="ICT Asset Relationship Dashboard"
        frameBorder="0"
        allow="fullscreen"
        onLoad={handleIframeLoad}
        style={{ flex: 1, width: '100%', border: 'none', display: 'block' }}
      />
    </div>
  )
}
