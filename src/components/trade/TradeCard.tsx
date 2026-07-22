import { TradeSetup } from '../../types/trade'
import RiskMeter from './RiskMeter'

interface TradeCardProps {
  data: TradeSetup
}

const setupBadge: Record<string, { label: string; cls: string }> = {
  perfect: { label: 'Perfect', cls: 'border-emerald-400/25 bg-emerald-400/10 text-emerald-300' },
  momentum: { label: 'Momentum', cls: 'border-sky-400/25 bg-sky-400/10 text-sky-300' },
  breakout: { label: 'Breakout', cls: 'border-violet-400/25 bg-violet-400/10 text-violet-300' },
  risky: { label: 'Risky', cls: 'border-amber-400/25 bg-amber-400/10 text-amber-300' },
  avoid: { label: 'Avoid', cls: 'border-red-400/25 bg-red-400/10 text-red-300' },
}

export default function TradeCard({ data }: TradeCardProps) {
  const badge = setupBadge[data.setupType] ?? setupBadge.perfect

  return (
    <div className="surface-card lift flex h-full flex-col p-6 shadow-card">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 border-b border-dashed border-white/[0.08] pb-4">
        <div className="min-w-0">
          <span className="font-mono text-2xl font-black leading-none text-text-main">{data.ticker}</span>
          <p className="mt-1 truncate text-xs text-text-muted">{data.name}</p>
        </div>
        <div className="flex flex-col items-end gap-1.5">
          <span className={`rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider ${badge.cls}`}>
            {badge.label}
          </span>
          <span className="text-[10px] uppercase tracking-wide text-text-faint">{data.sector}</span>
          {data.source && data.source !== 'Watchlist' && (
            <span className="rounded-full bg-amber-400/15 px-2 py-0.5 text-[10px] text-amber-300">📺 {data.source}</span>
          )}
        </div>
      </div>

      {/* Current price */}
      {data.currentPrice && (
        <div className="mt-4 flex items-center justify-between rounded-lg border border-white/[0.05] bg-black/20 px-3 py-2">
          <span className="text-[11px] uppercase tracking-wide text-text-faint">Current price</span>
          <span className="font-mono text-sm font-bold tabular text-text-main">{data.currentPrice}</span>
        </div>
      )}

      {/* Data grid */}
      <div className="mt-4 grid grid-cols-2 gap-3">
        <DataPoint label="Entry Zone" value={data.entry} color="text-accent-green" />
        <DataPoint label="Stop Loss" value={data.stop} color="text-accent-red" />
        <DataPoint label="Structure" value={data.structure} color="text-accent-gold" />
        <DataPoint label={data.trendLabel} value={data.trend} color="text-text-main" />
      </div>

      {/* Analysis */}
      <p className="mt-5 flex-grow text-sm leading-relaxed text-text-muted">{data.analysis}</p>

      {/* Footer */}
      <div className="mt-5 flex items-center justify-between border-t border-white/[0.07] pt-4">
        <RiskMeter score={data.riskScore} />
        <span className="text-xs text-text-faint">{data.footerTag}</span>
      </div>
    </div>
  )
}

function DataPoint({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="flex flex-col rounded-lg border border-white/[0.05] bg-black/20 p-3">
      <span className="mb-1 text-[10px] uppercase tracking-wide text-text-faint">{label}</span>
      <span className={`font-mono text-[15px] font-bold leading-tight ${color}`}>{value}</span>
    </div>
  )
}
