import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

// Handle GitHub Pages SPA redirect
const params = new URLSearchParams(window.location.search)
const redirectPath = params.get('p')
if (redirectPath) {
  // Remove the query param and redirect to the actual path
  const newUrl = window.location.origin + '/websites' + redirectPath + window.location.hash
  window.history.replaceState(null, '', newUrl)
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter basename="/websites">
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
