import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Contracts from './pages/Contracts'
import ContractDetail from './pages/ContractDetail'
import Providers from './pages/Providers'
import Services from './pages/Services'

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-auto bg-gray-50">
          <Routes>
            <Route path="/"              element={<Dashboard />} />
            <Route path="/contracts"     element={<Contracts />} />
            <Route path="/contracts/:id" element={<ContractDetail />} />
            <Route path="/providers"     element={<Providers />} />
            <Route path="/services"      element={<Services />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
