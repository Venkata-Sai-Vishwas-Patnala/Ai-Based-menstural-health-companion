import { useEffect, useState } from 'react'
import api from '../services/api'
import toast from 'react-hot-toast'
import { format } from 'date-fns'
import {
  IconTrash, IconActivity, IconCycle, IconDroplet,
  IconYoga, IconSleep, IconWalk, IconFlame, IconAlertCircle
} from '../components/Icons'

const today = () => new Date().toISOString().split('T')[0]

const getFormValidationError = (form, cycles = []) => {
  const start = form.start_date
  const end = form.end_date
  if (!start) return 'Please choose a period start date.'
  if (start > today()) return 'Period start date cannot be in the future.'
  if (end && end < start) return 'End date cannot be before the start date.'
  if (end && end > today()) return 'Period end date cannot be in the future.'

  for (const cycle of cycles) {
    if (!cycle.start_date) continue
    const existingStart = cycle.start_date
    const existingEnd = cycle.end_date || cycle.start_date
    const newStart = new Date(start)
    const newEnd = end ? new Date(end) : new Date(start)
    const existingStartDate = new Date(existingStart)
    const existingEndDate = new Date(existingEnd)

    if (start === existingStart) {
      return 'This period start date already exists.'
    }

    const overlap = Math.max(newStart.getTime(), existingStartDate.getTime()) <= Math.min(newEnd.getTime(), existingEndDate.getTime())
    if (overlap) {
      return 'This period overlaps an existing logged cycle.'
    }

    const daysSincePrevious = Math.floor((newStart.getTime() - existingStartDate.getTime()) / 86400000)
    if (daysSincePrevious > 0 && daysSincePrevious < 21) {
      return 'A new period entry is too close to a recent cycle.'
    }
  }

  return ''
}

const QUICK_SYMPTOMS = [
  { label: 'Cramps',            Icon: IconFlame },
  { label: 'Headache',          Icon: IconAlertCircle },
  { label: 'Bloating',          Icon: IconAlertCircle },
  { label: 'Fatigue',           Icon: IconSleep },
  { label: 'Back Pain',         Icon: IconActivity },
  { label: 'Nausea',            Icon: IconAlertCircle },
  { label: 'Mood Swings',       Icon: IconYoga },
  { label: 'Breast Tenderness', Icon: IconDroplet },
]

