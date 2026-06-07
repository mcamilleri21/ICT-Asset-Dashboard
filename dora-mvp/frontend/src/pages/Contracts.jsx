import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchContracts } from '../api/client'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'

function expiryClass(dateStr) {
  if (!dateStr) return 'text-gray-600'
  const diff = (new Date(dateStr) - new Date()) / 86400000
  if (diff < 0)  return 'text-red-600 font-semibold'
  if (diff < 90) return 'text-amber-600 font-semibold'
  return 'text-gray-600'
}

export default function Contracts() {
  const navigate                        = useNavigate()
  const [contracts, setContracts]       = useState([])
  const [loading, setLoading]           = useState(true)
  const [error, setError]               = useState(null)
  const [search, setSearch]             = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  useEffect(() => {
    fetchContracts()
      .then(setContracts)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const filtered = contracts.filter(c => {
    const q = search.toLowerCase()
    const matchSearch = !q ||
      c.contract_name?.toLowerCase().includes(q) ||
      c.contract_ref?.toLowerCase().includes(q)
    const matchStatus = !statusFilter || c.contract_status === statusFilter
    return matchSearch && matchStatus
  })

  if (loading) return <LoadingSpinner />

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Contracts</h1>

      {error && (
        <div className="border border-red-300 bg-red-50 rounded-xl p-4 text-red-700 text-sm mb-4">
          {error}
        </div>
      )}

      <div className="flex gap-3 mb-4">
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search by name or ref…"
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-64
                     focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm
                     focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All statuses</option>
          <option value="active">Active</option>
          <option value="draft">Draft</option>
          <option value="expired">Expired</option>
          <option value="terminated">Terminated</option>
        </select>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50">
              {['Contract ID', 'Name', 'Provider', 'Status', 'Critical', 'DORA Score', 'Expiry'].map(h => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filtered.map(c => (
              <tr
                key={c.id}
                className="hover:bg-gray-50 cursor-pointer"
                onClick={() => navigate(`/contracts/${c.id}`)}
              >
                <td className="px-4 py-3 font-mono text-xs text-gray-500">{c.contract_ref}</td>
                <td className="px-4 py-3 font-medium text-gray-900 max-w-xs truncate">
                  {c.contract_name}
                </td>
                <td className="px-4 py-3 text-gray-600">{c.provider_legal_name}</td>
                <td className="px-4 py-3">
                  <StatusBadge value={c.contract_status} type="status" />
                </td>
                <td className="px-4 py-3">
                  {c.has_critical_service
                    ? <span className="rounded-full px-2 py-0.5 text-xs font-semibold bg-green-100 text-green-800">YES</span>
                    : <span className="text-gray-400">—</span>}
                </td>
                <td className="px-4 py-3">
                  {c.dora_rating
                    ? <StatusBadge value={c.dora_rating} type="score" />
                    : <span className="text-gray-400">—</span>}
                </td>
                <td className={`px-4 py-3 ${expiryClass(c.expiry_date)}`}>
                  {c.expiry_date ?? '—'}
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-gray-400 text-sm">
                  No contracts found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
