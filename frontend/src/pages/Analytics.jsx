import { useEffect, useState } from 'react'
import { Bar, Line, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  PointElement, LineElement, ArcElement, Title, Tooltip, Legend, Filler
} from 'chart.js'
import api from '../services/api'
import StatCard from '../components/StatCard'

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, ArcElement, Title, Tooltip, Legend, Filler)

export default function Analytics() {
  const [data, setData] = useState(null)

  useEffect(() => {
    api.get('/analytics/').then(r => setData(r.data)).catch(() => {})
  }, [])

  if (!data) return <div className="loading">Loading analytics…</div>

  const cycleChart = {
    labels: data.cycle_trend.map(c => c.date),
    datasets: [{
      label: 'Cycle Length',
      data: data.cycle_trend.map(c => c.cycle_length),
      borderColor: '#e91e8c', backgroundColor: 'rgba(233,30,140,0.1)',
      fill: true, tension: 0.4,
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

  const moodChart = {
    labels: data.mood_trend.map(m => m.date),
    datasets: [{
      label: 'Mood Score',
      data: data.mood_trend.map(m => m.mood_score),
      borderColor: '#9c27b0', backgroundColor: 'rgba(156,39,176,0.1)',
      fill: true, tension: 0.4,
    }],
  }

  const opts = { responsive: true, plugins: { legend: { display: false } } }

  return (
    <div>
      <div className="page-header">
        <h1>Analytics</h1>
        <p>Insights from your health data</p>
      </div>

      <div className="card-grid" style={{ marginBottom: '1.5rem' }}>
        <StatCard label="Total Cycles" value={data.summary.total_cycles} icon="🔄" />
        <StatCard label="Avg Cycle Length" value={data.summary.avg_cycle_length ? `${data.summary.avg_cycle_length}d` : null} icon="📅" />
        <StatCard label="Shortest Cycle" value={data.summary.min_cycle_length ? `${data.summary.min_cycle_length}d` : null} icon="⬇️" />
        <StatCard label="Longest Cycle" value={data.summary.max_cycle_length ? `${data.summary.max_cycle_length}d` : null} icon="⬆️" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
        <div className="card">
          <h3 style={{ marginBottom: '1rem', color: 'var(--pink-dark)' }}>Cycle Length Over Time</h3>
          {data.cycle_trend.length > 0 ? <Line data={cycleChart} options={opts} /> : <p style={{ color: 'var(--text-muted)' }}>No data yet</p>}
        </div>
        <div className="card">
          <h3 style={{ marginBottom: '1rem', color: 'var(--pink-dark)' }}>Mood Score Trend</h3>
          {data.mood_trend.length > 0 ? <Line data={moodChart} options={opts} /> : <p style={{ color: 'var(--text-muted)' }}>No data yet</p>}
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: '1rem', color: 'var(--pink-dark)' }}>Symptom Frequency</h3>
        {data.symptom_frequency.length > 0
          ? <div style={{ maxWidth: 500, margin: '0 auto' }}><Doughnut data={symptomChart} /></div>
          : <p style={{ color: 'var(--text-muted)' }}>No symptoms logged yet</p>}
      </div>
    </div>
  )
}
