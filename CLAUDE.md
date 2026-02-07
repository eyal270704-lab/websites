# Agentic News Hub - Project Documentation

## Overview

An AI-managed news website where a **team of AI agents** automatically generates, monitors, and maintains daily news content. Built with **React 19 + TypeScript + Vite**, orchestrated via GitHub Actions, with content generation powered by Gemini API.

**Live Site**: https://eyal270704-lab.github.io/websites/

## Current Status (February 2026)

### Completed
- **React Migration** - Full Vite + React 19 + TypeScript frontend
- **Trade Watcher Page** - Swing trade analysis with TradeCard components
- **JSON-Based Feed System** - Extensible news feeds (NBA, Stocks)
- **Monitor Agent** - Auto-healing workflow system (detects all content workflows)
- **Version-Controlled Prompts** - Prompts in `agents/prompts/*.md`
- **Themed Pages** - Each feed has unique visual identity (accent colors, backgrounds)

### In Progress
- **Ticker Scout Agent** - Will listen to Micha Stocks YouTube livestreams and update watchlist

## Agent Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       GITHUB ACTIONS                             │
│                       (Orchestrator)                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
     ┌───────────────────────┼───────────────────────┐
     │                       │                       │
     ▼                       ▼                       ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  MONITOR    │      │   TRADE     │      │  NEWSFEED   │
│   Agent     │      │  ANALYZER   │      │   Agent     │
├─────────────┤      ├─────────────┤      ├─────────────┤
│ Hourly      │      │ Daily swing │      │ NBA/Stocks  │
│ health      │      │ trade       │      │ daily news  │
│ checks      │      │ analysis    │      │ generation  │
│ STATUS:DONE │      │ STATUS:DONE │      │ STATUS:DONE │
└─────────────┘      └─────────────┘      └─────────────┘
                             │
                     ┌───────┴───────┐
                     ▼               ▼
              ┌─────────────┐  ┌─────────────┐
              │   TICKER    │  │ Watchlist   │
              │   SCOUT     │  │ (Manual)    │
              │   (Future)  │  │ STATUS:DONE │
              └─────────────┘  └─────────────┘
