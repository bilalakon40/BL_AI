import React, { useState, useEffect, useCallback } from 'react'
import AgentPanel from './AgentPanel'
import TradeHistory from './TradeHistory'
import PnLChart from './PnLChart'
import KillSwitch from './KillSwitch'
import { useWebSocket } from '../hooks/useWebSocket'

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000'

interface State {
  is_running: boolean; is_locked: boolean; lock_reason: string | null
  active_agents: number; total_agents: number; market_symbols: string[]
  daily_stats: Record<string, any>
}
interface Price { symbol: string; price: number; change: number }

const SvgIcon = ({ path, color = 'currentColor', size = 20 }: { path: string; color?: string; size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d={path} />
  </svg>
)

const icons = {
  trades: 'M3 3v18h18M7 16l4-4 4 4 5-5',
  losses: 'M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M12 6a6 6 0 000 12 6 6 0 000-12z',
  agents: 'M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 3a4 4 0 100 8 4 4 0 000-8zM23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75',
  markets: 'M22 12h-4l-3 9L9 3l-3 9H2',
  running: 'M8 5v14l11-7z',
  stopped: 'M6 6l12 12M18 6l-12 12',
  arrowUp: 'M12 19V5M5 12l7-7 7 7',
  arrowDown: 'M12 5v14M5 12l7 7 7-7',
}

const Dashboard: React.FC = () => {
  const [state, setState] = useState<State | null>(null)
  const [prices, setPrices] = useState<Price[]>([])
  const [balance, setBalance] = useState({ free: 0, total: 0, asset: 'USDT' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const fetchState = useCallback(async () => {
    try {
      const [stateRes, balanceRes] = await Promise.all([
        fetch(`${API}/api/orchestrator/state`),
        fetch(`${API}/api/balance`),
      ])
      if (stateRes.ok) setState(await stateRes.json())
      if (balanceRes.ok) setBalance(await balanceRes.json())
    } catch { setError('Cannot connect to API') }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { fetchState(); const id = setInterval(fetchState, 5000); return () => clearInterval(id) }, [fetchState])

  useWebSocket((data: any) => {
    if (data.type === 'price' && data.symbol) {
      setPrices(prev => {
        const i = prev.findIndex(p => p.symbol === data.symbol)
        if (i >= 0) { const n = [...prev]; n[i] = data; return n }
        return [...prev, data]
      })
    }
  })

  const startOrch = async () => {
    await fetch(`${API}/api/orchestrator/start`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbols: ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT'] }),
    })
    fetchState()
  }

  if (loading) return (
    <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="w-10 h-10 border-2 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin" />
        <p className="text-gray-500 text-sm">Connecting...</p>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white" style={{ animation: 'fadeIn 0.4s ease' }}>
      {/* Ticker */}
      {prices.length > 0 && (
        <div className="ticker-wrap h-9 bg-[#0d0d15] border-b border-[#1a1a2e]">
          <div className="flex items-center h-full gap-8" style={{ animation: 'ticker 25s linear infinite' }}>
            {[...prices, ...prices, ...prices].map((p, i) => (
              <span key={i} className="flex items-center gap-2 text-sm whitespace-nowrap">
                <span className="font-semibold text-gray-300">{p.symbol.replace('USDT', '')}</span>
                <span className="font-mono text-white">${p.price?.toFixed(2)}</span>
                <span className={p.change && p.change >= 0 ? 'text-emerald-400' : 'text-red-400'}>
                  {p.change != null ? `${p.change >= 0 ? '+' : ''}${p.change.toFixed(2)}%` : '-'}
                </span>
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="p-4 md:p-6 max-w-7xl mx-auto">
        {/* Header */}
        <header className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8 gap-4">
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">AI Trading Platform</h1>
            <p className="text-gray-500 text-sm mt-1">
              Balance: <span className="text-emerald-400 font-mono font-semibold">{balance.free.toFixed(2)}</span>
              <span className="text-gray-600"> {balance.asset}</span>
            </p>
          </div>
          <div className="flex items-center gap-3">
            {state && (
              <span className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold tracking-wide ${
                state.is_running ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-gray-500/10 text-gray-400 border border-gray-500/20'
              }`}>
                <span className={`w-1.5 h-1.5 rounded-full ${state.is_running ? 'bg-emerald-400 glow-green' : 'bg-gray-500'}`} />
                {state.is_running ? 'Running' : 'Stopped'}
              </span>
            )}
            {state?.is_locked && (
              <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-red-500/10 text-red-400 border border-red-500/20 text-xs font-semibold">
                <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse" /> LOCKED
              </span>
            )}
            <KillSwitch onKill={fetchState} />
            <button onClick={startOrch} disabled={state?.is_running} className="btn-primary flex items-center gap-2">
              <SvgIcon path={icons.running} size={14} />
              Start
            </button>
          </div>
        </header>

        {error && (
          <div className="mb-6 p-4 bg-red-500/5 border border-red-500/10 rounded-2xl">
            <p className="text-red-400 text-sm flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-red-400" />
              {error}
            </p>
          </div>
        )}

        {state?.lock_reason && (
          <div className="mb-6 p-4 bg-red-500/5 border border-red-500/10 rounded-2xl" style={{ animation: 'slideIn 0.3s ease' }}>
            <p className="text-red-400 font-semibold text-sm mb-1">System Locked</p>
            <p className="text-red-300 text-xs">{state.lock_reason}</p>
          </div>
        )}

        {/* Stats */}
        {state && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <StatCard icon={icons.trades} label="Daily Trades" value={state.daily_stats?.trades_count ?? 0} />
            <StatCard icon={icons.losses} label="Consecutive Losses" value={state.daily_stats?.consecutive_losses ?? 0} color={state.daily_stats?.consecutive_losses > 2 ? 'red' : 'gray'} />
            <StatCard icon={icons.agents} label="Active Agents" value={`${state.active_agents}/${state.total_agents}`} color={state.active_agents > 0 ? 'green' : 'gray'} />
            <StatCard icon={icons.markets} label="Markets" value={state.market_symbols?.length ?? 0} />
          </div>
        )}

        {/* Charts & Agents */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <AgentPanel onUpdate={fetchState} prices={prices} />
          <PnLChart />
        </div>

        {/* Trade History */}
        <TradeHistory />
      </div>
    </div>
  )
}

const StatCard: React.FC<{ icon: string; label: string; value: string | number; color?: string }> = ({ icon, label, value, color = 'gray' }) => {
  const valColor = color === 'green' ? 'text-emerald-400' : color === 'red' ? 'text-red-400' : 'text-white'
  return (
    <div className="card card-glow" style={{ animation: 'fadeIn 0.4s ease' }}>
      <div className="flex items-start justify-between mb-3">
        <p className="stat-label">{label}</p>
        <span className="text-gray-600"><SvgIcon path={icon} size={18} /></span>
      </div>
      <p className={`stat-value ${valColor}`}>{value}</p>
    </div>
  )
}

export default Dashboard
