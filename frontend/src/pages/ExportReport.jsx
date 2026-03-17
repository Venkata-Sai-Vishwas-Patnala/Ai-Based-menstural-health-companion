import { useState } from 'react'
import api from '../services/api'
import toast from 'react-hot-toast'
import { IconDownload, IconDoc } from '../components/Icons'

export default function ExportReport() {
  const [loading, setLoading] = useState(false)

  const downloadReport = async () => {
    setLoading(true)
    try {
      const response = await api.get('/export/report', { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'health_report.pdf')
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      toast.success('Report downloaded!')
    } catch {
      toast.error('Failed to generate report')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Export Health Report</h1>
        <p>Download a comprehensive PDF of your health data</p>
      </div>

      <div className="card" style={{ maxWidth: 600 }}>
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div style={{ color: 'var(--pink)', marginBottom: '1rem' }}>
            <IconDoc size={64} />
          </div>
          <h2 style={{ color: 'var(--pink-dark)', marginBottom: '0.75rem' }}>Your Health Report</h2>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>Your report includes:</p>
          <div style={{ textAlign: 'left', display: 'inline-block', marginBottom: '2rem' }}>
            {[
              'Next predicted period date',
              'Full cycle history (last 12 cycles)',
              'Symptom log (last 15 entries)',
              'Mood journal summary',
              'Health disclaimer',
            ].map((item, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.6rem' }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--pink)" strokeWidth="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                <span style={{ fontSize: '0.9rem' }}>{item}</span>
              </div>
            ))}
          </div>
          <br />
          <button className="btn btn-primary" onClick={downloadReport} disabled={loading}
            style={{ padding: '0.85rem 2rem', fontSize: '1rem', display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
            <IconDownload size={18} />
            {loading ? 'Generating PDF...' : 'Download PDF Report'}
          </button>
        </div>
      </div>
    </div>
  )
}
