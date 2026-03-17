import { useEffect, useState } from 'react'
import api from '../services/api'
import { IconBell, IconCheck } from '../components/Icons'

export default function Notifications() {
  const [notifications, setNotifications] = useState([])

  const load = () => api.get('/notifications/').then(r => setNotifications(r.data)).catch(() => {})

  useEffect(() => { load() }, [])

  const markRead = async (id) => {
    await api.put(`/notifications/${id}/read`)
    load()
  }

  const typeIcon = (t) => {
    if (t === 'period_alert') return (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" style={{ color: 'var(--pink)' }}><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
    )
    if (t === 'pms_alert') return (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#9c27b0" strokeWidth="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
    )
    return (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ff9800" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
    )
  }

  return (
    <div>
      <div className="page-header">
        <h1>Notifications</h1>
        <p>Period alerts, PMS reminders, and health tips</p>
      </div>

      <div className="card">
        {notifications.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
            <div style={{ color: 'var(--border)', marginBottom: '1rem' }}><IconBell size={48} /></div>
            <p>No notifications yet.</p>
            <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>They will appear here when your period is approaching.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {notifications.map(n => (
              <div key={n.id} style={{
                display: 'flex', alignItems: 'flex-start', gap: '1rem', padding: '1rem',
                borderRadius: 8, background: n.is_read ? 'white' : '#fff5f8',
                border: `1px solid ${n.is_read ? 'var(--border)' : 'var(--pink-light)'}`,
              }}>
                <div style={{ flexShrink: 0, marginTop: 2 }}>{typeIcon(n.notification_type)}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>{n.title}</div>
                  <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>{n.message}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                    {new Date(n.created_at).toLocaleDateString()}
                  </div>
                </div>
                {!n.is_read && (
                  <button className="btn btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: 4 }}
                    onClick={() => markRead(n.id)}>
                    <IconCheck size={14} /> Mark Read
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
