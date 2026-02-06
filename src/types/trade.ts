/**
 * Trade setup data structure
 * This matches the JSON output from the TradeAnalyzer Gemini gem
 */
export interface TradeSetup {
  ticker: string       // e.g., "$TSLA"
  name: string         // e.g., "Tesla Inc."
  sector: string       // e.g., "Consumer Cyclical"
  entry: string        // e.g., "$182.50"
  stop: string         // e.g., "$175.00"
  structure: string    // e.g., "0.618 Fib"
  trend: string        // e.g., "> 150MA"
  trendLabel: string   // e.g., "Trend"
  analysis: string     // 2-3 sentence thesis
  riskScore: number    // 1-10
  footerTag: string    // e.g., "High Confidence"
  setupType: SetupType
}

export type SetupType = 'perfect' | 'momentum' | 'breakout' | 'risky' | 'avoid'

/**
 * Risk level derived from riskScore
 */
export type RiskLevel = 'low' | 'medium' | 'high'

export function getRiskLevel(score: number): RiskLevel {
  if (score <= 3) return 'low'
  if (score <= 6) return 'medium'
  return 'high'
}

export function getRiskColor(score: number): string {
  const level = getRiskLevel(score)
  switch (level) {
    case 'low': return 'text-accent-green'
    case 'medium': return 'text-accent-gold'
    case 'high': return 'text-accent-red'
  }
}
