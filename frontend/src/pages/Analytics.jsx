import { useEffect, useState } from 'react'
import { Line, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS, CategoryScale, LinearScale,
  PointElement, LineElement, ArcElement, Title, Tooltip, Legend, Filler
} from 'chart.js'
import api from '../services/api'
import { IconCycle, IconCalendar, IconHeart, IconAlertTriangle, IconCheck, IconActivity } from '../components/Icons'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, ArcElement, Title, Tooltip, Legend, Filler)

export default function Analytics() {
  const [data, setData] = useState(null)

  useEffect(() => {
    api.get('/analytics/').then(r => setData(r.data)).catch(() => {})
  }, [])

  if (!data) return <div className="loading">Loading analytics…</div>

  const summary = data.summary || {}

  const cycleChart = {
    labels: data.cycle_trend.map(c => c.date),
    datasets: [{
      label: 'Cycle Length',
      data: data.cycle_trend.map(c => c.cycle_length),
      borderColor: '#e91e8c', backgroundColor: 'rgba(233,30,140,0.12)',
      fill: true, tension: 0.35,
    }],
  }

  const moodChart = {
    labels: data.mood_trend.map(m => m.date),
    datasets: [{
      label: 'Mood Score',
      data: data.mood_trend.map(m => m.mood_score),
      borderColor: '#9c27b0', backgroundColor: 'rgba(156,39,176,0.12)',
      fill: true, tension: 0.35,
    }],
  }

  const symptomChart = {
    labels: data.symptom_frequency.map(s => s.symptom),
    datasets: [{
      label: 'Frequency',
      data: data.symptom_frequency.map(s => s.count),
      backgroundColor: [
        '#e91e8c','#9c27b0','#f06292','#ce93d8','#f48fb1',
        '#ba68c8','#f8bbd0','#e1bee7','#fce4ec','#f3e5f5',
      ],
    }],
  }

  const opts = { responsive: true, plugins: { legend: { display: false } } }

  const statCards = [
    { label: 'Total Cycles', value: summary.total_cycles ?? '—', accent: '#e91e8c', icon: <IconCycle size={18} />, note: 'Tracked cycle records' },
    { label: 'Avg Cycle', value: summary.avg_cycle_length ? `${summary.avg_cycle_length}d` : '—', accent: '#9c27b0', icon: <IconCalendar size={18} />, note: 'Average length' },
    { label: 'Current Phase', value: summary.current_phase || '—', accent: '#f06292', icon: <IconActivity size={18} />, note: summary.cycle_day ? `Day ${summary.cycle_day}` : 'No cycle day' },
    { label: 'Mood', value: summary.avg_mood_score ? `${summary.avg_mood_score}/10` : '—', accent: '#7b1fa2', icon: <IconHeart size={18} />, note: 'Average journal rating' },
    { label: 'Symptom Load', value: summary.avg_symptom_severity ? `${summary.avg_symptom_severity}/10` : '—', accent: '#c2185b', icon: <IconAlertTriangle size={18} />, note: summary.top_symptom ? `Top: ${summary.top_symptom}` : 'No symptoms yet' },
    { label: 'Status', value: summary.status || '—', accent: '#4caf50', icon: <IconCheck size={18} />, note: summary.days_until_next !== null ? `${summary.days_until_next}d until next period` : 'Awaiting cycle data' },
  ]

  return (
    <div>
      <div className="page-header">
        <h1>Health Analytics</h1>
        <p>Always-visible insights from your cycle, symptoms, and mood</p>
      </div>

      <div className="card-grid" style={{ marginBottom: '1.5rem' }}>
        {statCards.map(card => (
          <div key={card.label} className="stat-card" style={{ borderTop: `4px solid ${card.accent}` }}>
            <div style={{ color: card.accent, fontSize: '1.5rem', marginBottom: '0.5rem' }}>{card.icon}</div>
            <div className="stat-value" style={{ color: card.accent, fontSize: '1.7rem' }}>{card.value}</div>
            <div className="stat-label" style={{ marginTop: '0.2rem', fontWeight: 600 }}>{card.label}</div>
            <div style={{ marginTop: '0.4rem', color: 'var(--text-muted)', fontSize: '0.75rem' }}>{card.note}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
        <div className="card">
          <h3 style={{ marginBottom: '1rem', color: 'var(--pink-dark)' }}>Cycle Length Trend</h3>
          {data.cycle_trend.length > 0 ? <Line data={cycleChart} options={opts} /> : <p style={{ color: 'var(--text-muted)' }}>No cycle data yet</p>}
        </div>
        <div className="card">
          <h3 style={{ marginBottom: '1rem', color: 'var(--pink-dark)' }}>Mood Trend</h3>
          {data.mood_trend.length > 0 ? <Line data={moodChart} options={opts} /> : <p style={{ color: 'var(--text-muted)' }}>No journal mood data yet</p>}
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: '1rem', color: 'var(--pink-dark)' }}>Symptom Frequency</h3>
        {data.symptom_frequency.length > 0 ? (
          <div style={{ maxWidth: 500, margin: '0 auto' }}><Doughnut data={symptomChart} /></div>
        ) : (
          <p style={{ color: 'var(--text-muted)' }}>No symptom logs yet</p>
        )}
      </div>
    </div>
  )
}
