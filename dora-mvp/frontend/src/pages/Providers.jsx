import { useState, useEffect } from 'react'
import { fetchProviders } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'

const TYPE_COLORS = {
  ict_third_party: 'bg-blue-100 text-blue-700',
  intra_group:     'bg-purple-100 text-purple-700',
  subcontractor:   'bg-gray-100 text-gray-600',
}

export default function Providers() {
  const [providers, setProviders] = useState([])
  const [loading, setLoading]    = useState(true)
  const [error, setError]        = useState(null)

  useEffect(() => {
    fetchProviders()
      .then(setProviders)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner />

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Providers</h1>

      {error && (
        <div className="border border-red-300 bg-red-50 rounded-xl p-4 text-red-700 text-sm mb-4">
          {error}
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50">
              {['Legal Name', 'Trading Name', 'Country', 'Type', 'LEI', 'Parent Company'].map(h => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {providers.map(p => (
              <tr key={p.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900">{p.legal_name}</td>
                <td className="px-4 py-3 text-gray-600">{p.trading_name ?? '—'}</td>
                <td className="px-4 py-3 text-gray-600">{p.country_of_incorporation ?? '—'}</td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                    TYPE_COLORS[p.provider_type] ?? 'bg-gray-100 text-gray-600'
                  }`}>
                    {(p.provider_type ?? '').replace(/_/g, ' ')}
                  </span>
                </td>
                <td className="px-4 py-3 font-mono text-xs text-gray-500">{p.lei ?? '—'}</td>
                <td className="px-4 py-3 text-gray-600">{p.parent_company ?? '—'}</td>
              </tr>
            ))}
            {providers.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-400 text-sm">
                  No providers found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
