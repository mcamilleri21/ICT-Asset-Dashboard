import { NavLink } from 'react-router-dom'
import { Shield, LayoutDashboard, FileText, Building2, Server } from 'lucide-react'

const LINKS = [
  { to: '/',          end: true, icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/contracts',            icon: FileText,         label: 'Contracts' },
  { to: '/providers',            icon: Building2,        label: 'Providers' },
  { to: '/services',             icon: Server,           label: 'Services' },
]

export default function Sidebar() {
  return (
    <aside className="fixed top-0 left-0 h-screen w-64 bg-[#1e2a4a] text-white flex flex-col z-10">
      <div className="flex items-center gap-2.5 px-6 py-5 border-b border-white/10">
        <Shield size={20} className="text-blue-400 flex-shrink-0" />
        <span className="font-semibold text-sm tracking-wide">DORA Platform</span>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {LINKS.map(({ to, end, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-white/10 hover:text-white'
              }`
            }
          >
            <Icon size={16} className="flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="px-6 py-4 border-t border-white/10">
        <p className="text-gray-500 text-xs">DORA Art. 30 · RoI Ready</p>
      </div>
    </aside>
  )
}
