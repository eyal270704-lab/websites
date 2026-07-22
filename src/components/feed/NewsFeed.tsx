import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { NewsFeed as NewsFeedType, FeedSection, FeedItem } from '../../types/feed'

interface NewsFeedProps {
  feedId: string
  dataFile: string
  theme: {
    gradient: string
    bgGradient: string
    accentColor: 'orange' | 'blue' | 'purple' | 'green'
  }
}

interface AccentTokens {
  text: string
  dot: string
  chip: string
  bar: string
  glow: string
  spinner: string
  quoteBorder: string
}

const accentColors: Record<string, AccentTokens> = {
  orange: {
    text: 'text-orange-300',
    dot: 'bg-orange-400',
    chip: 'border-orange-400/25 bg-orange-400/10 text-orange-200',
    bar: 'from-orange-400 to-red-400',
    glow: 'rgba(251,146,60,0.16)',
    spinner: 'border-orange-500/25 border-t-orange-400',
    quoteBorder: 'border-l-orange-400/60',
  },
  blue: {
    text: 'text-sky-300',
    dot: 'bg-sky-400',
    chip: 'border-sky-400/25 bg-sky-400/10 text-sky-200',
    bar: 'from-sky-400 to-indigo-400',
    glow: 'rgba(56,189,248,0.16)',
    spinner: 'border-sky-500/25 border-t-sky-400',
    quoteBorder: 'border-l-sky-400/60',
  },
  purple: {
    text: 'text-purple-300',
    dot: 'bg-purple-400',
    chip: 'border-purple-400/25 bg-purple-400/10 text-purple-200',
    bar: 'from-purple-400 to-fuchsia-400',
    glow: 'rgba(168,85,247,0.16)',
    spinner: 'border-purple-500/25 border-t-purple-400',
    quoteBorder: 'border-l-purple-400/60',
  },
  green: {
    text: 'text-emerald-300',
    dot: 'bg-emerald-400',
    chip: 'border-emerald-400/25 bg-emerald-400/10 text-emerald-200',
    bar: 'from-emerald-400 to-teal-400',
    glow: 'rgba(52,211,153,0.16)',
    spinner: 'border-emerald-500/25 border-t-emerald-400',
    quoteBorder: 'border-l-emerald-400/60',
  },
}

