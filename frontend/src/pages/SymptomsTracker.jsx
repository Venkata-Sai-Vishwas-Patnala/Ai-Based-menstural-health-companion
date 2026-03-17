import { useEffect, useState } from 'react'
import api from '../services/api'
import toast from 'react-hot-toast'
import { Trash2 } from 'lucide-react'

const SYMPTOM_TYPES = [
  'Cramps', 'Headache', 'Bloating', 'Fatigue', 'Mood swings',
  'Back pain', 'Breast tenderness', 'Nausea', 'Acne', 'Insomnia', 'Other'
]

const today = () => new Date().toISOString().split('T')[0]

export default function SymptomsTracker() {
  const [symptoms, setSymptoms] = useState([])
  const [form, setForm] = useState({ logged_date: today(), symptom_type: 'Cramps', severity: 5, notes: '' })

  const load = () => api.get('/symptoms/').then(r => setSymptoms(r.data)).catch(() => {})

  useEffect(() => { load() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await api.post('/symptoms/', form)
      toast.success('Symptom logged!')
      setForm({ logged_date: today(), symptom_type: 'Cramps', severity: 5, notes: '' })
      load()
    } catch {
      toast.error('Failed to log symptom')
    }
  }

  const deleteSymptom = async (id) => {
    await api.delete(`/symptoms/${id}`)
    toast.success('Deleted')
    load()
  }

  const severityColor = (s) => s <= 3 ? '#4caf50' : s <= 6 ? '#ff9800' : '#f44336'

  return (
    <div>
      <div className="page-header">
        <h1>Symptoms Tracker</h1>
        <p>Track pain levels and physical symptoms</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: '1.5rem' }}>
        <div className="card">
          <h3 style={{ marginBottom: '1rem', color: 'var(--pink-dark)' }}>Log Symptom</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Date</label>
              <input type="date" value={form.logged_date} onChange={e => setForm({ ...form, logged_date: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>Symptom Type</label>
              <select value={form.symptom_type} onChange={e => setForm({ ...form, symptom_type: e.target.value })}>
                {SYMPTOM_TYPES.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Severity: <strong style={{ color: severityColor(form.severity) }}>{form.severity}/10</strong></label>
              <input type="range" min={1} max={10} value={form.severity}
                onChange={e => setForm({ ...form, severity: parseInt(e.target.value) })}
                style={{ width: '100%', accentColor: 'var(--pink)' }} />
            </div>
            <div className="form-group">
              <label>Notes</label>
              <textarea rows={2} value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} />
            </div>
            <button className="btn btn-primary">Log Symptom</button>
          </form>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1rem', color: 'var(--pink-dark)' }}>Symptom Log</h3>
          {symptoms.length === 0
            ? <p style={{ color: 'var(--text-muted)' }}>No symptoms logged yet.</p>
            : (
              <table className="data-table">
                <thead>
                  <tr><th>Date</th><th>Symptom</th><th>Severity</th><th>Notes</th><th></th></tr>
                </thead>
                <tbody>
                  {symptoms.map(s => (
                    <tr key={s.id}>
                      <td>{s.logged_date}</td>
                      <td><span className="badge badge-pink">{s.symptom_type}</span></td>
                      <td>
                        <span style={{ color: severityColor(s.severity), fontWeight: 600 }}>
                          {s.severity}/10
                        </span>
                      </td>
                      <td style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{s.notes || '—'}</td>
                      <td>
                        <button className="btn btn-danger" style={{ padding: '0.3rem 0.6rem' }} onClick={() => deleteSymptom(s.id)}>
                          <Trash2 size={14} />
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
  )
}