export default function CycleTracker() {
  const [cycles, setCycles] = useState([])
  const [prediction, setPrediction] = useState(null)
  const [status, setStatus] = useState(null)
  const [form, setForm] = useState({ start_date: today(), end_date: '', flow_intensity: 'medium', notes: '' })
  const [loading, setLoading] = useState(false)
  const [quickLogging, setQuickLogging] = useState(null)
  const validationError = getFormValidationError(form, cycles)

  const load = async () => {
    const [c, p, s] = await Promise.all([
      api.get('/cycle/').catch(() => ({ data: [] })),
      api.get('/prediction/latest').catch(() => ({ data: null })),
      api.get('/analytics/period-status').catch(() => ({ data: null })),
    ])
    setCycles(c.data)
    setPrediction(p.data)
    setStatus(s.data)
  }

  useEffect(() => { load() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    const error = getFormValidationError(form, cycles)
    if (error) {
      toast.error(error)
      return
    }

    setLoading(true)
    try {
      await api.post('/cycle/', { ...form, end_date: form.end_date || null })
      toast.success('Cycle logged!')
      setForm({ start_date: today(), end_date: '', flow_intensity: 'medium', notes: '' })
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to log cycle')
    } finally {
      setLoading(false)
    }
  }

  const deleteCycle = async (id) => {
    await api.delete(`/cycle/${id}`)
    toast.success('Deleted')
    load()
  }

  const quickLog = async (symptomLabel, severity) => {
    setQuickLogging(symptomLabel)
    try {
      await api.post('/symptoms/', { logged_date: today(), symptom_type: symptomLabel, severity })
      toast.success(`${symptomLabel} logged!`)
    } catch {
      toast.error('Failed to log symptom')
    } finally {
      setQuickLogging(null)
    }
  }

  const onPeriod = status?.on_period
  const hasPrediction = prediction && !prediction.insufficient_data

  return (
    <div>
      <div className="page-header">
        <h1>Cycle Tracker</h1>
        <p>Log and monitor your menstrual cycles</p>
      </div>

      {/* ── Active Period Quick Panel ── */}
      {onPeriod && (
        <div style={{
          background: 'linear-gradient(135deg,#fce4ec,#f8bbd0)',
          border: '1.5px solid #f48fb1', borderRadius: 14,
          padding: '1rem 1.25rem', marginBottom: '1.25rem',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, color: '#c2185b', marginBottom: '0.75rem', fontSize: '0.95rem' }}>
            <IconDroplet size={18} color="#c2185b" />
            Day {status.period_day} of your period — Quick Symptom Log
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {QUICK_SYMPTOMS.map(({ label, Icon }) => (
              <button
                key={label}
                disabled={quickLogging === label}
                onClick={() => quickLog(label, 6)}
                style={{
                  background: 'white', border: '1.5px solid #f48fb1',
                  borderRadius: 10, padding: '0.5rem 0.75rem',
                  cursor: 'pointer', fontSize: '0.82rem', color: '#c2185b',
                  display: 'flex', alignItems: 'center', gap: '0.3rem',
                  opacity: quickLogging === label ? 0.6 : 1,
                }}
              >
                <Icon size={14} color="#c2185b" /> {label}
              </button>
            ))}
          </div>
          <p style={{ fontSize: '0.73rem', color: '#880e4f', margin: '0.6rem 0 0' }}>
            Tap any symptom to log it instantly. Go to Symptoms page to set custom severity.
          </p>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: '1.5rem' }}>
        {/* ── Log Form ── */}
        <div className="card">
          <h3 style={{ marginBottom: '0.75rem', color: 'var(--pink-dark)' }}>Log New Cycle</h3>
          <div className="helper-text" style={{ marginBottom: '1rem' }}>
            Smart validation keeps entries realistic and prevents overlapping periods.
          </div>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Period Start Date</label>
              <input
                type="date"
                value={form.start_date}
                max={today()}
                onChange={e => setForm({ ...form, start_date: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Period End Date (optional)</label>
              <input
                type="date"
                value={form.end_date}
                max={today()}
                min={form.start_date || undefined}
                onChange={e => setForm({ ...form, end_date: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>Flow Intensity</label>
              <select value={form.flow_intensity} onChange={e => setForm({ ...form, flow_intensity: e.target.value })}>
                <option value="light">Light</option>
                <option value="medium">Medium</option>
                <option value="heavy">Heavy</option>
              </select>
            </div>
            <div className="form-group">
              <label>Notes</label>
              <textarea rows={3} value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} />
            </div>
            {validationError && (
              <div className="inline-alert error" role="alert">
                {validationError}
              </div>
            )}
            {!validationError && (
              <div className="inline-alert success">
                Entry looks consistent with a normal cycle pattern.
              </div>
            )}
            <button className="btn btn-primary" disabled={loading || !!validationError}>
              {loading ? 'Saving…' : 'Log Cycle'}
            </button>
          </form>
        </div>

        <div>
          {/* ── Prediction Card ── */}
          {hasPrediction ? (
            <div className="card" style={{ marginBottom: '1rem', borderLeft: '4px solid var(--pink)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.5rem' }}>
                <IconCycle size={18} color="var(--pink)" />
                <strong>Next Predicted Period:</strong>{' '}
                {format(new Date(prediction.predicted_start_date), 'MMMM d, yyyy')}
                {' '}
                <span className="badge badge-pink">{prediction.confidence_label}</span>
              </div>
              <div style={{ display: 'flex', gap: '1.25rem', fontSize: '0.8rem', color: '#666', flexWrap: 'wrap' }}>
                <span>Avg cycle: <strong>{prediction.avg_cycle_length} days</strong></span>
                {prediction.last_3_lengths?.length > 0 && (
                  <span>Last {prediction.last_3_lengths.length}: <strong>{prediction.last_3_lengths.join(', ')} days</strong></span>
                )}
              </div>
            </div>
          ) : (
            <div className="card" style={{ marginBottom: '1rem', borderLeft: '4px solid #bdbdbd', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <IconAlertCircle size={18} color="#9e9e9e" />
              <div>
                <div style={{ fontWeight: 600, color: '#555', fontSize: '0.88rem' }}>Not enough data to predict yet</div>
                <div style={{ fontSize: '0.76rem', color: '#888' }}>
                  {prediction?.complete_cycles === 0
                    ? 'Log your first complete cycle (with start and end date)'
                    : `${prediction?.complete_cycles ?? 0} complete cycle logged — need at least 2`}
                </div>
              </div>
            </div>
          )}

          {/* ── Cycle History ── */}
          <div className="card">
            <h3 style={{ marginBottom: '1rem', color: 'var(--pink-dark)' }}>Cycle History</h3>
            {cycles.length === 0
              ? <p style={{ color: 'var(--text-muted)' }}>No cycles logged yet.</p>
              : (
                <table className="data-table">
                  <thead>
                    <tr><th>Start</th><th>End</th><th>Cycle Length</th><th>Flow</th><th></th></tr>
                  </thead>
                  <tbody>
                    {cycles.map(c => (
                      <tr key={c.id}>
                        <td>{c.start_date}</td>
                        <td>{c.end_date || '—'}</td>
                        <td>{c.cycle_length ? `${c.cycle_length} days` : '—'}</td>
                        <td><span className="badge badge-pink">{c.flow_intensity || '—'}</span></td>
                        <td>
                          <button
                            className="btn btn-danger"
                            style={{ padding: '0.3rem 0.6rem', display: 'flex', alignItems: 'center' }}
                            onClick={() => deleteCycle(c.id)}
                          >
                            <IconTrash size={14} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
          </div>
        </div>
      </div>
    </div>
  )
}
