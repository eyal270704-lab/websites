import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import TradeCard from '../components/trade/TradeCard'
import { TradeSetup } from '../types/trade'

export default function TradeWatcher() {
  const [trades, setTrades] = useState<TradeSetup[]>([])
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<string>('')

  useEffect(() => {
    const loadTrades = async () => {
      try {
        const response = await fetch(`${import.meta.env.BASE_URL}data/trades.json`)
        if (response.ok) {
          const data = await response.json()
          setTrades(data.trades || [])
          setLastUpdated(new Date(data.generatedAt).toLocaleString('en-US', {
            weekday: 'short',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          }))
        } else {
          setTrades([])
          setLastUpdated('')
        }
      } catch (error) {
        console.error('Failed to load trades:', error)
        setTrades([])
        setLastUpdated('')
      } finally {
        setLoading(false)
      }
    }
    loadTrades()
  }, [])

  return (
    <div className="relative min-h-screen text-text-main">
      {/* Amber accent glow */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-80"
        style={{ background: 'radial-gradient(50rem 22rem at 50% -6rem, rgba(245,181,68,0.16), transparent 70%)' }}
      />

      <div className="mx-auto max-w-6xl px-5 py-8 md:px-8">
        {/* Back */}
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-sm font-medium text-amber-300 transition-opacity hover:opacity-75"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Newsroom
        </Link>

        {/* Header */}
        <header className="mb-10 mt-8 animate-fade-in">
          <span className="pill mb-5 border border-amber-400/25 bg-amber-400/10 text-amber-200">
            <span className="h-1.5 w-1.5 rounded-full bg-amber-400 animate-pulse-soft" />
            Trade Watcher desk
          </span>
          <h1 className="max-w-3xl text-balance text-4xl font-extrabold leading-[1.06] tracking-tight md:text-5xl">
            Daily swing-trade setups,
            <span className="bg-gradient-to-r from-amber-300 to-orange-400 bg-clip-text text-transparent"> scored by an agent.</span>
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-text-muted">
            Each weekday morning the analyzer scans the watchlist for Golden-Zone pullbacks, checks trend against the
            150-day moving average, and flags catalyst risk — then rates every candidate 1–10.
          </p>
          <div className="mt-5 flex flex-wrap gap-2">
            <span className="pill border border-amber-400/25 bg-amber-400/10 text-amber-200">Golden Zone · 0.618 Fib</span>
            <span className="pill">150-day MA trend</span>
            <span className="pill">Catalyst-aware risk</span>
          </div>
        </header>

        {/* Stats */}
        <div className="mb-8 grid grid-cols-2 gap-3 animate-fade-in md:grid-cols-4" style={{ animationDelay: '0.1s' }}>
          <StatTile label="Active Setups" value={trades.filter(t => t.setupType !== 'avoid').length} color="text-emerald-400" />
          <StatTile label="High Confidence" value={trades.filter(t => t.riskScore <= 3).length} color="text-amber-300" />
          <StatTile label="Momentum Plays" value={trades.filter(t => t.setupType === 'momentum').length} color="text-sky-400" />
          <StatTile label="Total Analyzed" value={trades.length} color="text-text-muted" />
        </div>

        {/* Content */}
        <main>
          {loading ? (
            <div className="py-24 text-center text-text-muted">
              <div className="mb-4 inline-block h-8 w-8 animate-spin rounded-full border-4 border-amber-500/25 border-t-amber-400" />
              <p>Loading trade setups…</p>
            </div>
          ) : trades.length === 0 ? (
            <div className="mx-auto mt-6 max-w-md rounded-2xl border border-white/[0.07] bg-white/[0.02] p-8 text-center">
              <svg className="mx-auto mb-4 h-10 w-10 text-amber-300/70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="text-lg font-semibold text-text-main">No setups yet today</h3>
              <p className="mt-2 text-sm text-text-muted">
                The analyzer runs weekday mornings at 6:00 AM UTC. Check back once the market scan completes.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
              {trades.map((trade, index) => (
                <div key={`${trade.ticker}-${index}`} className="animate-fade-in" style={{ animationDelay: `${0.15 + index * 0.07}s` }}>
                  <TradeCard data={trade} />
                </div>
              ))}
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="mt-16 border-t border-white/[0.06] py-8 text-center">
          <p className="text-xs text-text-faint">
            Last scan: <span className="text-amber-300/80">{lastUpdated || '—'}</span> · Generated by the Trade Analyzer agent
          </p>
          <p className="mt-2 text-xs text-text-faint">
            For information only — not financial advice.
          </p>
        </footer>
      </div>
    </div>
  )
}

function StatTile({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="surface-card p-4">
      <p className={`text-3xl font-black tabular ${color}`}>{value}</p>
      <p className="mt-1 text-xs uppercase tracking-wider text-text-faint">{label}</p>
    </div>
  )
}
