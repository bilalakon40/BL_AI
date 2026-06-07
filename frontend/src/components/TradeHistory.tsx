import React, { useState, useEffect } from 'react'

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000'

interface Trade {
  time: string; trade_id: string; symbol: string; side: string
  qty: string; price: string; pnl: string | null; status: string
}

const TradeHistory: React.FC = () => {
  const [trades, setTrades] = useState<Trade[]>([])

  useEffect(() => {
    const fetchTrades = async () => {
      try { const r = await fetch(`${API}/api/trades?limit=50`); if (r.ok) setTrades(await r.json()) } catch {}
    }
    fetchTrades()
    const id = setInterval(fetchTrades, 10000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-base font-semibold text-white">Trade History</h2>
        {trades.length > 0 && <span className="text-xs text-gray-600">{trades.length} trades</span>}
      </div>
      {trades.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-10 text-gray-600 gap-2">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" /><path d="M14 2v6h6" />
          </svg>
          <span className="text-sm">No trades yet</span>
        </div>
      ) : (
        <div className="overflow-x-auto -mx-5">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#1a1a2e]">
                {['Time', 'Symbol', 'Side', 'Qty', 'Price', 'PnL', 'Status'].map(h => (
                  <th key={h} className="text-left py-3 px-4 text-gray-500 text-[10px] uppercase tracking-widest font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {trades.map((t, i) => {
                const pnl = t.pnl ? parseFloat(t.pnl) : null
                return (
                  <tr key={t.trade_id} className="border-b border-[#12121a] hover:bg-[#0f0f1a] transition-colors" style={{ animation: `fadeIn 0.2s ease ${i * 0.02}s both` }}>
                    <td className="py-3 px-4 text-gray-500 font-mono text-xs">{new Date(t.time).toLocaleTimeString()}</td>
                    <td className="py-3 px-4 text-white font-medium text-xs">{t.symbol}</td>
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[10px] font-bold tracking-wide ${
                        t.side === 'BUY' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'
                      }`}>
                        <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                          <path d={t.side === 'BUY' ? 'M12 19V5M5 12l7-7 7 7' : 'M12 5v14M5 12l7 7 7-7'} />
                        </svg>
                        {t.side}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-gray-300 text-xs">{parseFloat(t.qty).toFixed(4)}</td>
                    <td className="py-3 px-4 text-right font-mono text-gray-300 text-xs">${parseFloat(t.price).toFixed(2)}</td>
                    <td className={`py-3 px-4 text-right font-mono text-xs font-semibold ${pnl != null ? (pnl >= 0 ? 'text-emerald-400' : 'text-red-400') : 'text-gray-600'}`}>
                      {pnl != null ? `${pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}` : '—'}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium ${
                        t.status === 'filled' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-yellow-500/10 text-yellow-400'
                      }`}>
                        <span className={`w-1 h-1 rounded-full ${t.status === 'filled' ? 'bg-emerald-400' : 'bg-yellow-400'}`} />
                        {t.status}
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default TradeHistory
