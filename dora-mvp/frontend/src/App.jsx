import { useRef, useState } from 'react'
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import { ExternalLink, Activity } from 'lucide-react'
import Sidebar        from './components/Sidebar'
import Dashboard      from './pages/Dashboard'
import Contracts      from './pages/Contracts'
import ContractDetail from './pages/ContractDetail'
import Providers      from './pages/Providers'
import Services       from './pages/Services'

function Layout({ children }) {
  const { pathname } = useLocation()
  const isAssetMap   = pathname === '/asset-map'

  const iframeRef                   = useRef(null)
  const [doraActive, setDoraActive] = useState(false)

  const triggerDoraOverlay = () => {
    try { iframeRef.current?.contentWindow?.fetchDoraScores?.() } catch (_) {}
  }
  const toggleDora = () => {
    const next = !doraActive
    setDoraActive(next)
    if (next) triggerDoraOverlay()
  }

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <Sidebar />
      <main style={{ marginLeft: 256, flex: 1, overflow: 'hidden', height: '100vh' }}>

        {/* Regular page content — hidden while on /asset-map */}
        <div style={{
          display: isAssetMap ? 'none' : 'flex',
          flexDirection: 'column',
          height: '100vh',
          overflow: 'auto',
          background: '#f9fafb',
        }}>
          {children}
        </div>

        {/* Persistent AssetMap — always mounted so the iframe is never destroyed */}
        <div style={{
          display: isAssetMap ? 'flex' : 'none',
          flexDirection: 'column',
          height: '100vh',
        }}>
          <div
            className="bg-white border-b border-gray-200 px-4 flex items-center justify-end flex-shrink-0"
            style={{ height: 40 }}
          >
            <div className="flex items-center gap-2">
              <button
                onClick={toggleDora}
                className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium border transition-colors ${
                  doraActive
                    ? 'bg-blue-50 border-blue-300 text-blue-700'
                    : 'bg-white border-gray-300 text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Activity size={13} /> DORA scores
              </button>
              <a
                href="/asset-dashboard.html"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium border border-gray-300 bg-white text-gray-600 hover:bg-gray-50 transition-colors"
              >
                <ExternalLink size={13} /> Full tab
              </a>
            </div>
          </div>
          <iframe
            ref={iframeRef}
            src="/asset-dashboard.html"
            title="ICT Asset Relationship Dashboard"
            frameBorder="0"
            style={{ flex: 1, width: '100%', border: 'none', display: 'block' }}
          />
        </div>

      </main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/"              element={<Dashboard />} />
          <Route path="/contracts"     element={<Contracts />} />
          <Route path="/contracts/:id" element={<ContractDetail />} />
          <Route path="/providers"     element={<Providers />} />
          <Route path="/services"      element={<Services />} />
          <Route path="/asset-map"     element={null} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
