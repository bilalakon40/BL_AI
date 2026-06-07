import React, { useState, useEffect } from 'react'

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000'

interface Agent {
  agent_id: string; strategy: string; is_active: boolean
  performance: { trades: number; wins: number; total_pnl: number; win_rate: number }
}
interface Price { symbol: string; price: number; change: number }
interface Props { onUpdate: () => void; prices: Price[] }

const strategyMeta: Record<string, { label: string; color: string }> = {
  grid: { label: 'Grid', color: '#8b5cf6' },
  ema_crossover: { label: 'Trend', color: '#06b6d4' },
  ollama_llm: { label: 'AI', color: '#f59e0b' },
}

const AgentPanel: React.FC<Props> = ({ onUpdate, prices }) => {
  const [agents, setAgents] = useState<Agent[]>([])

  const fetchAgents = async () => {
    try { const r = await fetch(`${API}/api/agents`); if (r.ok) setAgents(await r.json()) } catch {}
  }

  useEffect(() => { fetchAgents(); const id = setInterval(fetchAgents, 5000); return () => clearInterval(id) }, [])

  const toggleAgent = async (id: string, active: boolean) => {
    await fetch(`${API}/api/agents/${id}/${active ? 'stop' : 'start'}`, { method: 'POST' })
    fetchAgents(); onUpdate()
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-base font-semibold text-white">Trading Agents</h2>
        <span className="text-xs text-gray-600">{agents.filter(a => a.is_active).length}/{agents.length} active</span>
      </div>
      <div className="space-y-3">
        {agents.length === 0 && <p className="text-gray-600 text-sm text-center py-6">No agents configured</p>}
        {agents.map((agent, idx) => {
          const meta = strategyMeta[agent.strategy] || { label: agent.strategy, color: '#6b7280' }
          const wr = agent.performance.win_rate || 0
          const pnl = agent.performance.total_pnl || 0
          return (
            <div key={agent.agent_id} className="group bg-[#0f0f1a] rounded-2xl p-4 border border-[#1a1a2e] hover:border-[#2a2a40] transition-all" style={{ animation: `fadeIn 0.3s ease ${idx * 0.05}s both` }}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className={`w-2.5 h-2.5 rounded-full ${agent.is_active ? 'bg-emerald-400 shadow-lg shadow-emerald-500/20' : 'bg-gray-600'}`} />
                  <div>
                    <span className="font-medium text-white text-sm">{agent.agent_id}</span>
                    <span className="ml-2 px-2 py-0.5 rounded-md text-[10px] font-semibold tracking-wide"
                      style={{ backgroundColor: `${meta.color}15`, color: meta.color, border: `1px solid ${meta.color}20` }}>
                      {meta.label}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => toggleAgent(agent.agent_id, agent.is_active)}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 active:scale-90 ${
                    agent.is_active
                      ? 'bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20'
                      : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20'
                  }`}
                >
                  {agent.is_active ? 'Stop' : 'Start'}
                </button>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <p className="text-gray-600 text-[10px] uppercase tracking-wider mb-1">Trades</p>
                  <p className="text-white text-sm font-mono font-semibold">{agent.performance.trades}</p>
                </div>
                <div>
                  <p className="text-gray-600 text-[10px] uppercase tracking-wider mb-1">Win Rate</p>
                  <p className="text-white text-sm font-mono font-semibold">{(wr * 100).toFixed(0)}%</p>
                  <div className="w-full h-1 bg-[#1a1a2e] rounded-full mt-1.5 overflow-hidden">
                    <div className="h-full rounded-full transition-all duration-500" style={{ width: `${wr * 100}%`, backgroundColor: wr > 0.5 ? '#22c55e' : wr > 0.3 ? '#eab308' : '#ef4444' }} />
                  </div>
                </div>
                <div>
                  <p className="text-gray-600 text-[10px] uppercase tracking-wider mb-1">PnL</p>
                  <p className={`text-sm font-mono font-semibold ${pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {pnl >= 0 ? '+' : ''}{pnl.toFixed(2)}
                  </p>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {prices.length > 0 && (
        <div className="mt-5 pt-5 border-t border-[#1a1a2e]">
          <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">Live Prices</h3>
          <div className="space-y-2">
            {prices.map((p, i) => (
              <div key={p.symbol} className="flex items-center justify-between py-1.5 px-3 bg-[#0f0f1a] rounded-xl text-sm" style={{ animation: `fadeIn 0.2s ease ${i * 0.03}s both` }}>
                <span className="text-gray-400 font-medium">{p.symbol.replace('USDT', '')}/USDT</span>
                <div className="flex items-center gap-3">
                  <span className="font-mono text-white font-semibold">${p.price?.toFixed(2)}</span>
                  {p.change != null && (
                    <span className={`flex items-center gap-0.5 text-xs font-medium ${p.change >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                        <path d={p.change >= 0 ? 'M12 19V5M5 12l7-7 7 7' : 'M12 5v14M5 12l7 7 7-7'} />
                      </svg>
                      {p.change >= 0 ? '+' : ''}{p.change.toFixed(2)}%
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default AgentPanel
