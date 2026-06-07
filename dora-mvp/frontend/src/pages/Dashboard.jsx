import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileText, AlertTriangle, AlertCircle, Clock, Network } from 'lucide-react'
import {
  PieChart, Pie, Cell,
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend,
  ResponsiveContainer,
} from 'recharts'
import { fetchDashboardSummary, fetchClauseGaps, fetchProviderRisk, uploadExcel } from '../api/client'
import KPICard from '../components/KPICard'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'

const DORA_COLORS = {
  GREEN: '#22c55e',
  AMBER: '#f59e0b',
  RED:   '#ef4444',
  GREY:  '#9ca3af',
}

function fmt(ct) {
  return ct.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

function UploadCard({ onSuccess }) {
  const fileRef               = useRef(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult]   = useState(null)
  const [error, setError]     = useState(null)

  async function handleImport() {
    const file = fileRef.current?.files?.[0]
    if (!file) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await uploadExcel(file)
      setResult(res)
      setTimeout(onSuccess, 2500)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Import failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto mt-16">
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Get started — upload your data file
        </h2>
        <p className="text-sm text-gray-500 mb-6">
          Upload your Excel workbook (.xlsx) containing the ROI sheet to import your providers and
          contracts. Once imported, run{' '}
          <code className="font-mono bg-gray-100 px-1 rounded text-xs">seed_demo_compliance.py</code>{' '}
          to add DORA demo data.
        </p>
        <div className="flex items-center gap-3 flex-wrap">
          <input
            ref={fileRef}
            type="file"
            accept=".xlsx"
            className="text-sm text-gray-600
                       file:mr-3 file:py-2 file:px-4 file:rounded-lg
                       file:border-0 file:text-sm file:font-medium
                       file:bg-blue-600 file:text-white
                       hover:file:bg-blue-700 file:cursor-pointer"
          />
          <button
            onClick={handleImport}
            disabled={loading}
            className="px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white
                       text-sm font-medium transition disabled:opacity-50 whitespace-nowrap"
          >
            {loading ? 'Importing…' : 'Import workbook'}
          </button>
        </div>
        {result && (
          <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
            <p className="text-sm text-green-700 font-medium">
              ✓ Imported {result.contracts_created} contract(s) from {result.providers_created} provider(s).
            </p>
            <p className="text-xs text-green-600 mt-1">
              Now run{' '}
              <code className="font-mono bg-green-100 px-1 rounded">
                python backend/seed_demo_compliance.py
              </code>{' '}
              in the dora-mvp/ directory to add demo DORA clause data, then refresh.
            </p>
          </div>
        )}
        {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
      </div>
    </div>
  )
}

export default function Dashboard() {
  const navigate                      = useNavigate()
  const [summary, setSummary]         = useState(null)
  const [clauseGaps, setClauseGaps]   = useState([])
  const [provRisk, setProvRisk]       = useState([])
  const [loading, setLoading]         = useState(true)
  const [error, setError]             = useState(null)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const [s, cg, pr] = await Promise.all([
        fetchDashboardSummary(),
        fetchClauseGaps(),
        fetchProviderRisk(),
      ])
      setSummary(s)
      setClauseGaps(cg)
      setProvRisk(pr)
    } catch (e) {
      setError(e.message || 'Could not reach API')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  if (loading) return <LoadingSpinner />

  if (error) return (
    <div className="p-8">
      <div className="border border-red-300 bg-red-50 rounded-xl p-4 text-red-700 text-sm">
        API error: {error}. Ensure the backend is running on port 8000.
      </div>
    </div>
  )

  if (!summary || summary.total_contracts === 0) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>
        <UploadCard onSuccess={load} />
      </div>
    )
  }

  const dist = summary.score_distribution ?? {}
  const pieData = Object.entries(dist)
    .filter(([, v]) => v > 0)
    .map(([name, value]) => ({ name, value }))

  const barData = clauseGaps.slice(0, 8).map(g => ({
    name:    fmt(g.clause_type),
    Missing: g.missing_count ?? 0,
    Partial: g.partial_count ?? 0,
  }))

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

      {/* KPI cards */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <KPICard title="Total Contracts"    value={summary.total_contracts}    icon={FileText}      color="blue" />
        <KPICard title="Critical Services"  value={summary.critical_services}  icon={AlertTriangle} color="amber" />
        <KPICard
          title="DORA Gaps"
          value={summary.contracts_with_gaps}
          icon={AlertCircle}
          color="red"
          subtitle="Active RED or AMBER contracts"
        />
        <KPICard
          title="Expiring Soon"
          value={summary.expiring_soon_count}
          icon={Clock}
          color="amber"
          subtitle="Within 90 days"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <h3 className="font-semibold text-gray-700 mb-4">DORA Score Distribution</h3>
          <div style={{ height: 288 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={95}
                  label={({ name, value }) => `${name} ${value}`}
                >
                  {pieData.map(entry => (
                    <Cell key={entry.name} fill={DORA_COLORS[entry.name] ?? '#9ca3af'} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <h3 className="font-semibold text-gray-700 mb-4">Top Missing DORA Clauses</h3>
          <div style={{ height: 288 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} margin={{ top: 0, right: 4, left: -20, bottom: 64 }}>
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 10 }}
                  angle={-35}
                  textAnchor="end"
                  interval={0}
                />
                <YAxis tick={{ fontSize: 10 }} allowDecimals={false} />
                <Tooltip />
                <Legend verticalAlign="top" height={28} iconSize={10} wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey="Missing" fill="#ef4444" maxBarSize={28} />
                <Bar dataKey="Partial" fill="#f59e0b" maxBarSize={28} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Provider risk table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <h3 className="font-semibold text-gray-700">Provider Risk Overview</h3>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50">
              {['Provider', 'Contracts', 'Critical Services', 'Risk Rating'].map(h => (
                <th key={h} className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {provRisk.length === 0 && (
              <tr>
                <td colSpan={4} className="px-6 py-8 text-center text-gray-400 text-sm">
                  No provider data
                </td>
              </tr>
            )}
            {provRisk.map(p => (
              <tr
                key={p.provider_id}
                className="hover:bg-gray-50 cursor-pointer"
                onClick={() => navigate('/providers')}
              >
                <td className="px-6 py-3 font-medium text-gray-900">{p.provider_name}</td>
                <td className="px-6 py-3 text-gray-600">{p.contract_count}</td>
                <td className="px-6 py-3 text-gray-600">{p.critical_service_count}</td>
                <td className="px-6 py-3">
                  {p.risk_rating
                    ? <StatusBadge value={p.risk_rating} type="risk" />
                    : <span className="text-gray-400 text-xs">—</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Asset Map shortcut */}
      <div
        className="mt-6 bg-white rounded-xl border border-gray-200 p-4 cursor-pointer hover:shadow-sm transition-shadow flex items-center justify-between"
        onClick={() => navigate('/asset-map')}
      >
        <div>
          <p className="text-sm font-semibold text-gray-900">
            View full asset dependency graph →
          </p>
          <p className="text-xs text-gray-500 mt-0.5">
            See all hardware, software, information assets, roles and providers
            in the interactive network graph.
          </p>
        </div>
        <div className="flex-shrink-0 ml-4 p-2 bg-blue-100 rounded-lg">
          <Network size={20} className="text-blue-600" />
        </div>
      </div>
    </div>
  )
}
