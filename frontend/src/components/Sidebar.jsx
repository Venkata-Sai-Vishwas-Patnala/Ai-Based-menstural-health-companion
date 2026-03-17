import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  IconDashboard, IconCalendar, IconActivity, IconJournal, IconChat,
  IconChart, IconDiet, IconBell, IconDownload, IconSettings, IconLogout, AppLogo
} from './Icons'

const NAV = [
  { to: '/',             icon: IconDashboard, label: 'Dashboard' },
  { to: '/cycle',        icon: IconCalendar,  label: 'Cycle Tracker' },
  { to: '/symptoms',     icon: IconActivity,  label: 'Symptoms' },
  { to: '/journal',      icon: IconJournal,   label: 'Mood Journal' },
  { to: '/chatbot',      icon: IconChat,      label: 'AI Chatbot' },
  { to: '/analytics',    icon: IconChart,     label: 'Analytics' },
  { to: '/diet',         icon: IconDiet,      label: 'Diet Guide' },
  { to: '/notifications',icon: IconBell,      label: 'Notifications' },
  { to: '/export',       icon: IconDownload,  label: 'Export Report' },
  { to: '/settings',     icon: IconSettings,  label: 'Settings' },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <AppLogo size={34} />
        <div style={{ marginLeft: 10, lineHeight: 1.2 }}>
          <div style={{ fontWeight: 700, fontSize: '0.95rem', letterSpacing: '0.01em' }}>MenstrualAI</div>
          <div style={{ fontSize: '0.65rem', opacity: 0.65, fontWeight: 400 }}>Health Companion</div>
        </div>
      </div>
      <nav>
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => isActive ? 'active' : ''}>
            <Icon size={18} /> {label}
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div style={{ fontSize: '0.8rem', marginBottom: '0.5rem', opacity: 0.8 }}>
          {user?.full_name || user?.username}
        </div>
        <button onClick={handleLogout}>
          <IconLogout size={14} style={{ marginRight: 6 }} /> Logout
        </button>
      </div>
    </aside>
  )
}
