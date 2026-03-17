import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { AppLogo } from '../components/Icons'
import toast from 'react-hot-toast'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', username: '', password: '', full_name: '' })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await register(form)
      toast.success('Account created! Please sign in.')
      navigate('/login')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div style={{ display: 'flex', justifyContent: 'center', color: 'var(--pink)', marginBottom: '0.75rem' }}>
          <AppLogo size={52} />
        </div>
        <h1>Create Account</h1>
        <p>Start tracking your menstrual health</p>
        <form onSubmit={handleSubmit}>
          {[
            { key: 'full_name', label: 'Full Name', type: 'text', required: false },
            { key: 'username',  label: 'Username',  type: 'text', required: true },
            { key: 'email',     label: 'Email',     type: 'email', required: true },
            { key: 'password',  label: 'Password',  type: 'password', required: true },
          ].map(({ key, label, type, required }) => (
            <div className="form-group" key={key}>
              <label>{label}</label>
              <input type={type} value={form[key]} onChange={set(key)} required={required} />
            </div>
          ))}
          <button className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? 'Creating...' : 'Create Account'}
          </button>
        </form>
        <p style={{ textAlign: 'center', marginTop: '1rem', fontSize: '0.9rem' }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--pink)' }}>Sign In</Link>
        </p>
      </div>
    </div>
  )
}
