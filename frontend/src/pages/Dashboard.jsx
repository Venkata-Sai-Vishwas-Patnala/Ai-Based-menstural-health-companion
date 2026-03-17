import { useEffect, useState } from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, Title, Tooltip, Legend, Filler
} from 'chart.js'
import api from '../services/api'
import StatCard from '../components/StatCard'
import { IconDate, IconCycle, IconChart, IconPill,
  IconDroplet, IconLeaf, IconZap, IconShoppingBag,
  IconAlertTriangle, IconAlertCircle, IconMoon, IconSun,
  IconCoffee, IconWalk, IconWater, IconApple, IconRun,
  IconBath, IconBox, IconMeat, IconNoAlcohol, IconYoga,
  IconThermometer, IconPillBottle, IconTea, IconShirt,
  IconBackpack, IconChocolate, IconSleep, IconFlame, IconNoLift
} from '../components/Icons'
import { format, differenceInDays } from 'date-fns'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const PhaseIcon = ({ phase, size = 22 }) => {
  const props = { size, color: 'currentColor' }
  if (phase === 'Menstrual') return <IconDroplet {...props} />
  if (phase === 'Follicular') return <IconLeaf {...props} />
  if (phase === 'Ovulation') return <IconSun {...props} />
  return <IconMoon {...props} />
}

const IconSalt = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2v20M2 12h20"/>
  </svg>
)

const ADVICE_ICONS = {
  magnesium:    <IconApple size={16} />,
  caffeine:     <IconCoffee size={16} />,
  yoga:         <IconYoga size={16} />,
  journal:      <IconDate size={16} />,
  sleep:        <IconSleep size={16} />,
  walk:         <IconWalk size={16} />,
  salt:         <IconSalt size={16} />,
  water:        <IconWater size={16} />,
  potassium:    <IconApple size={16} />,
  run:          <IconRun size={16} />,
  bath:         <IconBath size={16} />,
  supplies:     <IconBox size={16} />,
  stock:        <IconDroplet size={16} />,
  heat:         <IconThermometer size={16} />,
  pain:         <IconPillBottle size={16} />,
  tea:          <IconTea size={16} />,
  iron:         <IconMeat size={16} />,
  alcohol:      <IconNoAlcohol size={16} />,
  stretch:      <IconYoga size={16} />,
  heating:      <IconThermometer size={16} />,
  clothes:      <IconShirt size={16} />,
  bag:          <IconBackpack size={16} />,
  chocolate:    <IconChocolate size={16} />,
  rest:         <IconSleep size={16} />,
  period:       <IconDroplet size={16} />,
  cramps:       <IconFlame size={16} />,
  nolift:       <IconNoLift size={16} />,
}

