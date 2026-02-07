import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { NewsFeed as NewsFeedType, FeedSection, FeedItem } from '../../types/feed'

interface NewsFeedProps {
  feedId: string
  dataFile: string
  theme: {
    gradient: string
  }
}

export default function NewsFeed({ dataFile, theme }: NewsFeedProps) {
  const [feed, setFeed] = useState<NewsFeedType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadFeed = async () => {
      try {
        const response = await fetch(`${import.meta.env.BASE_URL}data/${dataFile}`)
        if (!response.ok) {
          throw new Error(`Failed to load ${dataFile}`)
        }
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900/50 to-slate-900 text-white p-5">
        <div className="max-w-7xl mx-auto text-center py-20">
          <div className="inline-block w-8 h-8 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }

  if (error || !feed) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900/50 to-slate-900 text-white p-5">
        <div className="max-w-7xl mx-auto">
          <BackButton />
          <div className="text-center py-20">
            <p className="text-red-400">{error || 'Feed not available'}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900/50 to-slate-900 text-white p-5">
      <div className="max-w-7xl mx-auto">
        <BackButton />

        {/* Header */}
        <header className="text-center mb-12 pb-8 border-b border-purple-500/20 animate-fade-in">
          <h1 className={`text-4xl md:text-5xl font-extrabold bg-gradient-to-r ${theme.gradient} bg-clip-text text-transparent`}>
            {feed.title}
          </h1>
          {feed.subtitle && (
            <p className="text-gray-400 mt-3">{feed.subtitle}</p>
          )}
          {feed.badge && (
            <span className="inline-flex items-center gap-2 bg-purple-500/10 text-purple-400 border border-purple-500/30 px-4 py-2 rounded-full text-xs font-semibold mt-4">
              <span className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></span>
              {feed.badge}
            </span>
          )}
        </header>

        {/* Sections */}
        <main className="space-y-12">
          {feed.sections.map((section, idx) => (
            <FeedSectionComponent
              key={section.id}
              section={section}
              delay={idx * 0.1}
              theme={theme}
            />
          ))}
        </main>

        {/* Footer */}
        <footer className="text-center mt-16 pb-8">
          <p className="text-gray-500 text-xs">
            Generated: <span className="text-purple-400/70">
              {new Date(feed.generatedAt).toLocaleString()}
            </span>
          </p>
          <p className="text-gray-600 text-xs mt-2">
            Powered by {feed.generatedBy}
          </p>
        </footer>
      </div>

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

function BackButton() {
  return (
    <div className="mb-6">
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
  )
}

interface FeedSectionProps {
  section: FeedSection
  delay: number
  theme: { gradient: string }
}

function FeedSectionComponent({ section, delay, theme }: FeedSectionProps) {
  const layoutClass = section.layout === 'featured'
    ? 'grid grid-cols-1 gap-6'
    : section.layout === 'list'
    ? 'space-y-4'
    : 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'

  return (
    <section className="animate-fade-in" style={{ animationDelay: `${delay}s` }}>
      {section.title && (
        <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
          <span className={`w-1 h-8 bg-gradient-to-b ${theme.gradient} rounded-full`}></span>
          {section.title}
        </h2>
      )}
      <div className={layoutClass}>
        {section.items.map((item, idx) => (
          <FeedCard
            key={item.id}
            item={item}
            cardType={section.cardType}
            delay={delay + idx * 0.05}
          />
        ))}
      </div>
    </section>
  )
}

interface FeedCardProps {
  item: FeedItem
  cardType: string
  delay: number
}

function FeedCard({ item, cardType, delay }: FeedCardProps) {
  // Render different card types
  switch (cardType) {
    case 'breaking':
      return <BreakingCard item={item} delay={delay} />
    case 'game':
      return <GameCard item={item} delay={delay} />
    case 'stock':
      return <StockCard item={item} delay={delay} />
    case 'stat':
      return <StatCard item={item} delay={delay} />
    case 'quote':
      return <QuoteCard item={item} delay={delay} />
    case 'alert':
      return <AlertCard item={item} delay={delay} />
    case 'article':
    default:
      return <ArticleCard item={item} delay={delay} />
  }
}

// Card Components

function BreakingCard({ item, delay }: { item: FeedItem; delay: number }) {
  return (
    <div
      className="bg-red-900/20 border border-red-500/30 rounded-xl p-6 animate-fade-in"
      style={{ animationDelay: `${delay}s` }}
    >
      <span className="text-xs text-red-400 uppercase font-semibold tracking-wide">Breaking</span>
      <h3 className="text-2xl font-bold text-white mt-2">{item.headline}</h3>
      {item.summary && <p className="text-gray-300 mt-3">{item.summary}</p>}
      {item.tags && (
        <div className="flex gap-2 mt-4">
          {item.tags.map(tag => (
            <span key={tag} className="text-xs bg-red-500/20 text-red-300 px-2 py-1 rounded">{tag}</span>
          ))}
        </div>
      )}
    </div>
  )
}

function GameCard({ item, delay }: { item: FeedItem; delay: number }) {
  return (
    <div
      className="bg-purple-900/20 border border-purple-500/20 rounded-xl p-5 animate-fade-in"
      style={{ animationDelay: `${delay}s` }}
    >
      <div className="flex justify-between items-center mb-4">
        <span className="text-xs text-gray-400 uppercase">{item.gameStatus}</span>
        {item.gameTime && <span className="text-xs text-gray-500">{item.gameTime}</span>}
      </div>
      <div className="flex justify-between items-center">
        <div className="text-center flex-1">
          <p className="text-lg font-bold text-white">{item.awayTeam}</p>
          <p className="text-3xl font-black text-white mt-1">{item.awayScore ?? '-'}</p>
        </div>
        <span className="text-gray-500 text-sm px-4">vs</span>
        <div className="text-center flex-1">
          <p className="text-lg font-bold text-white">{item.homeTeam}</p>
          <p className="text-3xl font-black text-white mt-1">{item.homeScore ?? '-'}</p>
        </div>
      </div>
    </div>
  )
}

function StockCard({ item, delay }: { item: FeedItem; delay: number }) {
  const isUp = item.direction === 'up'
  const colorClass = isUp ? 'text-green-400' : item.direction === 'down' ? 'text-red-400' : 'text-gray-400'

  return (
    <div
      className="bg-purple-900/20 border border-purple-500/20 rounded-xl p-5 animate-fade-in"
      style={{ animationDelay: `${delay}s` }}
    >
      <div className="flex justify-between items-start">
        <div>
          <p className="text-xl font-bold text-white">{item.ticker}</p>
          <p className="text-sm text-gray-400">{item.headline}</p>
        </div>
        <div className="text-right">
          <p className="text-xl font-bold text-white">{item.price}</p>
          <p className={`text-sm font-semibold ${colorClass}`}>
            {item.change} ({item.changePercent})
          </p>
        </div>
      </div>
      {item.summary && <p className="text-gray-300 text-sm mt-3">{item.summary}</p>}
    </div>
  )
}

function ArticleCard({ item, delay }: { item: FeedItem; delay: number }) {
  return (
    <div
      className="bg-purple-900/20 border border-purple-500/20 rounded-xl p-5 hover:border-purple-500/40 transition-colors animate-fade-in"
      style={{ animationDelay: `${delay}s` }}
    >
      <h3 className="text-lg font-bold text-white">{item.headline}</h3>
      {item.summary && <p className="text-gray-300 text-sm mt-2 line-clamp-3">{item.summary}</p>}
      {item.tags && (
        <div className="flex gap-2 mt-4">
          {item.tags.map(tag => (
            <span key={tag} className="text-xs bg-purple-500/20 text-purple-300 px-2 py-1 rounded">{tag}</span>
          ))}
        </div>
      )}
      {item.timestamp && (
        <p className="text-xs text-gray-500 mt-3">{item.timestamp}</p>
      )}
    </div>
  )
}

function StatCard({ item, delay }: { item: FeedItem; delay: number }) {
  return (
    <div
      className="bg-purple-900/20 border border-purple-500/20 rounded-xl p-5 text-center animate-fade-in"
      style={{ animationDelay: `${delay}s` }}
    >
      <p className="text-sm text-gray-400 uppercase tracking-wide">{item.statLabel}</p>
      <p className="text-4xl font-black text-white mt-2">{item.statValue}</p>
      {item.statContext && <p className="text-sm text-gray-400 mt-2">{item.statContext}</p>}
    </div>
  )
}

function QuoteCard({ item, delay }: { item: FeedItem; delay: number }) {
  return (
    <div
      className="bg-purple-900/20 border-l-4 border-purple-500 rounded-r-xl p-5 animate-fade-in"
      style={{ animationDelay: `${delay}s` }}
    >
      <p className="text-lg text-white italic">"{item.quote}"</p>
      <div className="mt-4 flex items-center gap-2">
        <span className="text-purple-400 font-semibold">{item.author}</span>
        {item.source && <span className="text-gray-500 text-sm">— {item.source}</span>}
      </div>
    </div>
  )
}

function AlertCard({ item, delay }: { item: FeedItem; delay: number }) {
  const colorMap = {
    info: 'bg-blue-900/20 border-blue-500/30 text-blue-300',
    warning: 'bg-yellow-900/20 border-yellow-500/30 text-yellow-300',
    success: 'bg-green-900/20 border-green-500/30 text-green-300',
    error: 'bg-red-900/20 border-red-500/30 text-red-300'
  }
  const colors = colorMap[item.alertType || 'info']

  return (
    <div
      className={`${colors} border rounded-xl p-4 animate-fade-in`}
      style={{ animationDelay: `${delay}s` }}
    >
      <p className="font-semibold">{item.headline}</p>
      {item.summary && <p className="text-sm mt-1 opacity-80">{item.summary}</p>}
    </div>
  )
}
