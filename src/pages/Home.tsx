import { Link } from 'react-router-dom'

interface PageDef {
  title: string
  description: string
  path: string
  badge?: string
  accent: string
  glow: string
  tags: string[]
  cadence: string
  external?: boolean
  icon: React.ReactNode
}

const pages: PageDef[] = [
  {
    title: 'Trade Watcher',
    description: 'Daily swing-trade setups scored on Fibonacci structure, moving-average trend, and catalyst risk.',
    path: '/trade-watcher',
    badge: 'Flagship',
    accent: 'text-amber-300',
    glow: 'group-hover:shadow-[0_24px_60px_-24px_rgba(245,181,68,0.5)]',
    tags: ['Swing Trades', 'Fibonacci', 'Risk Scored'],
    cadence: 'Weekday mornings',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    )
  },
  {
    title: 'Stock Market',
    description: 'A daily market digest — index moves, top movers, and the stories driving the tape.',
    path: '/stock-market-news',
    accent: 'text-sky-300',
    glow: 'group-hover:shadow-[0_24px_60px_-24px_rgba(56,189,248,0.5)]',
    tags: ['Indices', 'Movers', 'Analysis'],
    cadence: 'Three times daily',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
      </svg>
    )
  },
  {
    title: 'NBA News',
    description: 'Scores, standouts, and the league rumor mill — a fresh rundown every morning.',
    path: '/basketball-news',
    accent: 'text-orange-300',
    glow: 'group-hover:shadow-[0_24px_60px_-24px_rgba(251,146,60,0.5)]',
    tags: ['Scores', 'Highlights', 'Rumors'],
    cadence: 'Every morning',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  },
  {
    title: 'Creator Monetization',
    description: 'A side-by-side look at how YouTube, TikTok, and Instagram pay their creators.',
    path: '/creator-monetization.html',
    external: true,
    accent: 'text-emerald-300',
    glow: 'group-hover:shadow-[0_24px_60px_-24px_rgba(52,211,153,0.5)]',
    tags: ['YouTube', 'TikTok', 'Instagram'],
    cadence: 'Reference',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  }
]

