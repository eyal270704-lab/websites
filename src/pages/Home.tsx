import { Link } from 'react-router-dom'

const pages = [
  {
    title: 'Trade Watcher',
    description: 'AI-powered swing trade analysis using the Golden Zone strategy. Get daily signals based on Fibonacci structures and momentum.',
    path: '/trade-watcher',
    badge: 'NEW',
    gradient: 'from-amber-500 to-orange-600',
    tags: ['Swing Trades', 'Fibonacci', 'AI Analysis'],
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    )
  },
  {
    title: 'Creator Monetization',
    description: 'Compare YouTube, TikTok, and Instagram monetization models. Get AI-powered strategies for your content channel.',
    path: '/creator-monetization.html',
    external: true,
    gradient: 'from-teal-500 to-emerald-600',
    tags: ['YouTube', 'TikTok', 'Instagram', 'AI Strategy'],
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  },
  {
    title: 'Basketball News',
    description: 'Daily updates on NBA games, scores, player stats, and highlights. Stay on top of the basketball world.',
    path: '/basketball-news.html',
    external: true,
    gradient: 'from-orange-500 to-red-500',
    tags: ['NBA', 'Scores', 'Live Updates'],
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  },
  {
    title: 'Stock Market News',
    description: 'Real-time market updates, trending stocks, financial news, and AI-powered market analysis.',
    path: '/stock-market-news.html',
    external: true,
    gradient: 'from-blue-500 to-indigo-600',
    tags: ['Market Trends', 'Stocks', 'Analysis'],
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
      </svg>
    )
  }
]

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="text-center mb-16 pt-8 animate-fade-in">
          <h1 className="text-5xl md:text-7xl font-bold mb-4 bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            Daily News Hub
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto mb-6">
            Your curated collection of data-driven websites, updated daily with fresh insights
          </p>
          <div className="flex justify-center gap-6 text-sm text-gray-400">
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

        {/* Cards Grid */}
        <main>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
            {pages.map((page, index) => (
              <Card key={page.path} {...page} delay={index * 0.1} />
            ))}
          </div>

          {/* Coming Soon Banner */}
          <div className="text-center bg-gradient-to-r from-purple-800 to-indigo-800 rounded-2xl p-12 shadow-2xl animate-fade-in">
            <h3 className="text-3xl font-bold mb-4">More Coming Soon</h3>
            <p className="text-lg text-gray-200 mb-6 max-w-2xl mx-auto">
              We're constantly adding new data-driven websites to keep you informed. Check back regularly for updates!
            </p>
            <div className="flex flex-wrap justify-center gap-3 text-sm">
              <span className="bg-white/10 px-4 py-2 rounded-full">Tech News</span>
              <span className="bg-white/10 px-4 py-2 rounded-full">Weather Updates</span>
              <span className="bg-white/10 px-4 py-2 rounded-full">Crypto Tracker</span>
              <span className="bg-white/10 px-4 py-2 rounded-full">Gaming News</span>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="mt-16 text-center text-gray-400 text-sm">
          <p>&copy; 2026 Daily News Hub. All content updated daily via automated pipelines.</p>
          <p className="mt-2">Built with GitHub Pages & AI-Powered Content</p>
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
    rounded-2xl p-8 shadow-2xl
    hover:translate-y-[-8px] hover:shadow-[0_20px_40px_rgba(0,0,0,0.3)]
    transition-all duration-300 cursor-pointer
    relative animate-fade-in
  `

  const content = (
    <>
      <div className="flex justify-between items-start mb-4">
        {badge ? (
          <span className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide">
            {badge}
          </span>
        ) : (
          <span className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide">
            Active
          </span>
        )}
        <span className="text-white/80">{icon}</span>
      </div>

      <h2 className="text-3xl font-bold mb-3">{title}</h2>
      <p className="text-white/90 mb-6 leading-relaxed">{description}</p>

      <div className="flex flex-wrap gap-2 mb-4">
        {tags.map(tag => (
          <span key={tag} className="text-xs bg-white/20 px-3 py-1 rounded-full">
            {tag}
          </span>
        ))}
      </div>

      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold">Explore Dashboard →</span>
        <span className="text-xs opacity-75">Updated Daily</span>
      </div>
    </>
  )

  if (external) {
    return (
      <a
        href={path}
        className={cardClasses}
        style={{ animationDelay: `${delay}s` }}
      >
        {content}
      </a>
    )
  }

  return (
    <Link
      to={path}
      className={cardClasses}
      style={{ animationDelay: `${delay}s` }}
    >
      {content}
    </Link>
  )
}
