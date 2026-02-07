import { getRiskColor } from '../../types/trade'

interface RiskMeterProps {
  score: number
}

export default function RiskMeter({ score }: RiskMeterProps) {
  const colorClass = getRiskColor(score)

  return (
    <div className="flex items-center gap-2">
      <span className="text-text-muted text-sm">Risk Score:</span>
      <span className={`font-bold ${colorClass}`}>{score}/10</span>
    </div>
  )
}
