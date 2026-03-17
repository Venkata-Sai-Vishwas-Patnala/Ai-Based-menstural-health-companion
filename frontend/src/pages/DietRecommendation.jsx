import { useEffect, useState } from 'react'
import api from '../services/api'

const PHASE_COLORS = {
  menstrual:  'phase-menstrual',
  follicular: 'phase-follicular',
  ovulation:  'phase-ovulation',
  luteal:     'phase-luteal',
}

const PHASE_LABELS = {
  menstrual:  'Menstrual Phase',
  follicular: 'Follicular Phase',
  ovulation:  'Ovulation Phase',
  luteal:     'Luteal Phase',
}

const PHASE_SVG = {
  menstrual: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/></svg>
  ),
  follicular: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="M17 8C8 10 5.9 16.17 3.82 21.34L5.71 22l1-2.3A4.49 4.49 0 0 0 8 20C19 20 22 3 22 3c-1 2-8 2-8 2 4-4 8-2 8-2C18 2 17 8 17 8z"/></svg>
  ),
  ovulation: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a5 5 0 1 0 0 10A5 5 0 0 0 12 2zm0 12c-5.33 0-8 2.67-8 4v2h16v-2c0-1.33-2.67-4-8-4z"/></svg>
  ),
  luteal: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.389 5.389 0 0 1-4.4 2.26 5.403 5.403 0 0 1-3.14-9.8c-.44-.06-.9-.1-1.36-.1z"/></svg>
  ),
}

export default function DietRecommendation() {
  const [diet, setDiet] = useState(null)

  useEffect(() => {
    api.get('/diet/').then(r => setDiet(r.data)).catch(() => {})
  }, [])

  if (!diet) return <div className="loading">Loading recommendations...</div>

  const { phase, cycle_day, recommendations } = diet

  return (
    <div>
      <div className="page-header">
        <h1>Diet Recommendations</h1>
        <p>Nutrition guidance tailored to your cycle phase</p>
      </div>

      {/* Current phase hero card */}
      <div className={`phase-card ${PHASE_COLORS[phase]}`} style={{ marginBottom: '1.5rem', display: 'flex', gap: '1.5rem', alignItems: 'flex-start' }}>
        <div style={{ opacity: 0.9, flexShrink: 0 }}>{PHASE_SVG[phase]}</div>
        <div style={{ flex: 1 }}>
          <h2 style={{ marginBottom: '0.25rem' }}>{PHASE_LABELS[phase]}</h2>
          <p style={{ opacity: 0.85, fontSize: '0.9rem', marginBottom: '0.5rem' }}>Day {cycle_day} of your cycle</p>
          <p style={{ opacity: 0.95, fontSize: '0.95rem' }}>{recommendations.description}</p>
          <p style={{ marginTop: '0.75rem', opacity: 0.9, fontStyle: 'italic', fontSize: '0.9rem' }}>{recommendations.tips}</p>
        </div>
        <div style={{ textAlign: 'right', flexShrink: 0 }}>
          <div style={{ fontSize: '0.75rem', opacity: 0.8, marginBottom: '0.25rem' }}>Energy Level</div>
          <div style={{ fontWeight: 700, textTransform: 'capitalize' }}>{recommendations.energy_level}</div>
          <div style={{ fontSize: '0.75rem', opacity: 0.8, marginTop: '0.5rem', marginBottom: '0.25rem' }}>Exercise</div>
          <div style={{ fontSize: '0.8rem' }}>{recommendations.exercise}</div>
        </div>
      </div>

      {/* Foods + Avoid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
        <div className="card">
          <h3 style={{ marginBottom: '1rem', color: 'var(--pink-dark)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>
            Recommended Foods
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {recommendations.foods.map((f, i) => (
              <div key={i} style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--pink)', marginTop: 6, flexShrink: 0 }} />
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{f.name}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{f.reason}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1rem', color: '#c62828', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            Foods to Avoid
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {recommendations.avoid.map((f, i) => (
              <div key={i} style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#f44336', marginTop: 6, flexShrink: 0 }} />
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{f.name}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{f.reason}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Supplements + Hydration */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
        <div className="card">
          <h3 style={{ marginBottom: '0.75rem', color: 'var(--pink-dark)' }}>Recommended Supplements</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {recommendations.supplements.map((s, i) => (
              <span key={i} className="badge badge-purple">{s}</span>
            ))}
          </div>
        </div>
        <div className="card">
          <h3 style={{ marginBottom: '0.75rem', color: 'var(--pink-dark)' }}>Hydration Guide</h3>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>{recommendations.hydration}</p>
        </div>
      </div>

      {/* All phases overview */}
      <div className="card">
        <h3 style={{ marginBottom: '1rem', color: 'var(--pink-dark)' }}>All Phases Overview</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem' }}>
          {Object.entries(PHASE_LABELS).map(([key, label]) => (
            <div key={key} className={`phase-card ${PHASE_COLORS[key]}`}
              style={{ opacity: key === phase ? 1 : 0.55, fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              {PHASE_SVG[key]}
              <strong style={{ marginTop: '0.25rem' }}>{label}</strong>
              {key === phase && <div style={{ fontSize: '0.75rem', background: 'rgba(255,255,255,0.2)', borderRadius: 4, padding: '0.1rem 0.4rem', display: 'inline-block' }}>Current</div>}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
