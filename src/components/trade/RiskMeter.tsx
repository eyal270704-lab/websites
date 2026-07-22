import { getRiskColor, getRiskLevel } from '../../types/trade'

interface RiskMeterProps {
  score: number
}

const barColor: Record<string, string> = {
  low: 'bg-accent-green',
  medium: 'bg-accent-gold',
  high: 'bg-accent-red',
}

export default function RiskMeter({ score }: RiskMeterProps) {
  const colorClass = getRiskColor(score)
  const level = getRiskLevel(score)
  const filled = Math.round((Math.min(Math.max(score, 0), 10) / 10) * 5)

  return (
    <div className="flex items-center gap-2">
      <span className="text-[11px] uppercase tracking-wide text-text-faint">Risk</span>
      <div className="flex items-center gap-1" aria-hidden>
        {Array.from({ length: 5 }).map((_, i) => (
          <span
            key={i}
            className={`h-1.5 w-3 rounded-full ${i < filled ? barColor[level] : 'bg-white/10'}`}
          />
        ))}
      </div>
      <span className={`font-mono text-sm font-bold tabular ${colorClass}`}>{score}/10</span>
    </div>
  )
}
