import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import TradeCard from '../components/trade/TradeCard'
import { TradeSetup } from '../types/trade'

// Mock data for development - will be replaced by fetched JSON
const MOCK_TRADES: TradeSetup[] = [
  {
    ticker: "$TSLA",
    name: "Tesla Inc.",
    sector: "Consumer Cyclical",
    entry: "$182.50",
    stop: "$175.00",
    structure: "0.618 Fib",
    trend: "> 150MA",
    trendLabel: "Trend",
    analysis: "Stock is flagging nicely above the 150-day MA. Just touched the Golden Zone (0.618) on the daily chart with volume drying up, suggesting sellers are exhausted.",
    riskScore: 3,
    footerTag: "High Confidence",
    setupType: "perfect"
  },
  {
    ticker: "$NVDA",
    name: "NVIDIA Corp.",
    sector: "Technology",
    entry: "$940.00",
    stop: "$915.00",
    structure: "0.5 Fib",
    trend: "1.5x",
    trendLabel: "RVOL",
    analysis: "Aggressive momentum play. Bounced off the 20-day MA which aligns with the 0.5 Fibonacci retracement. Strong relative strength vs QQQ.",
    riskScore: 5,
    footerTag: "Momentum",
    setupType: "momentum"
  },
  {
    ticker: "$PLTR",
    name: "Palantir Tech",
    sector: "Software",
    entry: "$24.15",
    stop: "$22.80",
    structure: "Support Test",
    trend: "Uptrend",
    trendLabel: "Trend",
    analysis: "Classic breakout and retest of previous resistance which is now acting as floor. Volume is increasing on green days indicating accumulation.",
    riskScore: 4,
    footerTag: "Accumulation",
    setupType: "breakout"
  }
]

export default function TradeWatcher() {
  const [trades, setTrades] = useState<TradeSetup[]>([])
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<string>('')

  useEffect(() => {
    const loadTrades = async () => {
      try {
        // Try to fetch from JSON file first
        const response = await fetch(`${import.meta.env.BASE_URL}data/trades.json`)
        if (response.ok) {
          const data = await response.json()
          setTrades(data.trades)
          setLastUpdated(new Date(data.generatedAt).toLocaleString('en-US', {
            weekday: 'short',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          }))
        } else {
          // Fall back to mock data during development
          console.log('Using mock data (JSON not available)')
          setTrades(MOCK_TRADES)
          setLastUpdated(new Date().toLocaleString('en-US', {
            weekday: 'short',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          }))
        }
      } catch (error) {
        // Fall back to mock data on error
        console.log('Using mock data (fetch failed)')
        setTrades(MOCK_TRADES)
        setLastUpdated(new Date().toLocaleString('en-US', {
          weekday: 'short',
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        }))
      } finally {
        setLoading(false)
      }
    }

    loadTrades()
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900/50 to-slate-900 text-white p-5">
      {/* Back Button */}
      <div className="max-w-7xl mx-auto mb-6">
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 transition-colors text-sm font-medium"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Hub
        </Link>
      </div>

      {/* Header */}
      <header className="text-center mb-12 pb-8 border-b border-purple-500/20 max-w-7xl mx-auto animate-fade-in">
        <div className="flex justify-center mb-4">
          <div className="bg-gradient-to-r from-amber-500 to-orange-500 p-3 rounded-xl">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
        </div>
        <h1 className="text-4xl md:text-5xl font-extrabold bg-gradient-to-r from-amber-400 via-orange-400 to-yellow-400 bg-clip-text text-transparent uppercase tracking-wide">
          MarketFlow AI
        </h1>
        <p className="text-gray-400 mt-3 max-w-xl mx-auto">
          Daily Swing Trade Signals based on Technical Momentum & Fibonacci Structures
        </p>
        <div className="flex justify-center gap-4 mt-4">
          <span className="inline-flex items-center gap-2 bg-amber-500/10 text-amber-400 border border-amber-500/30 px-4 py-2 rounded-full text-xs font-semibold">
            <span className="w-2 h-2 bg-amber-400 rounded-full animate-pulse"></span>
            Golden Zone (0.618 Fib)
          </span>
          <span className="inline-flex items-center gap-2 bg-purple-500/10 text-purple-400 border border-purple-500/30 px-4 py-2 rounded-full text-xs font-semibold">
            150MA Trend
          </span>
        </div>
      </header>

      {/* Stats Bar */}
      <div className="max-w-7xl mx-auto mb-8 animate-fade-in" style={{ animationDelay: '0.1s' }}>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="Active Setups" value={trades.filter(t => t.setupType !== 'avoid').length.toString()} color="text-green-400" />
          <StatCard label="High Confidence" value={trades.filter(t => t.riskScore <= 3).length.toString()} color="text-amber-400" />
          <StatCard label="Momentum Plays" value={trades.filter(t => t.setupType === 'momentum').length.toString()} color="text-blue-400" />
          <StatCard label="Total Analyzed" value={trades.length.toString()} color="text-gray-400" />
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto">
        {loading ? (
          <div className="text-center text-gray-400 py-20">
            <div className="inline-block w-8 h-8 border-4 border-purple-500/30 border-t-amber-500 rounded-full animate-spin mb-4"></div>
            <p>Loading trade setups...</p>
          </div>
        ) : trades.length === 0 ? (
          <div className="text-center text-gray-400 py-20">
            <p>No trade setups available</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {trades.map((trade, index) => (
              <div
                key={`${trade.ticker}-${index}`}
                className="animate-fade-in"
                style={{ animationDelay: `${0.2 + index * 0.1}s` }}
              >
                <TradeCard data={trade} />
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="text-center mt-16 pb-8">
        <p className="text-gray-500 text-xs">
          System Generated: <span className="text-purple-400/70">{lastUpdated}</span>
        </p>
        <p className="text-gray-600 text-xs mt-2">
          Powered by TradeAnalyzer AI • Not financial advice
        </p>
      </footer>

      {/* Animations */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fadeIn 0.6s ease-out forwards;
          opacity: 0;
        }
      `}</style>
    </div>
  )
}

interface StatCardProps {
  label: string
  value: string
  color: string
}

function StatCard({ label, value, color }: StatCardProps) {
  return (
    <div className="bg-purple-900/20 backdrop-blur-sm border border-purple-500/20 rounded-xl p-4 text-center">
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-500 uppercase tracking-wide mt-1">{label}</p>
    </div>
  )
}