const PRE_PERIOD_PLAN = {
  7: {
    HeaderIcon: IconMoon, color: '#9c27b0', bg: '#f3e5f5', border: '#ce93d8',
    title: '7 Days to Go — PMS Window Starts',
    advice: [
      { iconKey: 'magnesium', text: 'Increase magnesium: dark chocolate, almonds, leafy greens' },
      { iconKey: 'caffeine',  text: 'Start reducing caffeine gradually to avoid withdrawal headaches' },
      { iconKey: 'yoga',      text: 'Add light yoga or stretching to your daily routine' },
      { iconKey: 'journal',   text: 'Start journaling mood and energy levels daily' },
    ]
  },
  6: {
    HeaderIcon: IconMoon, color: '#7b1fa2', bg: '#ede7f6', border: '#b39ddb',
    title: '6 Days to Go — Watch Your Mood',
    advice: [
      { iconKey: 'sleep',  text: 'Prioritise 8 hours of sleep — poor sleep worsens PMS' },
      { iconKey: 'walk',   text: '20-minute walk daily boosts serotonin naturally' },
      { iconKey: 'salt',   text: 'Reduce salty foods to prevent bloating later' },
      { iconKey: 'water',  text: 'Drink at least 2L of water today' },
    ]
  },
  5: {
    HeaderIcon: IconZap, color: '#e65100', bg: '#fff3e0', border: '#ffcc80',
    title: '5 Days to Go — Energy May Dip',
    advice: [
      { iconKey: 'potassium', text: 'Eat potassium-rich foods: bananas, sweet potatoes' },
      { iconKey: 'run',       text: 'Do your last high-intensity workout before your period' },
      { iconKey: 'bath',      text: 'Warm baths now can relax muscles before cramps begin' },
      { iconKey: 'supplies',  text: 'Check your period supplies — restock if needed' },
    ]
  },
  4: {
    HeaderIcon: IconShoppingBag, color: '#d84315', bg: '#fbe9e7', border: '#ffab91',
    title: '4 Days to Go — Prepare Your Kit',
    advice: [
      { iconKey: 'stock',   text: 'Stock up on pads, tampons, or menstrual cup' },
      { iconKey: 'heating', text: 'Get your heating pad ready for cramp relief' },
      { iconKey: 'pain',    text: 'Buy ibuprofen or your preferred pain relief' },
      { iconKey: 'tea',     text: 'Prepare ginger and chamomile tea bags' },
    ]
  },
  3: {
    HeaderIcon: IconAlertTriangle, color: '#c62828', bg: '#ffebee', border: '#ef9a9a',
    title: '3 Days to Go — Prepare Now',
    advice: [
      { iconKey: 'iron',    text: 'Eat iron-rich foods: spinach, lentils, red meat' },
      { iconKey: 'alcohol', text: 'Avoid alcohol — it worsens cramps and bloating' },
      { iconKey: 'stretch', text: "Child's pose and cat-cow stretches ease lower back pain" },
      { iconKey: 'heat',    text: 'Place heating pad near your bed for easy access' },
    ]
  },
  2: {
    HeaderIcon: IconAlertCircle, color: '#b71c1c', bg: '#fce4ec', border: '#f48fb1',
    title: '2 Days to Go — Almost Time',
    advice: [
      { iconKey: 'clothes',   text: 'Wear comfortable, dark clothing tomorrow just in case' },
      { iconKey: 'bag',       text: 'Pack period supplies in your bag today' },
      { iconKey: 'chocolate', text: 'Dark chocolate helps with mood and magnesium' },
      { iconKey: 'rest',      text: 'Sleep early — rest reduces cramp severity' },
    ]
  },
  1: {
    HeaderIcon: IconAlertCircle, color: '#e91e8c', bg: '#fce4ec', border: '#e91e8c',
    title: 'Period Tomorrow — Get Ready!',
    advice: [
      { iconKey: 'period',  text: 'Keep period supplies in your bag and at home' },
      { iconKey: 'pain',    text: 'Take pain relief at the very first sign of cramps' },
      { iconKey: 'cramps',  text: 'Apply heat to lower abdomen as soon as cramps start' },
      { iconKey: 'nolift',  text: 'Avoid heavy lifting or intense exercise today' },
    ]
  },
}

