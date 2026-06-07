const MAPS = {
  score: {
    GREEN: 'bg-green-100 text-green-800',
    AMBER: 'bg-amber-100 text-amber-800',
    RED:   'bg-red-100 text-red-800',
    GREY:  'bg-gray-100 text-gray-600',
  },
  status: {
    active:     'bg-green-100 text-green-800',
    expired:    'bg-red-100 text-red-800',
    draft:      'bg-yellow-100 text-yellow-800',
    terminated: 'bg-gray-100 text-gray-600',
  },
  clause: {
    yes:            'bg-green-100 text-green-800',
    no:             'bg-red-100 text-red-800',
    partial:        'bg-yellow-100 text-yellow-800',
    not_applicable: 'bg-gray-100 text-gray-600',
  },
  risk: {
    low:      'bg-green-100 text-green-800',
    medium:   'bg-yellow-100 text-yellow-800',
    high:     'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
  },
}

export default function StatusBadge({ value, type = 'status' }) {
  if (!value) return null
  const colorClass = MAPS[type]?.[value] ?? 'bg-gray-100 text-gray-600'
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-semibold uppercase ${colorClass}`}>
      {value.replace(/_/g, ' ')}
    </span>
  )
}
