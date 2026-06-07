import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000'

interface Stat { date: string; ending_balance: string; total_trades: number; winning_trades: number }

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div className="bg-[#0f0f1a] border border-[#2a2a40] rounded-xl px-4 py-3 shadow-2xl shadow-black/50" style={{ backdropFilter: 'blur(12px)' }}>
      <p className="text-gray-400 text-xs mb-1">{label}</p>
      <p className="text-white font-mono text-sm font-semibold">${d.balance?.toFixed(2)}</p>
      <div className="flex gap-4 mt-1.5 text-[10px]">
        <span className="text-gray-500">Trades: {d.trades}</span>
        <span className="text-gray-500">Wins: {d.wins}</span>
      </div>
    </div>
  )
}

const PnLChart: React.FC = () => {
  const [stats, setStats] = useState<Stat[]>([])

  useEffect(() => {
    const fetchStats = async () => {
      try { const r = await fetch(`${API}/api/stats`); if (r.ok) setStats(await r.json()) } catch {}
    }
    fetchStats()
    const id = setInterval(fetchStats, 30000)
    return () => clearInterval(id)
  }, [])

  const data = stats.map(s => ({
    date: new Date(s.date).toLocaleDateString(),
    balance: parseFloat(s.ending_balance),
    trades: s.total_trades,
    wins: s.winning_trades,
  })).reverse()

  return (
    <div className="card">
      <h2 className="text-base font-semibold text-white mb-5">Performance (30 Days)</h2>
      {data.length === 0 ? (
        <div className="h-[220px] flex flex-col items-center justify-center text-gray-600 gap-2">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
          </svg>
          <span className="text-sm">No data yet</span>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={data} margin={{ top: 5, right: 5, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="balanceGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#22c55e" stopOpacity={0.2} />
                <stop offset="100%" stopColor="#22c55e" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1a1a2e" vertical={false} />
            <XAxis dataKey="date" stroke="#3a3a4e" tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false} />
            <YAxis stroke="#3a3a4e" tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false} domain={['auto', 'auto']} tickFormatter={(v: number) => `$${v.toFixed(0)}`} />
            <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#2a2a40', strokeWidth: 1 }} />
            <Area type="monotone" dataKey="balance" stroke="#22c55e" strokeWidth={2.5} fill="url(#balanceGrad)" dot={false} activeDot={{ r: 4, fill: '#22c55e', stroke: '#0a0a0f', strokeWidth: 2 }} />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}

export default PnLChart