export default function NewsFeed({ dataFile, theme }: NewsFeedProps) {
  const [feed, setFeed] = useState<NewsFeedType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const colors = accentColors[theme.accentColor]

  useEffect(() => {
    const loadFeed = async () => {
      try {
        const response = await fetch(`${import.meta.env.BASE_URL}data/${dataFile}`)
        if (!response.ok) throw new Error(`Failed to load ${dataFile}`)
        const data = await response.json()
        setFeed(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load feed')
      } finally {
        setLoading(false)
      }
    }
    loadFeed()
  }, [dataFile])

  const AccentGlow = () => (
    <div
      aria-hidden
      className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-80"
      style={{ background: `radial-gradient(50rem 22rem at 50% -6rem, ${colors.glow}, transparent 70%)` }}
    />
  )

  if (loading) {
    return (
      <div className="relative min-h-screen text-text-main">
        <AccentGlow />
        <div className="mx-auto max-w-6xl px-5 py-24 text-center md:px-8">
          <div className={`mb-4 inline-block h-8 w-8 animate-spin rounded-full border-4 ${colors.spinner}`} />
          <p className="text-text-muted">Gathering the latest…</p>
        </div>
      </div>
    )
  }

  if (error || !feed) {
    return (
      <div className="relative min-h-screen text-text-main">
        <AccentGlow />
        <div className="mx-auto max-w-6xl px-5 py-8 md:px-8">
          <BackButton colors={colors} />
          <div className="mx-auto mt-16 max-w-md rounded-2xl border border-white/[0.07] bg-white/[0.02] p-8 text-center">
            <p className="text-red-300">{error || 'This feed is not available right now.'}</p>
            <p className="mt-2 text-sm text-text-muted">The agent may be mid-refresh. Try again shortly.</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="relative min-h-screen text-text-main">
      <AccentGlow />
      <div className="mx-auto max-w-6xl px-5 py-8 md:px-8">
        <BackButton colors={colors} />

        {/* Header */}
        <header className="mb-14 mt-8 animate-fade-in">
          {feed.badge && (
            <span className={`pill mb-5 border ${colors.chip}`}>
              <span className={`h-1.5 w-1.5 rounded-full ${colors.dot} animate-pulse-soft`} />
              {feed.badge}
            </span>
          )}
          <h1 className="max-w-3xl text-balance text-4xl font-extrabold leading-[1.08] tracking-tight md:text-5xl">
            {feed.title}
          </h1>
          {feed.subtitle && (
            <p className="mt-4 max-w-2xl text-base leading-relaxed text-text-muted">{feed.subtitle}</p>
          )}
        </header>

        {/* Sections */}
        <main className="space-y-14">
          {feed.sections.map((section, idx) => (
            <FeedSectionComponent key={section.id} section={section} delay={idx * 0.08} colors={colors} />
          ))}
        </main>

        {/* Footer */}
        <footer className="mt-16 border-t border-white/[0.06] py-8 text-center">
          <p className="text-xs text-text-faint">
            Generated{' '}
            <span className={colors.text}>{new Date(feed.generatedAt).toLocaleString()}</span>
            {' '}· Powered by {feed.generatedBy}
          </p>
          <Link to="/" className="mt-3 inline-block text-xs text-text-faint hover:text-text-muted transition-colors">
            ← Back to the newsroom
          </Link>
        </footer>
      </div>
    </div>
  )
}

function BackButton({ colors }: { colors: AccentTokens }) {
  return (
    <Link
      to="/"
      className={`inline-flex items-center gap-2 text-sm font-medium ${colors.text} transition-opacity hover:opacity-75`}
    >
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
      Newsroom
    </Link>
  )
}

interface FeedSectionProps {
  section: FeedSection
  delay: number
  colors: AccentTokens
}

function FeedSectionComponent({ section, delay, colors }: FeedSectionProps) {
  const layoutClass = section.layout === 'featured'
    ? 'grid grid-cols-1 gap-5'
    : section.layout === 'list'
    ? 'space-y-4'
    : 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5'

  return (
    <section className="animate-fade-in" style={{ animationDelay: `${delay}s` }}>
      {section.title && (
        <h2 className="mb-6 flex items-center gap-3 text-lg font-semibold tracking-tight text-text-main">
          <span className={`h-5 w-1 rounded-full bg-gradient-to-b ${colors.bar}`} />
          {section.title}
        </h2>
      )}
      <div className={layoutClass}>
        {section.items.map((item, idx) => (
          <FeedCard key={item.id} item={item} cardType={section.cardType} delay={delay + idx * 0.05} colors={colors} />
        ))}
      </div>
    </section>
  )
}

interface FeedCardProps {
  item: FeedItem
  cardType: string
  delay: number
  colors: AccentTokens
}

function FeedCard({ item, cardType, delay, colors }: FeedCardProps) {
  switch (cardType) {
    case 'breaking': return <BreakingCard item={item} delay={delay} colors={colors} />
    case 'game': return <GameCard item={item} delay={delay} colors={colors} />
    case 'stock': return <StockCard item={item} delay={delay} colors={colors} />
    case 'stat': return <StatCard item={item} delay={delay} colors={colors} />
    case 'quote': return <QuoteCard item={item} delay={delay} colors={colors} />
    case 'alert': return <AlertCard item={item} delay={delay} />
    case 'article':
    default: return <ArticleCard item={item} delay={delay} colors={colors} />
  }
}

// Treat agent placeholders ("N/A", "-", "") as missing so they never render literally.
function clean(value?: string | number | null): string | undefined {
  if (value === undefined || value === null) return undefined
  const s = String(value).trim()
  if (s === '' || s === '-' || s === '—' || /^n\/?a$/i.test(s)) return undefined
  return s
}

function Tags({ tags, colors }: { tags?: string[]; colors: AccentTokens }) {
  if (!tags || tags.length === 0) return null
  return (
    <div className="mt-4 flex flex-wrap gap-1.5">
      {tags.map(tag => (
        <span key={tag} className={`rounded-md border px-2 py-0.5 text-[11px] ${colors.chip}`}>{tag}</span>
      ))}
    </div>
  )
}

function BreakingCard({ item, delay, colors }: { item: FeedItem; delay: number; colors: AccentTokens }) {
  return (
    <article className="surface-card lift p-6 md:p-7 animate-fade-in" style={{ animationDelay: `${delay}s` }}>
      <span className={`inline-flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider ${colors.text}`}>
        <span className={`h-1.5 w-1.5 rounded-full ${colors.dot}`} />
        Breaking
      </span>
      <h3 className="mt-3 text-2xl font-bold tracking-tight text-text-main">{item.headline}</h3>
      {item.summary && <p className="mt-3 leading-relaxed text-text-muted">{item.summary}</p>}
      <Tags tags={item.tags} colors={colors} />
    </article>
  )
}

function GameCard({ item, delay, colors }: { item: FeedItem; delay: number; colors: AccentTokens }) {
  const isRealGame = Boolean(clean(item.awayTeam) || clean(item.homeTeam))
  return (
    <article className="surface-card p-5 animate-fade-in" style={{ animationDelay: `${delay}s` }}>
      {(item.gameStatus || item.gameTime) && (
        <div className="mb-4 flex items-center justify-between">
          <span className={`text-[11px] font-semibold uppercase tracking-wider ${colors.text}`}>{item.gameStatus}</span>
          {item.gameTime && <span className="text-xs text-text-faint">{item.gameTime}</span>}
        </div>
      )}
      {isRealGame ? (
        <div className="flex items-center justify-between">
          <div className="flex-1 text-center">
            <p className="text-sm font-semibold text-text-muted">{item.awayTeam}</p>
            <p className="mt-1 text-3xl font-black tabular text-text-main">{item.awayScore ?? '—'}</p>
          </div>
          <span className="px-4 text-xs font-medium text-text-faint">vs</span>
          <div className="flex-1 text-center">
            <p className="text-sm font-semibold text-text-muted">{item.homeTeam}</p>
            <p className="mt-1 text-3xl font-black tabular text-text-main">{item.homeScore ?? '—'}</p>
          </div>
        </div>
      ) : (
        item.headline && <h3 className="text-base font-semibold leading-snug text-text-main">{item.headline}</h3>
      )}
      {item.summary && <p className="mt-3 text-sm leading-relaxed text-text-muted">{item.summary}</p>}
    </article>
  )
}

function StockCard({ item, delay, colors }: { item: FeedItem; delay: number; colors: AccentTokens }) {
  const isUp = item.direction === 'up'
  const changeColor = isUp ? 'text-emerald-400' : item.direction === 'down' ? 'text-red-400' : 'text-text-muted'
  const price = clean(item.price)
  const change = clean(item.change)
  const changePercent = clean(item.changePercent)
  const arrow = isUp ? '▲' : item.direction === 'down' ? '▼' : ''
  return (
    <article className="surface-card p-5 animate-fade-in" style={{ animationDelay: `${delay}s` }}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className={`font-mono text-lg font-bold ${colors.text}`}>{item.ticker}</p>
          {clean(item.headline) && <p className="mt-0.5 truncate text-sm text-text-muted">{item.headline}</p>}
        </div>
        <div className="text-right">
          {price && <p className="font-mono text-lg font-bold tabular text-text-main">{price}</p>}
          {(change || changePercent) && (
            <p className={`text-sm font-semibold tabular ${changeColor}`}>
              {arrow && <span className="mr-0.5 text-[10px]">{arrow}</span>}
              {[change, changePercent && `(${changePercent})`].filter(Boolean).join(' ')}
            </p>
          )}
        </div>
      </div>
      {clean(item.summary) && <p className="mt-3 text-sm leading-relaxed text-text-muted">{item.summary}</p>}
    </article>
  )
}

function ArticleCard({ item, delay, colors }: { item: FeedItem; delay: number; colors: AccentTokens }) {
  return (
    <article className="surface-card p-5 animate-fade-in" style={{ animationDelay: `${delay}s` }}>
      <h3 className="text-base font-semibold leading-snug text-text-main">{item.headline}</h3>
      {item.summary && <p className="mt-2 text-sm leading-relaxed text-text-muted">{item.summary}</p>}
      <Tags tags={item.tags} colors={colors} />
      {item.timestamp && (
        <p className="mt-3 text-xs text-text-faint">{new Date(item.timestamp).toLocaleString()}</p>
      )}
    </article>
  )
}

function StatCard({ item, delay, colors }: { item: FeedItem; delay: number; colors: AccentTokens }) {
  const dirColor = item.direction === 'up' ? 'text-emerald-400' : item.direction === 'down' ? 'text-red-400' : colors.text
  return (
    <article className="surface-card p-5 animate-fade-in" style={{ animationDelay: `${delay}s` }}>
      <p className="text-xs uppercase tracking-wider text-text-faint">{item.statLabel}</p>
      <p className={`mt-2 text-3xl font-black tabular ${dirColor}`}>{item.statValue}</p>
      {item.statContext && <p className="mt-1.5 text-sm text-text-muted">{item.statContext}</p>}
      {item.summary && <p className="mt-2 text-xs leading-relaxed text-text-faint">{item.summary}</p>}
    </article>
  )
}

function QuoteCard({ item, delay, colors }: { item: FeedItem; delay: number; colors: AccentTokens }) {
  return (
    <article
      className={`rounded-2xl border border-l-4 border-white/[0.07] bg-white/[0.03] p-5 animate-fade-in ${colors.quoteBorder}`}
      style={{ animationDelay: `${delay}s` }}
    >
      <p className="text-lg italic leading-relaxed text-text-main">“{item.quote}”</p>
      <div className="mt-4 flex items-center gap-2 text-sm">
        <span className={`font-semibold ${colors.text}`}>{item.author}</span>
        {item.source && <span className="text-text-faint">— {item.source}</span>}
      </div>
    </article>
  )
}

function AlertCard({ item, delay }: { item: FeedItem; delay: number }) {
  const colorMap = {
    info: 'border-sky-400/25 bg-sky-400/[0.06] text-sky-200',
    warning: 'border-amber-400/25 bg-amber-400/[0.06] text-amber-200',
    success: 'border-emerald-400/25 bg-emerald-400/[0.06] text-emerald-200',
    error: 'border-red-400/25 bg-red-400/[0.06] text-red-200',
  }
  const alertColors = colorMap[item.alertType || 'info']
  return (
    <div className={`rounded-2xl border p-4 animate-fade-in ${alertColors}`} style={{ animationDelay: `${delay}s` }}>
      <p className="font-semibold">{item.headline}</p>
      {item.summary && <p className="mt-1 text-sm opacity-80">{item.summary}</p>}
    </div>
  )
}
