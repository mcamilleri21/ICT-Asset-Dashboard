import { useState, useEffect } from 'react'
import { fetchServices } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'

function truncate(str, n) {
  if (!str) return '—'
  return str.length > n ? str.slice(0, n) + '…' : str
}

export default function Services() {
  const [services, setServices] = useState([])
  const [loading, setLoading]  = useState(true)
  const [error, setError]      = useState(null)

  useEffect(() => {
    fetchServices()
      .then(setServices)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner />

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Services</h1>

      {error && (
        <div className="border border-red-300 bg-red-50 rounded-xl p-4 text-red-700 text-sm mb-4">
          {error}
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50">
              {['Service ID', 'Description', 'Category', 'Contract', 'Critical', 'Locations'].map(h => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {services.map(s => (
              <tr key={s.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-mono text-xs text-gray-500">{s.service_ref}</td>
                <td className="px-4 py-3 text-gray-800">{truncate(s.service_description, 80)}</td>
                <td className="px-4 py-3">
                  <span className="rounded-full px-2 py-0.5 text-xs font-semibold bg-blue-100 text-blue-700">
                    {s.ict_service_category}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-600 font-mono text-xs">{s.contract_id}</td>
                <td className="px-4 py-3">
                  {s.is_critical_or_important
                    ? <span className="rounded-full px-2 py-0.5 text-xs font-semibold bg-red-100 text-red-700">YES</span>
                    : <span className="text-gray-400">—</span>}
                </td>
                <td className="px-4 py-3 text-gray-600">{(s.locations ?? []).length || '—'}</td>
              </tr>
            ))}
            {services.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-400 text-sm">
                  No services found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
