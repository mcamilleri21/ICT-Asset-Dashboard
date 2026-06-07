const COLOR = {
  blue:  { wrap: 'bg-blue-50',   icon: 'text-blue-600' },
  amber: { wrap: 'bg-amber-50',  icon: 'text-amber-600' },
  red:   { wrap: 'bg-red-50',    icon: 'text-red-600' },
  green: { wrap: 'bg-green-50',  icon: 'text-green-600' },
  gray:  { wrap: 'bg-gray-50',   icon: 'text-gray-600' },
}

export default function KPICard({ title, value, subtitle, icon: Icon, color = 'blue' }) {
  const c = COLOR[color] ?? COLOR.blue
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 relative overflow-hidden">
      {Icon && (
        <div className={`absolute top-4 right-4 p-2 rounded-lg ${c.wrap}`}>
          <Icon size={18} className={c.icon} />
        </div>
      )}
      <p className="text-sm text-gray-500 font-medium mb-1 pr-10">{title}</p>
      <p className="text-3xl font-bold text-gray-900">{value ?? '—'}</p>
      {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
    </div>
  )
}
