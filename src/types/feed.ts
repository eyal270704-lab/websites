/**
 * Extensible News Feed Schema
 *
 * This schema is designed to be agent-friendly:
 * - Adding a new feed type = add config + prompt (no code changes)
 * - Gemini outputs JSON matching this schema
 * - React renders based on feedType and cardType
 */

// Feed types - extend this as agents create new feeds
export type FeedType = 'nba' | 'stocks' | 'creator' | 'tech' | 'crypto' | 'weather' | string

// Card layouts - determines how content is rendered
export type CardType =
  | 'breaking'      // Big headline, prominent
  | 'game'          // Sports game with scores
  | 'stock'         // Ticker with price/change
  | 'article'       // Standard news article
  | 'stat'          // Key statistic highlight
  | 'list'          // Bullet list of items
  | 'quote'         // Featured quote
  | 'alert'         // Warning/important notice

// Base structure for all feeds
export interface NewsFeed {
  generatedAt: string           // ISO timestamp
  generatedBy: string           // Agent identifier
  feedType: FeedType

  // Header
  title: string                 // "NBA Daily News"
  subtitle?: string             // "February 7, 2026"
  badge?: string                // "LIVE" or "Updated 2h ago"

  // Theme (optional - falls back to feedType defaults)
  theme?: {
    gradient: string            // "from-orange-500 to-red-500"
    accentColor: string         // "orange"
  }

  // Content sections
  sections: FeedSection[]
}

export interface FeedSection {
  id: string                    // Unique section ID
  title?: string                // "Breaking News", "Today's Games"
  cardType: CardType            // How to render cards in this section
  layout?: 'grid' | 'list' | 'featured'  // Section layout
  items: FeedItem[]
}

// Flexible item structure - fields used depend on cardType
export interface FeedItem {
  id: string

  // Common fields
  headline: string
  summary?: string
  timestamp?: string
  tags?: string[]
  imageUrl?: string
  link?: string

  // Game-specific (cardType: 'game')
  homeTeam?: string
  awayTeam?: string
  homeScore?: number
  awayScore?: number
  gameStatus?: 'scheduled' | 'live' | 'final'
  gameTime?: string

  // Stock-specific (cardType: 'stock')
  ticker?: string
  price?: string
  change?: string
  changePercent?: string
  direction?: 'up' | 'down' | 'flat'

  // Stat-specific (cardType: 'stat')
  statLabel?: string
  statValue?: string
  statContext?: string

  // Quote-specific (cardType: 'quote')
  quote?: string
  author?: string
  source?: string

  // Alert-specific (cardType: 'alert')
  alertType?: 'info' | 'warning' | 'success' | 'error'

  // Extensible: agents can add custom fields
  [key: string]: unknown
}

// Config for each feed type (stored in newsfeeds.json)
export interface FeedConfig {
  id: string                    // "nba"
  name: string                  // "Basketball News"
  route: string                 // "/basketball-news"
  dataFile: string              // "nba.json"
  promptFile: string            // "agents/prompts/nba.md"
  schedule: string              // "0 8 * * *"
  theme: {
    gradient: string
    icon: string                // SVG path or icon name
  }
  enabled: boolean
}
