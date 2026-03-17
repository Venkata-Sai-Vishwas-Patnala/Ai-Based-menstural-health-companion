export default function StatCard({ label, value, icon: Icon, color = 'var(--pink)' }) {
  return (
    <div className="stat-card">
      <div style={{ color, marginBottom: '0.5rem' }}>
        {Icon ? <Icon size={28} /> : null}
      </div>
      <div className="stat-value" style={{ color }}>{value ?? '—'}</div>
      <div className="stat-label">{label}</div>
    </div>
  )
}