export default function Home() {
  return (
    <div className="min-h-screen text-text-main">
      <div className="mx-auto max-w-6xl px-5 md:px-8">
        {/* Top bar */}
        <nav className="flex items-center justify-between py-6 animate-fade-in">
          <div className="flex items-center gap-2.5">
            <span className="grid h-8 w-8 place-items-center rounded-lg border border-white/10 bg-white/[0.04] text-sm font-black tracking-tight">
              A
            </span>
            <span className="text-sm font-semibold tracking-tight text-text-main">Agentic Newsroom</span>
          </div>
          <Link
            to="/workflows"
            className="pill hover:border-white/20 hover:text-text-main transition-colors"
          >
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse-soft" />
            System status
          </Link>
        </nav>

        {/* Hero */}
        <header className="pt-10 pb-14 md:pt-16 md:pb-20 animate-fade-in" style={{ animationDelay: '0.05s' }}>
          <span className="pill mb-6">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-emerald-400" />
            Run entirely by autonomous AI agents
          </span>
          <h1 className="max-w-3xl text-balance text-4xl font-extrabold leading-[1.05] tracking-tight md:text-6xl">
            A newsroom that writes,
            <br className="hidden sm:block" />
            <span className="bg-gradient-to-r from-white via-white to-white/50 bg-clip-text text-transparent">
              {' '}monitors, and fixes itself.
            </span>
          </h1>
          <p className="mt-6 max-w-xl text-base leading-relaxed text-text-muted md:text-lg">
            A team of AI agents researches, drafts, and publishes daily coverage across markets, basketball,
            and swing trading — then quietly heals its own pipelines when something breaks. No editors. No days off.
          </p>

          <div className="mt-8 flex flex-wrap items-center gap-x-7 gap-y-3 text-sm text-text-faint">
            <div className="flex items-center gap-2">
              <span className="inline-block h-2 w-2 rounded-full bg-emerald-400 animate-pulse-soft" />
              <span className="text-text-muted">Live &amp; self-updating</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="inline-block h-2 w-2 rounded-full bg-sky-400" />
              <span className="text-text-muted">4 autonomous agents</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="inline-block h-2 w-2 rounded-full bg-amber-400" />
              <span className="text-text-muted">Refreshed around the clock</span>
            </div>
          </div>
        </header>

        {/* Cards */}
        <main>
          <div className="mb-4 flex items-baseline justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-text-faint">The desks</h2>
            <span className="text-xs text-text-faint">4 live sections</span>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {pages.map((page, index) => (
              <Card key={page.path} page={page} delay={0.1 + index * 0.07} />
            ))}
          </div>

          {/* Coming soon */}
          <div className="mt-6 overflow-hidden rounded-2xl border border-white/[0.07] bg-white/[0.02] p-8 animate-fade-in" style={{ animationDelay: '0.5s' }}>
            <div className="flex flex-col items-start justify-between gap-6 md:flex-row md:items-center">
              <div>
                <h3 className="text-lg font-semibold">New desks in the pipeline</h3>
                <p className="mt-1.5 max-w-md text-sm text-text-muted">
                  The Ticker Scout agent is next — it will listen to livestreams and reshape the trade watchlist on its own.
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                {['Ticker Scout', 'Crypto', 'Tech', 'Weather'].map(tag => (
                  <span key={tag} className="rounded-full border border-white/[0.08] bg-white/[0.03] px-3 py-1.5 text-xs text-text-muted">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="mt-16 flex flex-col items-center justify-between gap-3 border-t border-white/[0.06] py-8 text-xs text-text-faint sm:flex-row">
          <p>&copy; 2026 Agentic Newsroom · Written &amp; maintained by autonomous agents.</p>
          <Link to="/workflows" className="hover:text-text-muted transition-colors">View the pipeline →</Link>
        </footer>
      </div>
    </div>
  )
}

function Card({ page, delay }: { page: PageDef; delay: number }) {
  const inner = (
    <>
      <div className="mb-5 flex items-start justify-between">
        <span className={`grid h-11 w-11 place-items-center rounded-xl border border-white/10 bg-white/[0.05] ${page.accent}`}>
          {page.icon}
        </span>
        {page.badge ? (
          <span className={`rounded-full border border-white/10 bg-white/[0.05] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider ${page.accent}`}>
            {page.badge}
          </span>
        ) : (
          <span className="text-[10px] font-medium uppercase tracking-wider text-text-faint">Live</span>
        )}
      </div>

      <h3 className="text-xl font-semibold tracking-tight text-text-main">{page.title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-text-muted">{page.description}</p>

      <div className="mt-4 flex flex-wrap gap-1.5">
        {page.tags.map(tag => (
          <span key={tag} className="rounded-md border border-white/[0.06] bg-white/[0.03] px-2 py-0.5 text-[11px] text-text-faint">
            {tag}
          </span>
        ))}
      </div>

      <div className="mt-6 flex items-center justify-between border-t border-white/[0.06] pt-4">
        <span className={`inline-flex items-center gap-1.5 text-sm font-medium ${page.accent}`}>
          Open desk
          <svg className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </span>
        <span className="text-xs text-text-faint">{page.cadence}</span>
      </div>
    </>
  )

  const cls = `group surface-card lift block p-6 animate-fade-in ${page.glow}`

  if (page.external) {
    const fullPath = `${import.meta.env.BASE_URL}${page.path.replace(/^\//, '')}`
    return (
      <a href={fullPath} className={cls} style={{ animationDelay: `${delay}s` }}>
        {inner}
      </a>
    )
  }

  return (
    <Link to={page.path} className={cls} style={{ animationDelay: `${delay}s` }}>
      {inner}
    </Link>
  )
}
