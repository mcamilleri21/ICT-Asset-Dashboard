import { useState, useEffect, useRef } from 'react'
import { fetchSummary, uploadExcel } from '../api/client'

const RATING_COLORS = {
  GREEN: 'text-green-400',
  AMBER: 'text-amber-400',
  RED:   'text-red-400',
  GREY:  'text-gray-400',
}

const RATING_BG = {
  GREEN: 'bg-green-900/40 border-green-700',
  AMBER: 'bg-amber-900/40 border-amber-700',
  RED:   'bg-red-900/40 border-red-700',
  GREY:  'bg-gray-800/40 border-gray-600',
}

function KpiCard({ label, value, sub }) {
  return (
    <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
      <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">{label}</p>
      <p className="text-3xl font-bold text-white">{value ?? '—'}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  )
}

function ScoreDistCard({ dist }) {
  if (!dist) return null
  return (
    <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
      <p className="text-xs text-gray-400 uppercase tracking-wider mb-3">DORA Score Distribution</p>
      <div className="flex gap-3 flex-wrap">
        {['GREEN', 'AMBER', 'RED', 'GREY'].map(r => (
          <div key={r} className={`flex-1 min-w-[56px] rounded-lg border p-2 text-center ${RATING_BG[r]}`}>
            <p className={`text-xl font-bold ${RATING_COLORS[r]}`}>{dist[r] ?? 0}</p>
            <p className="text-[10px] text-gray-400 uppercase">{r}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

function UploadCard({ onSuccess }) {
  const fileRef = useRef(null)
  const [importing, setImporting] = useState(false)
  const [result, setResult]     = useState(null)
  const [error, setError]       = useState(null)

  async function handleImport() {
    const file = fileRef.current?.files?.[0]
    if (!file) return
    setImporting(true)
    setError(null)
    setResult(null)
    try {
      const res = await uploadExcel(file)
      setResult(res)
      setTimeout(() => onSuccess(), 1500)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Import failed')
    } finally {
      setImporting(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto mt-24 bg-gray-800 rounded-2xl border border-gray-700 p-8 shadow-xl">
      <h2 className="text-xl font-semibold text-white mb-2">Get started — upload your data file</h2>
      <p className="text-sm text-gray-400 mb-6">
        Upload your Excel workbook (.xlsx) containing the ROI sheet to import your providers and
        contracts. Once imported, use the DORA Platform to add clause checklists and risk assessments.
      </p>

      <div className="flex items-center gap-3">
        <input
          ref={fileRef}
          type="file"
          accept=".xlsx"
          className="block text-sm text-gray-300 file:mr-3 file:py-2 file:px-4 file:rounded-lg
                     file:border-0 file:text-sm file:font-medium file:bg-indigo-600
                     file:text-white hover:file:bg-indigo-700 file:cursor-pointer"
        />
        <button
          onClick={handleImport}
          disabled={importing}
          className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm
                     font-medium transition disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
        >
          {importing ? 'Importing…' : 'Import workbook'}
        </button>
      </div>

      {result && (
        <p className="mt-4 text-sm text-green-400">
          Imported {result.contracts_created} contracts from {result.providers_created} providers.
          {result.services_created > 0 && ` (${result.services_created} services)`}
        </p>
      )}
      {error && (
        <p className="mt-4 text-sm text-red-400">{error}</p>
      )}
    </div>
  )
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [fetchError, setFetchError] = useState(null)

  async function load() {
    setLoading(true)
    setFetchError(null)
    try {
      setSummary(await fetchSummary())
    } catch (e) {
      setFetchError(e.message || 'Could not reach API')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="border-b border-gray-800 px-8 py-4">
        <h1 className="text-lg font-semibold tracking-tight">DORA Contract Intelligence Platform</h1>
      </header>

      <main className="px-8 py-8">
        {loading && (
          <p className="text-gray-400 text-sm">Loading…</p>
        )}

        {fetchError && (
          <p className="text-red-400 text-sm">
            API error: {fetchError}. Make sure the backend is running on port 8000.
          </p>
        )}

        {!loading && !fetchError && summary?.total_contracts === 0 && (
          <UploadCard onSuccess={load} />
        )}

        {!loading && !fetchError && summary?.total_contracts > 0 && (
          <>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
              <KpiCard label="Total Contracts"     value={summary.total_contracts} />
              <KpiCard label="Active Contracts"    value={summary.active_contracts} />
              <KpiCard label="Critical Services"   value={summary.critical_services} />
              <KpiCard label="Contracts with Gaps" value={summary.contracts_with_gaps}
                sub="RED or AMBER rated active contracts" />
              <KpiCard label="Expiring Soon"       value={summary.expiring_soon_count}
                sub="within 90 days" />
              <ScoreDistCard dist={summary.score_distribution} />
            </div>

            <p className="text-xs text-gray-600 mt-2">
              Use the API at{' '}
              <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer"
                 className="underline hover:text-gray-400">
                localhost:8000/docs
              </a>{' '}
              to manage contracts, clauses, and risk assessments.
            </p>
          </>
        )}
      </main>
    </div>
  )
}
