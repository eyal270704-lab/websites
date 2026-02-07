import { Link } from 'react-router-dom'

const pages = [
  {
    title: 'Trade Watcher',
    description: 'AI-powered swing trade analysis using the Golden Zone strategy.',
    path: '/trade-watcher',
    badge: 'NEW',
    gradient: 'from-amber-500 to-orange-600',
    tags: ['Swing Trades', 'Fibonacci'],
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    )
  },
  {
    title: 'Stock Market',
    description: 'Real-time market updates, trending stocks, and AI analysis.',
    path: '/stock-market-news',
    gradient: 'from-blue-500 to-indigo-600',
    tags: ['Stocks', 'Analysis'],
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
      </svg>
    )
  },
  {
    title: 'NBA News',
    description: 'Daily updates on games, scores, and player highlights.',
    path: '/basketball-news',
    gradient: 'from-orange-500 to-red-500',
    tags: ['NBA', 'Scores'],
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  },
  {
    title: 'Creator Monetization',
    description: 'Compare YouTube, TikTok, and Instagram monetization.',
    path: '/creator-monetization.html',
    external: true,
    gradient: 'from-teal-500 to-emerald-600',
    tags: ['YouTube', 'TikTok'],
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  }
]

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-4 md:p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="text-center mb-10 pt-6 animate-fade-in">
          <h1 className="text-4xl md:text-5xl font-bold mb-3 bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            Daily News Hub
          </h1>
          <p className="text-lg text-gray-300 max-w-2xl mx-auto mb-4">
            Your curated collection of data-driven websites, updated daily
          </p>
          <div className="flex justify-center gap-6 text-xs text-gray-400">
            <div className="flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
              <span>Live & Updated Daily</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-blue-400 rounded-full"></span>
              <span>AI-Powered Content</span>
            </div>
          </div>
        </header>

        {/* Cards Grid - 2x2 on medium screens, smaller cards */}
        <main>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
            {pages.map((page, index) => (
              <Card key={page.path} {...page} delay={index * 0.1} />
            ))}
          </div>

          {/* Coming Soon Banner */}
          <div className="text-center bg-gradient-to-r from-purple-800/80 to-indigo-800/80 rounded-xl p-8 shadow-xl animate-fade-in">
            <h3 className="text-xl font-bold mb-3">More Coming Soon</h3>
            <p className="text-sm text-gray-200 mb-4 max-w-xl mx-auto">
              We're constantly adding new data-driven websites. Check back for updates!
            </p>
            <div className="flex flex-wrap justify-center gap-2 text-xs">
              <span className="bg-white/10 px-3 py-1.5 rounded-full">Tech News</span>
              <span className="bg-white/10 px-3 py-1.5 rounded-full">Weather</span>
              <span className="bg-white/10 px-3 py-1.5 rounded-full">Crypto</span>
              <span className="bg-white/10 px-3 py-1.5 rounded-full">Gaming</span>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="mt-10 text-center text-gray-500 text-xs">
          <p>&copy; 2026 Daily News Hub. Updated daily via automated pipelines.</p>
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
        }
      `}</style>
    </div>
  )
}

interface CardProps {
  title: string
  description: string
  path: string
  badge?: string
  gradient: string
  tags: string[]
  icon: React.ReactNode
  external?: boolean
  delay: number
}

function Card({ title, description, path, badge, gradient, tags, icon, external, delay }: CardProps) {
  const cardClasses = `
    bg-gradient-to-br ${gradient}
    rounded-xl p-5 shadow-xl
    hover:translate-y-[-4px] hover:shadow-[0_15px_30px_rgba(0,0,0,0.3)]
    transition-all duration-300 cursor-pointer
    relative animate-fade-in flex flex-col
  `

  const content = (
    <>
      <div className="flex justify-between items-start mb-3">
        <span className="bg-white/20 backdrop-blur-sm px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wide">
          {badge || 'Active'}
        </span>
        <span className="text-white/80">{icon}</span>
      </div>

      <h2 className="text-xl font-bold mb-2">{title}</h2>
      <p className="text-white/85 text-sm mb-4 leading-relaxed flex-grow">{description}</p>

      <div className="flex flex-wrap gap-1.5 mb-3">
        {tags.map(tag => (
          <span key={tag} className="text-[10px] bg-white/20 px-2 py-0.5 rounded-full">
            {tag}
          </span>
        ))}
      </div>

      <div className="flex items-center justify-between text-xs">
        <span className="font-semibold">Explore →</span>
        <span className="opacity-75">{external ? 'Static' : 'Daily'}</span>
      </div>
    </>
  )

  if (external) {
    // External links need the base URL prefix for GitHub Pages
    const fullPath = `${import.meta.env.BASE_URL}${path.replace(/^\//, '')}`
    return (
      <a href={fullPath} className={cardClasses} style={{ animationDelay: `${delay}s` }}>
        {content}
      </a>
    )
  }

  return (
    <Link to={path} className={cardClasses} style={{ animationDelay: `${delay}s` }}>
      {content}
    </Link>
  )
}
