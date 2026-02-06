import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import TradeWatcher from './pages/TradeWatcher'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/trade-watcher" element={<TradeWatcher />} />
    </Routes>
  )
}

export default App
