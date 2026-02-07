import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import TradeWatcher from './pages/TradeWatcher'
import NewsFeed from './components/feed/NewsFeed'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/trade-watcher" element={<TradeWatcher />} />
      <Route
        path="/basketball-news"
        element={
          <NewsFeed
            feedId="nba"
            dataFile="nba.json"
            theme={{ gradient: 'from-orange-500 to-red-500' }}
          />
        }
      />
      <Route
        path="/stock-market-news"
        element={
          <NewsFeed
            feedId="stocks"
            dataFile="stocks.json"
            theme={{ gradient: 'from-blue-500 to-indigo-600' }}
          />
        }
      />
      <Route
        path="/creator-monetization"
        element={
          <NewsFeed
            feedId="creator"
            dataFile="creator.json"
            theme={{ gradient: 'from-teal-500 to-emerald-600' }}
          />
        }
      />
    </Routes>
  )
}

export default App
