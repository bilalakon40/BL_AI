import React, { useState } from 'react'

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000'

interface Props { onKill: () => void }

const KillSwitch: React.FC<Props> = ({ onKill }) => {
  const [confirming, setConfirming] = useState(false)
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleKill = async () => {
    if (!password) { setError('Password required'); return }
    setLoading(true)
    try {
      const res = await fetch(`${API}/api/orchestrator/stop`, { method: 'POST' })
      if (res.ok) {
        setConfirming(false); setPassword(''); setError(''); onKill()
      } else {
        setError('Failed to stop')
      }
    } catch { setError('Connection error') }
    finally { setLoading(false) }
  }

  if (!confirming) {
    return (
      <button
        onClick={() => setConfirming(true)}
        className="flex items-center gap-2 px-4 py-2.5 bg-red-600/10 hover:bg-red-600/20 border border-red-500/20 rounded-xl text-red-400 text-xs font-bold tracking-wider transition-all active:scale-95"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" /><path d="M12 8v4M12 16h.01" />
        </svg>
        KILL
      </button>
    )
  }

  return (
    <div className="modal-overlay" onClick={(e) => { if (e.target === e.currentTarget) { setConfirming(false); setPassword(''); setError('') } }}>
      <div className="bg-[#12121a] p-6 rounded-2xl border border-red-500/30 max-w-sm w-full mx-4 shadow-2xl shadow-red-900/20" style={{ animation: 'fadeIn 0.2s ease' }}>
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-red-500/10 flex items-center justify-center">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" /><path d="M12 8v4M12 16h.01" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-bold text-red-400">Emergency Stop</h3>
            <p className="text-gray-500 text-xs">This will cancel ALL orders and lock the system</p>
          </div>
        </div>
        <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Admin password" autoFocus disabled={loading} />
        {error && <p className="text-red-400 text-xs mt-2 flex items-center gap-1"><span className="w-1 h-1 rounded-full bg-red-400" />{error}</p>}
        <div className="flex gap-3 mt-4">
          <button onClick={handleKill} disabled={loading} className="flex-1 py-2.5 bg-gradient-to-r from-red-600 to-red-500 hover:from-red-500 hover:to-red-400 rounded-xl text-white text-sm font-bold transition-all active:scale-95 disabled:opacity-50 flex items-center justify-center gap-2">
            {loading ? <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : null}
            {loading ? 'Stopping...' : 'STOP ALL'}
          </button>
          <button onClick={() => { setConfirming(false); setPassword(''); setError('') }} disabled={loading} className="flex-1 py-2.5 bg-[#1e1e30] hover:bg-[#2a2a40] rounded-xl text-gray-300 text-sm font-semibold transition-all active:scale-95 disabled:opacity-50 border border-[#2a2a40]">
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}

export default KillSwitch
