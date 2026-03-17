import { useEffect, useState } from 'react'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function Settings() {
  const { user } = useAuth()
  const [form, setForm] = useState({
    full_name: '',
    date_of_birth: '',
    average_cycle_length: 28,
    average_period_length: 5,
    notify_email: '',
    notify_name: '',
    email_notifications: true,
  })
  const [loading, setLoading] = useState(false)
  const [testLoading, setTestLoading] = useState(false)

  useEffect(() => {
    api.get('/user/me').then(r => {
      const u = r.data
      setForm({
        full_name: u.full_name || '',
        date_of_birth: u.date_of_birth || '',
        average_cycle_length: u.average_cycle_length,
        average_period_length: u.average_period_length,
        notify_email: u.notify_email || '',
        notify_name: u.notify_name || '',
        email_notifications: u.email_notifications ?? true,
      })
    }).catch(() => {})
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await api.put('/user/me', {
        ...form,
        date_of_birth: form.date_of_birth || null,
        notify_email: form.notify_email || null,
        notify_name: form.notify_name || null,
      })
      toast.success('Settings saved!')
    } catch {
      toast.error('Failed to save settings')
    } finally {
      setLoading(false)
    }
  }

  const sendTestEmail = async () => {
    setTestLoading(true)
    try {
      const { data } = await api.post('/notifications/test-email')
      if (data.status === 'sent') {
        toast.success(`Test email sent to ${data.to}`)
      } else {
        toast.error('Email failed — check SMTP settings in .env')
      }
    } catch {
      toast.error('Failed to send test email')
    } finally {
      setTestLoading(false)
    }
  }

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  return (
    <div>
      <div className="page-header">
        <h1>Settings</h1>
        <p>Update your profile, cycle preferences, and email notifications</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>

        {/* Profile */}
        <div className="card">
          <h3 style={{ marginBottom: '1rem', color: 'var(--pink-dark)' }}>Profile</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Full Name</label>
              <input value={form.full_name} onChange={set('full_name')} />
            </div>
            <div className="form-group">
              <label>Date of Birth</label>
              <input type="date" value={form.date_of_birth} onChange={set('date_of_birth')} />
            </div>
            <div className="form-group">
              <label>Average Cycle Length (days)</label>
              <input type="number" min={21} max={45} value={form.average_cycle_length}
                onChange={e => setForm({ ...form, average_cycle_length: parseInt(e.target.value) })} />
            </div>
            <div className="form-group">
              <label>Average Period Length (days)</label>
              <input type="number" min={2} max={10} value={form.average_period_length}
                onChange={e => setForm({ ...form, average_period_length: parseInt(e.target.value) })} />
            </div>
            <button className="btn btn-primary" type="submit" disabled={loading}>
              {loading ? 'Saving...' : 'Save Profile'}
            </button>
          </form>

          <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--bg)', borderRadius: 8 }}>
            <strong style={{ fontSize: '0.85rem' }}>Account Info</strong>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.5rem', lineHeight: 1.8 }}>
              Email: {user?.email}<br />
              Username: {user?.username}
            </p>
          </div>
        </div>

        {/* Email Notifications */}
        <div className="card">
          <h3 style={{ marginBottom: '0.5rem', color: 'var(--pink-dark)' }}>Email Notifications</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
            Set a recipient email to receive automatic health updates. Leave blank to use your account email.
          </p>

          <div className="form-group">
            <label>Recipient Name</label>
            <input
              placeholder="e.g. Sarah or Mom"
              value={form.notify_name}
              onChange={set('notify_name')}
            />
          </div>
          <div className="form-group">
            <label>Recipient Email</label>
            <input
              type="email"
              placeholder="e.g. sarah@example.com"
              value={form.notify_email}
              onChange={set('notify_email')}
            />
            <small style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>
              Leave blank to send to your account email ({user?.email})
            </small>
          </div>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={form.email_notifications}
                onChange={e => setForm({ ...form, email_notifications: e.target.checked })}
                style={{ width: 18, height: 18, accentColor: 'var(--pink)', cursor: 'pointer' }}
              />
              Enable email notifications
            </label>
          </div>

          <button className="btn btn-primary" onClick={handleSubmit} disabled={loading} style={{ marginBottom: '0.75rem' }}>
            {loading ? 'Saving...' : 'Save Email Settings'}
          </button>

          <button className="btn btn-secondary" onClick={sendTestEmail} disabled={testLoading} style={{ marginLeft: '0.75rem' }}>
            {testLoading ? 'Sending...' : 'Send Test Email'}
          </button>

          <div style={{ marginTop: '1.5rem', padding: '1rem', background: '#fff5f8', borderRadius: 8, borderLeft: '3px solid var(--pink)' }}>
            <strong style={{ fontSize: '0.85rem', color: 'var(--pink-dark)' }}>Emails you will receive:</strong>
            <ul style={{ marginTop: '0.5rem', paddingLeft: '1.2rem', fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 2 }}>
              <li>Period alert — 3 days before predicted period</li>
              <li>PMS alert — 7 days before predicted period</li>
              <li>Low mood alert — when mood score drops below 4</li>
              <li>High severity symptom alert — when severity is 8+</li>
              <li>Weekly health summary — every Monday</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
