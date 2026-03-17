import { useEffect, useState } from 'react'
import api from '../services/api'
import toast from 'react-hot-toast'
import { Trash2 } from 'lucide-react'

const MOODS = ['Happy', 'Calm', 'Anxious', 'Sad', 'Irritable', 'Energetic', 'Tired', 'Hopeful']
const MOOD_EMOJI = { Happy: '😊', Calm: '😌', Anxious: '😰', Sad: '😢', Irritable: '😤', Energetic: '⚡', Tired: '😴', Hopeful: '🌟' }

const today = () => new Date().toISOString().split('T')[0]

export default function MoodJournal() {
  const [entries, setEntries] = useState([])
  const [form, setForm] = useState({ entry_date: today(), mood: 'Happy', mood_score: 7, energy_level: 7, content: '' })

  const load = () => api.get('/journal/').then(r => setEntries(r.data)).catch(() => {})

  useEffect(() => { load() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await api.post('/journal/', form)
      toast.success('Journal entry saved!')
      setForm({ entry_date: today(), mood: 'Happy', mood_score: 7, energy_level: 7, content: '' })
      load()
    } catch {
      toast.error('Failed to save entry')
    }
  }

  const deleteEntry = async (id) => {
    await api.delete(`/journal/${id}`)
    toast.success('Deleted')
    load()
  }

  return (
    <div>
      <div className="page-header">
        <h1>Mood Journal</h1>
        <p>Track your emotional wellbeing throughout your cycle</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', gap: '1.5rem' }}>
        <div className="card">
          <h3 style={{ marginBottom: '1rem', color: 'var(--pink-dark)' }}>New Entry</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Date</label>
              <input type="date" value={form.entry_date} onChange={e => setForm({ ...form, entry_date: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>Mood</label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {MOODS.map(m => (
                  <button key={m} type="button"
                    className={`btn ${form.mood === m ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
                    onClick={() => setForm({ ...form, mood: m })}>
                    {MOOD_EMOJI[m]} {m}
                  </button>
                ))}
              </div>
            </div>
            <div className="form-group">
              <label>Mood Score: <strong>{form.mood_score}/10</strong></label>
              <input type="range" min={1} max={10} value={form.mood_score}
                onChange={e => setForm({ ...form, mood_score: parseInt(e.target.value) })}
                style={{ width: '100%', accentColor: 'var(--pink)' }} />
            </div>
            <div className="form-group">
              <label>Energy Level: <strong>{form.energy_level}/10</strong></label>
              <input type="range" min={1} max={10} value={form.energy_level}
                onChange={e => setForm({ ...form, energy_level: parseInt(e.target.value) })}
                style={{ width: '100%', accentColor: 'var(--purple)' }} />
            </div>
            <div className="form-group">
              <label>Journal Entry</label>
              <textarea rows={4} placeholder="How are you feeling today?" value={form.content}
                onChange={e => setForm({ ...form, content: e.target.value })} />
            </div>
            <button className="btn btn-primary">Save Entry</button>
          </form>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1rem', color: 'var(--pink-dark)' }}>Journal Entries</h3>
          {entries.length === 0
            ? <p style={{ color: 'var(--text-muted)' }}>No entries yet. Start journaling!</p>
            : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {entries.map(e => (
                  <div key={e.id} style={{ border: '1px solid var(--border)', borderRadius: 8, padding: '1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <div>
                        <span style={{ fontWeight: 600 }}>{e.entry_date}</span>
                        {' '}
                        <span className="badge badge-pink">{MOOD_EMOJI[e.mood]} {e.mood}</span>
                        {' '}
                        <span className="badge badge-purple">Energy {e.energy_level}/10</span>
                      </div>
                      <button className="btn btn-danger" style={{ padding: '0.3rem 0.6rem' }} onClick={() => deleteEntry(e.id)}>
                        <Trash2 size={14} />
                      </button>
                    </div>
                    {e.content && <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>{e.content}</p>}
                  </div>
                ))}
              </div>
            )}
        </div>
      </div>
    </div>
  )
}
