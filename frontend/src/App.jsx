import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Sidebar from './components/Sidebar'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import CycleTracker from './pages/CycleTracker'
import SymptomsTracker from './pages/SymptomsTracker'
import MoodJournal from './pages/MoodJournal'
import Chatbot from './pages/Chatbot'
import Analytics from './pages/Analytics'
import DietRecommendation from './pages/DietRecommendation'
import Notifications from './pages/Notifications'
import ExportReport from './pages/ExportReport'
import Settings from './pages/Settings'

function ProtectedLayout({ children }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">{children}</main>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/" element={<ProtectedLayout><Dashboard /></ProtectedLayout>} />
      <Route path="/cycle" element={<ProtectedLayout><CycleTracker /></ProtectedLayout>} />
      <Route path="/symptoms" element={<ProtectedLayout><SymptomsTracker /></ProtectedLayout>} />
      <Route path="/journal" element={<ProtectedLayout><MoodJournal /></ProtectedLayout>} />
      <Route path="/chatbot" element={<ProtectedLayout><Chatbot /></ProtectedLayout>} />
      <Route path="/analytics" element={<ProtectedLayout><Analytics /></ProtectedLayout>} />
      <Route path="/diet" element={<ProtectedLayout><DietRecommendation /></ProtectedLayout>} />
      <Route path="/notifications" element={<ProtectedLayout><Notifications /></ProtectedLayout>} />
      <Route path="/export" element={<ProtectedLayout><ExportReport /></ProtectedLayout>} />
      <Route path="/settings" element={<ProtectedLayout><Settings /></ProtectedLayout>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