export default function Dashboard() {
  const [analytics, setAnalytics] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/analytics/').catch(() => ({ data: null })),
      api.get('/prediction/latest').catch(() => ({ data: null })),
      api.get('/analytics/period-status').catch(() => ({ data: null })),
    ]).then(([a, p, s]) => {
      setAnalytics(a.data)
      setPrediction(p.data)
      setStatus(s.data)
    }).finally(() => setLoading(false))
  }, [])

  const hasPrediction = prediction && !prediction.insufficient_data
  // Use days_until_next from period-status as source of truth for countdown
  const daysUntil = status?.days_until_next ?? (
    hasPrediction
      ? differenceInDays(new Date(prediction.predicted_start_date), new Date())
      : null
  )

  const cycleChartData = {
    labels: analytics?.cycle_trend?.map(c => c.date) || [],
    datasets: [{
      label: 'Cycle Length (days)',
      data: analytics?.cycle_trend?.map(c => c.cycle_length) || [],
      borderColor: '#e91e8c',
      backgroundColor: 'rgba(233,30,140,0.08)',
      fill: true, tension: 0.4,
    }],
  }

  const moodChartData = {
    labels: analytics?.mood_trend?.map(m => m.date) || [],
    datasets: [{
      label: 'Mood Score',
      data: analytics?.mood_trend?.map(m => m.mood_score) || [],
      borderColor: '#9c27b0',
      backgroundColor: 'rgba(156,39,176,0.08)',
      fill: true, tension: 0.4,
    }],
  }

  const chartOptions = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: false } },
  }

  if (loading) return <div className="loading">Loading dashboard...</div>

  const phase = status?.phase
  const onPeriod = status?.on_period
  const countdown = (daysUntil !== null && daysUntil >= 1 && daysUntil <= 7)
    ? PRE_PERIOD_PLAN[daysUntil]
    : null

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Your menstrual health at a glance</p>
      </div>

      {/* ── Active Period Banner ── */}
      {onPeriod && (
        <div style={{
          background: 'linear-gradient(135deg,#fce4ec,#f8bbd0)',
          border: '1.5px solid #f48fb1',
          borderRadius: 14, padding: '1rem 1.25rem',
          marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '1rem',
          flexWrap: 'wrap',
        }}>
          <div style={{ color: '#c2185b' }}><IconDroplet size={28} color="#c2185b" /></div>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, color: '#c2185b', fontSize: '1rem' }}>
              You are on Day {status.period_day} of your period
            </div>
            <div style={{ fontSize: '0.83rem', color: '#880e4f', marginTop: 2 }}>
              {phase?.description}
            </div>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {phase?.tips?.map(tip => (
              <span key={tip} style={{
                background: 'white', color: '#c2185b', fontSize: '0.75rem',
                padding: '0.3rem 0.7rem', borderRadius: 20, border: '1px solid #f48fb1',
              }}>{tip}</span>
            ))}
          </div>
        </div>
      )}

      {/* ── Pre-Period Countdown Card ── */}
      {!onPeriod && countdown && (() => {
        const { HeaderIcon, color, bg, border, title, advice } = countdown
        return (
          <div style={{
            background: bg, border: `1.5px solid ${border}`,
            borderRadius: 14, padding: '1rem 1.25rem', marginBottom: '1.25rem',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.85rem' }}>
              <div style={{ color }}><HeaderIcon size={24} color={color} /></div>
              <div>
                <div style={{ fontWeight: 700, color, fontSize: '0.95rem' }}>{title}</div>
                <div style={{ fontSize: '0.78rem', color: '#666', marginTop: 1 }}>
                  Predicted: {hasPrediction && format(new Date(prediction.predicted_start_date), 'MMMM d, yyyy')}
                </div>
              </div>
              <div style={{
                marginLeft: 'auto', background: color, color: 'white',
                borderRadius: 20, padding: '0.3rem 0.9rem', fontSize: '0.8rem', fontWeight: 700,
              }}>
                {daysUntil} {daysUntil === 1 ? 'day' : 'days'} left
              </div>
            </div>

            {/* Progress bar — 7 days window */}
            <div style={{ background: 'rgba(0,0,0,0.08)', borderRadius: 8, height: 6, marginBottom: '0.85rem' }}>
              <div style={{
                background: color, borderRadius: 8, height: 6,
                width: `${((7 - daysUntil) / 7) * 100}%`,
                transition: 'width 0.5s ease',
              }} />
            </div>

            {/* Advice grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
              {advice.map((a, i) => (
                <div key={i} style={{
                  background: 'white', borderRadius: 10, padding: '0.6rem 0.85rem',
                  display: 'flex', alignItems: 'flex-start', gap: '0.5rem',
                  border: `1px solid ${border}`,
                }}>
                  <span style={{ color, flexShrink: 0, marginTop: 1 }}>{ADVICE_ICONS[a.iconKey]}</span>
                  <span style={{ fontSize: '0.78rem', color: '#444', lineHeight: 1.4 }}>{a.text}</span>
                </div>
              ))}
            </div>
          </div>
        )
      })()}

      {/* ── Phase Indicator (when not on period and not in countdown) ── */}
      {!onPeriod && !countdown && phase && status?.status !== 'no_data' && (
        <div style={{
          background: `${phase.color}12`,
          border: `1.5px solid ${phase.color}40`,
          borderRadius: 14, padding: '0.85rem 1.25rem',
          marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '1rem',
          flexWrap: 'wrap',
        }}>
          <div style={{ color: phase.color }}><PhaseIcon phase={phase.phase} size={22} /></div>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, color: phase.color, fontSize: '0.95rem' }}>
              {phase.phase} Phase — Day {status.cycle_day} of your cycle
            </div>
            <div style={{ fontSize: '0.82rem', color: '#555', marginTop: 2 }}>
              {phase.description}
            </div>
          </div>
          <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
            {phase.tips?.slice(0, 2).map(tip => (
              <span key={tip} style={{
                background: 'white', color: phase.color, fontSize: '0.73rem',
                padding: '0.25rem 0.6rem', borderRadius: 20,
                border: `1px solid ${phase.color}40`,
              }}>{tip}</span>
            ))}
          </div>
        </div>
      )}

      {/* ── Stat Cards ── */}
      <div className="card-grid" style={{ marginBottom: '1.5rem' }}>
        <StatCard
          label={onPeriod ? 'Period Day' : 'Days Until Next Period'}
          value={onPeriod
            ? `Day ${status.period_day}`
            : prediction?.insufficient_data
              ? '—'
              : daysUntil !== null ? (daysUntil >= 0 ? `${daysUntil} days` : 'Due now') : '—'}
          icon={IconDate}
        />
        <StatCard
          label="Avg Cycle Length"
          value={analytics?.summary?.avg_cycle_length ? `${analytics.summary.avg_cycle_length} days` : null}
          icon={IconCycle}
        />
        <StatCard
          label="Total Cycles Logged"
          value={analytics?.summary?.total_cycles}
          icon={IconChart}
        />
        <StatCard
          label="Symptoms Logged"
          value={analytics?.summary?.total_symptoms_logged}
          icon={IconPill}
          color="var(--purple)"
        />
      </div>

      {/* ── Next Period Prediction (outside countdown window) ── */}
      {!onPeriod && !countdown && (
        prediction?.insufficient_data
          ? (
            <div className="card" style={{ marginBottom: '1.5rem', borderLeft: '4px solid #bdbdbd', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{ color: '#9e9e9e' }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              </div>
              <div>
                <div style={{ fontWeight: 600, color: '#555', fontSize: '0.9rem' }}>Not enough data to predict your next cycle yet</div>
                <div style={{ fontSize: '0.78rem', color: '#888', marginTop: 2 }}>
                  {prediction.complete_cycles === 0
                    ? 'Log your first complete cycle (with start and end date) to get started'
                    : `You have ${prediction.complete_cycles} complete cycle — need at least 2`}
                </div>
              </div>
            </div>
          ) : hasPrediction && daysUntil !== null && daysUntil > 7 ? (
            <div className="card" style={{ marginBottom: '1.5rem', borderLeft: '4px solid var(--pink)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                <div style={{ color: 'var(--pink)' }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                </div>
                <div style={{ flex: 1 }}>
                  <strong>Next Predicted Period: </strong>
                  {format(new Date(prediction.predicted_start_date), 'MMMM d, yyyy')}
                  {' '}
                  <span className="badge badge-pink">{prediction.confidence_label} (based on cycle consistency)</span>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', fontSize: '0.82rem', color: '#555' }}>
                <span>Avg cycle: <strong>{prediction.avg_cycle_length} days</strong></span>
                {prediction.last_3_lengths?.length > 0 && (
                  <span>Last {prediction.last_3_lengths.length} cycles: <strong>{prediction.last_3_lengths.join(', ')} days</strong></span>
                )}
                <span style={{ color: prediction.std_dev <= 4 ? '#2e7d32' : '#e65100', fontStyle: 'italic' }}>
                  {prediction.regularity}
                </span>
              </div>
            </div>
          ) : null
      )}

      {/* ── Charts ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        <div className="card">
          <h3 style={{ marginBottom: '1rem', color: 'var(--pink-dark)' }}>Cycle Length Trend</h3>
          {analytics?.cycle_trend?.length > 0
            ? <Line data={cycleChartData} options={chartOptions} />
            : <p style={{ color: 'var(--text-muted)' }}>Log cycles to see trends</p>}
        </div>
        <div className="card">
          <h3 style={{ marginBottom: '1rem', color: 'var(--pink-dark)' }}>Mood Trend</h3>
          {analytics?.mood_trend?.length > 0
            ? <Line data={moodChartData} options={chartOptions} />
            : <p style={{ color: 'var(--text-muted)' }}>Log journal entries to see mood trends</p>}
        </div>
      </div>

      {analytics?.symptom_frequency?.length > 0 && (
        <div className="card" style={{ marginTop: '1rem' }}>
          <h3 style={{ marginBottom: '1rem', color: 'var(--pink-dark)' }}>Top Symptoms</h3>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {analytics.symptom_frequency.map(s => (
              <span key={s.symptom} className="badge badge-pink">{s.symptom} ({s.count})</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
