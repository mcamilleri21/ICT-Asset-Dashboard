import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import Sidebar       from './components/Sidebar'
import Dashboard     from './pages/Dashboard'
import Contracts     from './pages/Contracts'
import ContractDetail from './pages/ContractDetail'
import Providers     from './pages/Providers'
import Services      from './pages/Services'
import AssetMap      from './pages/AssetMap'

function Layout({ children }) {
  const { pathname } = useLocation()
  const isAssetMap = pathname === '/asset-map'
  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <Sidebar />
      <main style={{
        marginLeft: 256,
        flex: 1,
        overflow: isAssetMap ? 'hidden' : 'auto',
        background: isAssetMap ? 'transparent' : '#f9fafb',
        height: '100vh',
      }}>
        {children}
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
          <Route path="/asset-map"     element={<AssetMap />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