```

## File Structure

```
websites/
├── .github/
│   ├── workflows/
│   │   ├── deploy.yml              # Build React + deploy to GitHub Pages
│   │   ├── trade-watcher.yml       # Daily trade analysis (6 AM UTC weekdays)
│   │   ├── nba-news.yml            # Daily NBA news
│   │   ├── stock-news.yml          # Stock market news
│   │   └── monitor-and-fix.yml     # Hourly health checks & auto-fix
│   └── fix_attempts.json           # Tracks auto-fix attempts
├── agents/
│   ├── prompts/
│   │   ├── trade-analyzer.md       # TradeAnalyzer prompt (accepts {{TICKERS}})
│   │   ├── nba.md                  # NBA news prompt
│   │   └── stocks.md               # Stock market prompt
│   └── examples/
│       └── trade-analyzer/         # Example JSON outputs
├── config/
│   ├── newsfeeds.json              # Feed configurations
│   └── watchlist.json              # Ticker watchlist for TradeAnalyzer
├── public/
│   ├── data/                       # AI-generated JSON data
│   │   ├── trades.json
│   │   ├── nba.json
│   │   └── stocks.json
│   ├── creator-monetization.html   # Static page (not in React)
│   └── 404.html                    # SPA redirect for GitHub Pages
├── src/
│   ├── components/
│   │   ├── feed/
│   │   │   └── NewsFeed.tsx        # Generic feed renderer
│   │   └── trade/
│   │       ├── TradeCard.tsx       # Trade setup card
│   │       └── RiskMeter.tsx       # Risk score visualization
│   ├── pages/
│   │   ├── Home.tsx                # Homepage with card grid
│   │   └── TradeWatcher.tsx        # Trade analysis page
│   ├── types/
│   │   ├── feed.ts                 # NewsFeed TypeScript types
│   │   └── trade.ts                # TradeSetup TypeScript types
│   ├── App.tsx                     # Routes configuration
│   ├── main.tsx                    # Entry point with SPA redirect handling
│   └── index.css                   # Tailwind styles
├── scripts/
│   ├── generate_trades.py          # TradeAnalyzer - generates trades.json
│   ├── generate_newsfeed.py        # Newsfeed generator - generates feed JSON
│   ├── diagnose_workflow_failure.py  # Monitor Agent - diagnostics
│   └── autofix_workflow.py         # Monitor Agent - auto-fixes
├── index.html                      # Vite entry
├── vite.config.ts                  # Vite config with base path
├── tailwind.config.js              # Tailwind with custom colors
├── package.json                    # Node dependencies
└── CLAUDE.md                       # This file
```

## Workflow Schedules

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| `trade-watcher.yml` | Weekdays 6 AM UTC | Analyze watchlist tickers |
| `nba-news.yml` | Daily 8 AM UTC | Generate NBA news |
| `stock-news.yml` | 7, 12, 16 UTC | Generate stock market news |
| `monitor-and-fix.yml` | Hourly | Health checks, auto-fix |
| `deploy.yml` | On push to main | Build React, deploy to GitHub Pages |

## GitHub Secrets Required

| Secret | Purpose |
|--------|---------|
| `GEMINI_API_KEY` | Google Gemini API access |
| `PAT_TOKEN` | GitHub PAT for push access |

**Note**: Prompts are now version-controlled in `agents/prompts/*.md`, not in secrets.

## Key Scripts

### generate_trades.py
Trade analysis script. Uses Gemini API with Google Search grounding.
```bash
python scripts/generate_trades.py                    # Uses config/watchlist.json
python scripts/generate_trades.py --tickers AAPL,MSFT,TSLA  # Override tickers
python scripts/generate_trades.py --quiet            # JSON only output
```

### generate_newsfeed.py
News generation script.
```bash
python scripts/generate_newsfeed.py --feed nba      # Generate NBA news
python scripts/generate_newsfeed.py --feed stocks   # Generate stock news
```

### diagnose_workflow_failure.py
Analyzes workflow failures. Detects all content generation workflows automatically.
```bash
python scripts/diagnose_workflow_failure.py           # Human-readable
python scripts/diagnose_workflow_failure.py --json    # JSON output
```

## Trade Watcher System

### Architecture
```
config/watchlist.json → generate_trades.py → Gemini API → public/data/trades.json → React TradeCards
```

### Watchlist Configuration
Located in `config/watchlist.json`:
```json
{
  "description": "Ticker watchlist for TradeAnalyzer. Will be updated by Ticker Scout agent.",
  "tickers": ["AAPL", "MSFT", "NVDA", "TSLA", "META", "GOOGL", "AMZN", "JPM", "V", "AMD"]
}
```

### TradeAnalyzer Prompt
Located in `agents/prompts/trade-analyzer.md`. Uses `{{TICKERS}}` placeholder.

**Analysis Method ("Micha Stocks")**:
- Golden Zone: 0.5 - 0.618 Fibonacci retracement levels
- Moving Averages: Price above 150MA or testing 20MA
- Volume: Rising RVOL on bounce
- Catalysts: Flag earnings within 5 days as high risk

### Trade Setup JSON Schema
```json
{
  "ticker": "$TSLA",
  "name": "Tesla Inc.",
  "sector": "Consumer Cyclical",
  "entry": "$182.50",
  "stop": "$175.00",
  "structure": "0.618 Fib",
  "trend": "> 150MA",
  "trendLabel": "Trend",
  "analysis": "2-3 sentence technical thesis",
  "riskScore": 3,
  "footerTag": "High Confidence",
  "setupType": "perfect"
}
```

### Setup Types
- `perfect` - Golden Zone + above 150MA + no catalyst risk
- `momentum` - 20MA bounce + high RVOL
- `breakout` - Support/resistance test + volume confirmation
- `risky` - Valid setup but earnings nearby
- `avoid` - No valid technical setup

### Risk Score
- 1-3: Low risk (green)
- 4-6: Medium risk (gold)
- 7-10: High risk (red)

## NewsFeed System

### How to Add a New Feed
1. Add prompt file: `agents/prompts/{feed-name}.md`
2. Add config in `config/newsfeeds.json`
3. Create workflow in `.github/workflows/{feed-name}.yml`
4. Add route in `src/App.tsx` with NewsFeed component

### Feed Configuration Example
```json
{
  "nba": {
    "id": "nba",
    "promptFile": "agents/prompts/nba.md",
    "dataFile": "nba.json",
    "title": "NBA Daily News"
  }
}
```

### Theme System
Each feed can have custom theming:
```tsx
<NewsFeed
  feedId="nba"
  dataFile="nba.json"
  theme={{
    gradient: 'from-orange-500 to-red-500',
    bgGradient: 'from-slate-800 via-orange-900/50 to-slate-800',
    accentColor: 'orange'
  }}
/>
```

### Card Types
- `breaking` - Featured breaking news
- `game` - Sports game scores
- `stock` - Stock ticker cards
- `article` - News articles
- `stat` - Statistics cards
- `quote` - Quote cards
- `alert` - Alert/info cards

## Monitor Agent

**Timing Configuration**:
- Cooldown: 60 minutes between fix attempts
- Max attempts: 3 per hour per workflow
- API quota wait: 120 minutes

**Detects Workflows Using**:
- `generate_newsfeed.py`
- `generate_trades.py`

**Failure Types**:
- `permission_denied` - PAT_TOKEN issues (creates Issue)
- `api_quota` - Gemini rate limits (waits and retries)
- `empty_response` - Transient API error (retries)
- `git_conflict` - Push conflicts (retries with rebase)
- `unknown` - Requires human review (creates Issue)

## Development

### Local Development
```bash
npm install
npm run dev                # Start Vite dev server at localhost:5173
```

### Build for Production
```bash
npm run build              # Outputs to dist/
```

### Trigger Workflows Manually
```bash
gh workflow run trade-watcher.yml
gh workflow run trade-watcher.yml -f tickers=AAPL,MSFT  # Custom tickers
gh workflow run nba-news.yml
gh workflow run stock-news.yml
```

### Check Workflow Status
```bash
gh run list --limit 5
gh run view <run-id> --log
```

## Future: Ticker Scout Agent

**Purpose**: Automatically update watchlist based on Micha Stocks YouTube livestreams

**Planned Behavior**:
1. Listen to/analyze Micha Stocks livestream transcripts
2. Identify 2 most promising tickers mentioned
3. Update `config/watchlist.json`
4. Commit changes for next TradeAnalyzer run

**Status**: Planned

## Common Issues & Fixes

### Workflow fails with 403 error
- PAT_TOKEN needs `contents: write` permission
- Regenerate PAT and update: `gh secret set PAT_TOKEN`

### Race condition on concurrent pushes
- Workflows include `git pull --rebase` before push
- Already handled in all workflows

### Empty Gemini response
- Usually transient, monitor auto-retries
- Check Gemini API status if persistent

### SPA Routing on GitHub Pages
- Uses 404.html redirect trick
- Query param `?p=` carries path through redirect
- Handled in `main.tsx`

## Design Decisions

1. **Creator Monetization**: Kept as static HTML (not daily-updated React)
2. **Prompts**: Version-controlled in `agents/prompts/*.md`
3. **Ticker Input**: Watchlist-based with manual override option
4. **Theme System**: Per-feed accent colors for visual identity
5. **Data Flow**: Agents output JSON, React renders it

---

## Notes for Claude

- Monitor Agent is COMPLETE - detects both newsfeed and trade workflows
- React migration is COMPLETE - all pages working
- TradeAnalyzer uses `{{TICKERS}}` placeholder - replaced by script
- Watchlist in `config/watchlist.json` - user updates manually for now
- Future: Ticker Scout agent will update watchlist from YouTube
- All timing intervals are 2x the original plan
- Never modify or check GEMINI_API_KEY in diagnostics
