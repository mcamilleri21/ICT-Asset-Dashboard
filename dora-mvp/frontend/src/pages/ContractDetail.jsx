import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { fetchContract, fetchContractDoraScore } from '../api/client'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'

const ALL_CLAUSE_TYPES = [
  'service_description', 'sla', 'incident_support', 'authority_cooperation',
  'audit_rights', 'subcontracting_controls', 'data_return', 'business_continuity',
  'exit_support', 'termination_rights', 'location_change_notification',
  'data_processing_location',
]

const SCORE_COLORS = {
  GREEN: '#22c55e',
  AMBER: '#f59e0b',
  RED:   '#ef4444',
  GREY:  '#9ca3af',
}

const TABS = ['Overview', 'Services', 'DORA Clauses', 'Risk']

function fmt(ct) {
  return ct.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

function InfoRow({ label, value }) {
  if (value === null || value === undefined || value === '') return null
  return (
    <div className="mb-3">
      <p className="text-xs text-gray-400 uppercase tracking-wide mb-0.5">{label}</p>
      <p className="text-sm text-gray-800 font-medium">{value}</p>
    </div>
  )
}

export default function ContractDetail() {
  const { id }                            = useParams()
  const [contract, setContract]           = useState(null)
  const [doraScore, setDoraScore]         = useState(null)
  const [tab, setTab]                     = useState('Overview')
  const [loading, setLoading]             = useState(true)
  const [error, setError]                 = useState(null)

  useEffect(() => {
    Promise.all([fetchContract(id), fetchContractDoraScore(id)])
      .then(([c, d]) => { setContract(c); setDoraScore(d) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <LoadingSpinner />

  if (error || !contract) return (
    <div className="p-8">
      <div className="border border-red-300 bg-red-50 rounded-xl p-4 text-red-700 text-sm">
        {error || 'Contract not found'}
      </div>
    </div>
  )

  const clauseMap = Object.fromEntries(
    (contract.clauses ?? []).map(c => [c.clause_type, c])
  )

  const clauseStatuses = ALL_CLAUSE_TYPES.map(ct => ({
    ct,
    status: doraScore?.clause_summary?.[ct] ?? 'no',
    clause: clauseMap[ct],
  }))

  const completedCount = clauseStatuses.filter(
    c => c.status === 'yes' || c.status === 'not_applicable'
  ).length
  const partialCount = clauseStatuses.filter(c => c.status === 'partial').length
  const missingCount = clauseStatuses.filter(c => c.status === 'no').length

  const scorePct  = doraScore ? (doraScore.score / doraScore.max_score) * 100 : 0
  const barColor  = SCORE_COLORS[doraScore?.rating ?? 'GREY']

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-start gap-3 flex-wrap mb-1">
          <h1 className="text-2xl font-bold text-gray-900">{contract.contract_name}</h1>
          <code className="self-center text-sm bg-gray-100 text-gray-600 px-2 py-1 rounded font-mono">
            {contract.contract_ref}
          </code>
          <StatusBadge value={contract.contract_status} type="status" />
          {doraScore && <StatusBadge value={doraScore.rating} type="score" />}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-gray-200 mb-6">
        {TABS.map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              tab === t
                ? 'text-blue-600 border-b-2 border-blue-600 -mb-px bg-transparent'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* ── Overview ── */}
      {tab === 'Overview' && (
        <div className="grid grid-cols-2 gap-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-700 mb-4">Contract Details</h3>
            <InfoRow label="Owner"          value={contract.contract_owner} />
            <InfoRow label="Effective Date" value={contract.effective_date} />
            <InfoRow label="Expiry Date"    value={contract.expiry_date} />
            <InfoRow label="Renewal Type"   value={contract.renewal_type} />
            <InfoRow label="Notice Period"  value={contract.notice_period_days
              ? `${contract.notice_period_days} days` : null} />
            <InfoRow label="Last Reviewed"  value={contract.last_reviewed_date} />
            <InfoRow label="Version"        value={contract.version} />
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-700 mb-4">Provider</h3>
            <InfoRow label="Legal Name"     value={contract.provider?.legal_name} />
            <InfoRow label="LEI"            value={contract.provider?.lei} />
            <InfoRow label="Country"        value={contract.provider?.country_of_incorporation} />
            <InfoRow label="Provider Type"  value={contract.provider?.provider_type} />
            <InfoRow label="Parent Company" value={contract.provider?.parent_company} />
          </div>
        </div>
      )}

      {/* ── Services ── */}
      {tab === 'Services' && (
        <div className="space-y-4">
          {(contract.services ?? []).length === 0 && (
            <p className="text-gray-400 text-sm">No services linked to this contract.</p>
          )}
          {(contract.services ?? []).map(s => (
            <div key={s.id} className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="flex items-start justify-between gap-3 mb-2">
                <div>
                  <code className="text-xs text-gray-400 font-mono">{s.service_ref}</code>
                  <p className="text-sm font-medium text-gray-900 mt-0.5">{s.service_description}</p>
                </div>
                <div className="flex gap-2 flex-shrink-0 flex-wrap justify-end">
                  <span className="rounded-full px-2 py-0.5 text-xs font-semibold bg-blue-100 text-blue-700">
                    {s.ict_service_category}
                  </span>
                  {s.is_critical_or_important
                    ? <span className="rounded-full px-2 py-0.5 text-xs font-semibold bg-red-100 text-red-700">
                        CRITICAL / IMPORTANT
                      </span>
                    : <span className="rounded-full px-2 py-0.5 text-xs font-semibold bg-gray-100 text-gray-600">
                        Non-critical
                      </span>}
                  {s.personal_data_involved &&
                    <span className="rounded-full px-2 py-0.5 text-xs font-semibold bg-purple-100 text-purple-700">
                      Personal Data
                    </span>}
                </div>
              </div>
              {s.supported_application && (
                <p className="text-xs text-gray-500 mt-1">Application: {s.supported_application}</p>
              )}
              {s.supported_function && (
                <p className="text-xs text-gray-500">Function: {s.supported_function}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* ── DORA Clauses ── */}
      {tab === 'DORA Clauses' && (
        <div>
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden mb-6">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  {['Clause', 'Status', 'Reference', 'Notes', 'Reviewer', 'Date'].map(h => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {clauseStatuses.map(({ ct, status, clause }) => (
                  <tr key={ct} className={status === 'no' ? 'bg-red-50' : ''}>
                    <td className="px-4 py-2.5 font-medium text-gray-800 text-xs whitespace-nowrap">
                      {fmt(ct)}
                    </td>
                    <td className="px-4 py-2.5">
                      <StatusBadge value={status} type="clause" />
                    </td>
                    <td className="px-4 py-2.5 text-xs text-gray-500">{clause?.clause_reference ?? '—'}</td>
                    <td className="px-4 py-2.5 text-xs text-gray-500 max-w-xs">{clause?.notes ?? '—'}</td>
                    <td className="px-4 py-2.5 text-xs text-gray-500">{clause?.reviewer ?? '—'}</td>
                    <td className="px-4 py-2.5 text-xs text-gray-500">{clause?.review_date ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Score bar */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                {doraScore?.score ?? 0} / {doraScore?.max_score ?? 120}
                {doraScore && <StatusBadge value={doraScore.rating} type="score" />}
              </span>
              <span className="text-xs text-gray-500">
                {completedCount} complete · {partialCount} partial · {missingCount} missing
              </span>
            </div>
            <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{ width: `${scorePct}%`, backgroundColor: barColor }}
              />
            </div>
          </div>
        </div>
      )}

      {/* ── Risk ── */}
      {tab === 'Risk' && (
        <div>
          {!contract.risk_assessment ? (
            <p className="text-gray-400 text-sm">No risk assessment recorded.</p>
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-4 gap-4">
                {[
                  { label: 'Risk Rating',        val: contract.risk_assessment.risk_rating,        type: 'risk' },
                  { label: 'Substitutability',   val: contract.risk_assessment.substitutability,   type: 'risk' },
                  { label: 'Concentration Risk', val: contract.risk_assessment.concentration_risk, type: 'risk' },
                  { label: 'Next Review',        val: contract.risk_assessment.next_review_date,   type: null },
                ].map(({ label, val, type }) => (
                  <div key={label} className="bg-white rounded-xl border border-gray-200 p-5 text-center">
                    <p className="text-xs text-gray-400 uppercase mb-2">{label}</p>
                    {type
                      ? <StatusBadge value={val} type={type} />
                      : <p className="text-sm font-semibold text-gray-800">{val ?? '—'}</p>}
                  </div>
                ))}
              </div>
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <InfoRow label="Last Due Diligence" value={contract.risk_assessment.last_due_diligence_date} />
                <InfoRow label="Assessed By"        value={contract.risk_assessment.assessed_by} />
                {contract.risk_assessment.notes && (
                  <div className="mt-2 p-3 bg-amber-50 rounded-lg border border-amber-200">
                    <p className="text-xs text-amber-700">{contract.risk_assessment.notes}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
