import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import api from '../services/api'
import toast from 'react-hot-toast'
import { IconSend, IconHeart, IconTrash } from '../components/Icons'
import { format } from 'date-fns'

const QUICK_QUESTIONS = [
  'What foods help with cramps?',
  'Why am I tired before my period?',
  'What is the luteal phase?',
  'How to track my cycle?',
]

function TypingIndicator() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.25rem 0' }}>
      <div style={{
        width: 32, height: 32, borderRadius: '50%',
        background: 'linear-gradient(135deg,var(--pink),var(--purple))',
        display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
      }}>
        <IconHeart size={14} color="white" />
      </div>
      <div style={{
        background: '#f3f4f6', borderRadius: '0 12px 12px 12px',
        padding: '0.65rem 1rem', display: 'flex', gap: 4, alignItems: 'center',
      }}>
        {[0, 1, 2].map(i => (
          <span key={i} style={{
            width: 7, height: 7, borderRadius: '50%', background: 'var(--pink)',
            display: 'inline-block',
            animation: 'bounce 1.2s infinite',
            animationDelay: `${i * 0.2}s`,
          }} />
        ))}
      </div>
    </div>
  )
}

function Message({ msg }) {
  const isUser = msg.role === 'user'
  const time = msg.created_at ? format(new Date(msg.created_at), 'h:mm a') : ''

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: isUser ? 'flex-end' : 'flex-start',
      marginBottom: '0.75rem',
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: '0.5rem', flexDirection: isUser ? 'row-reverse' : 'row' }}>
        {!isUser && (
          <div style={{
            width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
            background: 'linear-gradient(135deg,var(--pink),var(--purple))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <IconHeart size={13} color="white" />
          </div>
        )}

        <div style={{
          maxWidth: '72%',
          padding: isUser ? '0.75rem 1rem' : '0.8rem 1rem',
          borderRadius: isUser ? '18px 18px 0 18px' : '0 18px 18px 18px',
          background: isUser ? 'linear-gradient(135deg,var(--pink),var(--purple))' : '#fff9fb',
          color: isUser ? 'white' : '#1a1a2e',
          fontSize: '0.88rem',
          lineHeight: 1.7,
          boxShadow: isUser ? '0 6px 18px rgba(233,30,140,0.16)' : '0 2px 10px rgba(0,0,0,0.05)',
          border: isUser ? 'none' : '1px solid rgba(233,30,140,0.12)',
        }}>
          {isUser ? (
            <span>{msg.content}</span>
          ) : (
            <div className="markdown-body">
              <ReactMarkdown
                components={{
                  p: ({ children }) => <p>{children}</p>,
                  ul: ({ children }) => <ul>{children}</ul>,
                  ol: ({ children }) => <ol>{children}</ol>,
                  li: ({ children }) => <li>{children}</li>,
                  strong: ({ children }) => <strong>{children}</strong>,
                  em: ({ children }) => <em>{children}</em>,
                  blockquote: ({ children }) => <blockquote>{children}</blockquote>,
                }}
              >
                {msg.content}
              </ReactMarkdown>
            </div>
          )}
        </div>
      </div>

      {time && (
        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.2rem', paddingLeft: isUser ? 0 : '2.5rem', paddingRight: isUser ? 0 : 0 }}>
          {time}
        </span>
      )}
    </div>
  )
}

export default function Chatbot() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const messagesContainerRef = useRef(null)

  useEffect(() => {
    api.get('/chatbot/history').then(r => setMessages(r.data)).catch(() => {})
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = async (text) => {
    const msg = text || input
    if (!msg.trim()) return
    const userMsg = { role: 'user', content: msg, id: Date.now(), created_at: new Date().toISOString() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)
    try {
      const { data } = await api.post('/chatbot/ask', { message: msg })
      setMessages(prev => [...prev, data])
    } catch (err) {
      toast.error(err.response?.data?.detail || 'AI service unavailable')
      setMessages(prev => prev.filter(m => m.id !== userMsg.id))
    } finally {
      setLoading(false)
    }
  }

  const clearChat = async () => {
    try {
      await api.delete('/chatbot/history')
      setMessages([])
      toast.success('Chat cleared')
    } catch {
      toast.error('Failed to clear chat')
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 80px)', maxHeight: '100%' }}>

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexShrink: 0 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '1.4rem', color: 'var(--pink-dark)' }}>AI Health Chatbot</h1>
          <p style={{ margin: 0, fontSize: '0.82rem', color: 'var(--text-muted)' }}>Powered by Gemini 3.6 Flash</p>
        </div>
        <button className="btn btn-secondary" onClick={clearChat} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem' }}>
          <IconTrash size={14} /> Clear
        </button>
      </div>

      {/* Chat card */}
      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', padding: 0 }}>

        {/* Messages area */}
        <div
          ref={messagesContainerRef}
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '1.25rem',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {messages.length === 0 && (
            <div style={{ margin: 'auto', textAlign: 'center', padding: '2rem 1rem' }}>
              <div style={{ color: 'var(--pink)', marginBottom: '0.75rem' }}>
                <IconHeart size={44} />
              </div>
              <p style={{ fontWeight: 600, color: 'var(--pink-dark)', marginBottom: '0.3rem' }}>Hi! I am your health assistant.</p>
              <p style={{ fontSize: '0.83rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
                Ask me about symptoms, cycle phases, diet, or general health tips.
              </p>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', justifyContent: 'center' }}>
                {QUICK_QUESTIONS.map(q => (
                  <button key={q} className="btn btn-secondary"
                    style={{ fontSize: '0.78rem', padding: '0.35rem 0.75rem' }}
                    onClick={() => sendMessage(q)}>
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => <Message key={msg.id || i} msg={msg} />)}
          {loading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        {/* Divider */}
        <div style={{ height: 1, background: '#f0d0dc', flexShrink: 0 }} />

        {/* Input area */}
        <div style={{ padding: '0.85rem 1.25rem', flexShrink: 0 }}>
          <form onSubmit={e => { e.preventDefault(); sendMessage() }}
            style={{ display: 'flex', gap: '0.6rem', alignItems: 'center' }}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Ask about your health..."
              disabled={loading}
              style={{
                flex: 1, border: '1.5px solid #f0d0dc', borderRadius: 24,
                padding: '0.6rem 1rem', fontSize: '0.88rem', outline: 'none',
                background: '#fff8fb',
              }}
            />
            <button
              className="btn btn-primary"
              type="submit"
              disabled={loading || !input.trim()}
              style={{ borderRadius: '50%', width: 40, height: 40, padding: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}
            >
              <IconSend size={16} />
            </button>
          </form>
          <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: '0.4rem 0 0', textAlign: 'center' }}>
            General information only — not medical advice.
          </p>
        </div>
      </div>

      <style>{`
        @keyframes bounce {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-6px); }
        }
        .markdown-body p { margin: 0 0 0.4rem; }
        .markdown-body p:last-child { margin-bottom: 0; }
        .markdown-body ul { margin: 0.3rem 0 0.3rem 1.1rem; padding: 0; }
        .markdown-body li { margin-bottom: 0.2rem; }
        .markdown-body strong { color: #c2185b; }
        .markdown-body em { color: var(--text-muted); font-size: 0.82rem; }
      `}</style>
    </div>
  )
}
