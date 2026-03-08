import { TradeSetup } from '../../types/trade'
import RiskMeter from './RiskMeter'

interface TradeCardProps {
  data: TradeSetup
}

export default function TradeCard({ data }: TradeCardProps) {
  return (
    <div className="bg-card-bg border border-border-color rounded-xl p-6 shadow-lg hover:translate-y-[-5px] hover:shadow-2xl hover:border-text-muted transition-all duration-300 flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-start mb-5 pb-4 border-b border-dashed border-border-color">
        <div className="flex flex-col">
          <span className="text-3xl font-black text-text-main leading-none">
            {data.ticker}
          </span>
          <span className="text-xs text-text-muted mt-1">{data.name}</span>
        </div>
        <div className="flex flex-col items-end gap-1.5">
          <span className="bg-white/5 text-text-muted px-3 py-1.5 rounded-md text-xs uppercase font-semibold tracking-wide">
            {data.sector}
          </span>
          {data.source && data.source !== 'Watchlist' && (
            <span className="text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded-full">
              📺 {data.source}
            </span>
          )}
        </div>
      </div>

      {/* Current Price Bar */}
      {data.currentPrice && (
        <div className="flex justify-between items-center bg-black/20 px-3 py-2 rounded-md mb-4 text-sm">
          <span className="text-text-muted text-xs uppercase">Current Price</span>
          <span className="font-bold font-mono text-text-main">{data.currentPrice}</span>
        </div>
      )}

      {/* Data Grid */}
      <div className="grid grid-cols-2 gap-4 mb-5">
        <DataPoint label="Entry Zone" value={data.entry} color="text-accent-green" />
        <DataPoint label="Stop Loss" value={data.stop} color="text-accent-red" />
        <DataPoint label="Structure" value={data.structure} color="text-accent-gold" />
        <DataPoint label={data.trendLabel} value={data.trend} color="text-text-main" />
      </div>

      {/* Analysis */}
      <p className="text-[#bdc3c7] text-sm leading-relaxed mb-5 flex-grow">
        {data.analysis}
      </p>

      {/* Footer */}
      <div className="flex justify-between items-center bg-black/20 px-4 py-3 -mx-6 -mb-6 rounded-b-xl border-t border-border-color">
        <RiskMeter score={data.riskScore} />
        <span className="text-text-muted text-sm">{data.footerTag}</span>
      </div>
    </div>
  )
}

interface DataPointProps {
  label: string
  value: string
  color: string
}

function DataPoint({ label, value, color }: DataPointProps) {
  return (
    <div className="flex flex-col bg-black/20 p-3 rounded-md">
      <span className="text-xs text-text-muted uppercase mb-1">{label}</span>
      <span className={`font-bold font-mono text-lg ${color}`}>{value}</span>
    </div>
  )
}
