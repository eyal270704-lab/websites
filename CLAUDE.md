# Agentic News Hub - Project Documentation

## Overview

An AI-managed news website where a **team of AI agents** automatically generates, monitors, and maintains daily news content. The system uses GitHub Actions for orchestration and Gemini API for content generation.

**Live Site**: https://eyal270704-lab.github.io/websites/

## Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS                           │
│                    (Orchestrator)                           │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   MONITOR     │   │    WRITER     │   │   DESIGNER    │
│    Agent      │   │    Agent      │   │    Agent      │
├───────────────┤   ├───────────────┤   ├───────────────┤
│ Hourly health │   │ Research &    │   │ Generate HTML │
│ checks, auto- │   │ write content │   │ with Tailwind │
│ fix failures  │   │ (future)      │   │ styling       │
│ STATUS: DONE  │   │ STATUS: TODO  │   │ STATUS: BASIC │
└───────────────┘   └───────────────┘   └───────────────┘
```

## Current Status

### Completed
- Monitor Agent (auto-healing system)
- Basic Designer Agent (Gemini generates full HTML pages)
- GitHub Pages deployment
- TradeAnalyzer gem schema & examples

### In Progress
- **Trade Watcher page** - New swing trade analysis page
- React migration (Vite + TypeScript)
- Moving prompts to version-controlled files
- Writer Agent implementation

## File Structure

```
websites/
├── .github/
│   ├── workflows/
│   │   ├── deploy.yml           # Deploy docs/ to GitHub Pages
│   │   ├── nba-news.yml         # Daily NBA news generation (8 AM UTC)
│   │   ├── stock-news.yml       # Stock news 3x daily (7, 12, 16 UTC)
│   │   └── monitor-and-fix.yml  # Hourly health checks & auto-fix
│   └── fix_attempts.json        # Tracks auto-fix attempts
├── config/
│   └── newsfeeds.json           # Feed configurations
├── docs/                        # GitHub Pages root
│   ├── index.html               # Homepage hub
│   ├── basketball-news.html     # NBA news (AI-generated)
│   ├── stock-market-news.html   # Stock news (AI-generated)
│   └── creator-monetization.html # Interactive dashboard
├── scripts/
│   ├── generate_newsfeed.py     # Designer Agent - generates HTML
│   ├── diagnose_workflow_failure.py  # Monitor Agent - diagnostics
│   ├── autofix_workflow.py      # Monitor Agent - auto-fixes
│   ├── inject_secrets.py        # Deploy-time secret injection
│   └── list_gemini_models.py    # Utility: list available models
├── agents/
│   └── examples/
│       └── trade-analyzer/      # TradeAnalyzer output examples
│           ├── example-1-perfect.json
│           ├── example-2-momentum.json
│           ├── example-3-breakout.json
│           ├── example-4-risky.json
│           ├── example-5-avoid.json
│           └── example-6-multiple.json
├── CLAUDE.md                    # This file
├── README.md                    # Public readme
└── SETUP.md                     # Setup instructions
```

## Workflow Schedules

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| `nba-news.yml` | Daily 8 AM UTC | Generate NBA news page |
| `stock-news.yml` | 7, 12, 16 UTC | Generate stock market news |
| `monitor-and-fix.yml` | Hourly | Health checks, auto-fix |
| `deploy.yml` | On push to main | Deploy to GitHub Pages |

## GitHub Secrets Required

| Secret | Purpose |
|--------|---------|
| `GEMINI_API_KEY` | Google Gemini API access |
| `PAT_TOKEN` | GitHub PAT for push access |
| `NBA_PROMPT` | Prompt for NBA news generation |
| `STOCK_PROMPT` | Prompt for stock news generation |
| `TRADE_PROMPT` | (Future) Prompt for TradeAnalyzer - currently in Gemini gem |

## Gemini Gems

| Gem Name | Purpose | Output |
|----------|---------|--------|
| TradeAnalyzer | Swing trade analysis using "Micha Stocks" method | JSON array of trade setups |

## Key Scripts

### generate_newsfeed.py
Main content generation script. Uses Gemini API with Google Search grounding.
```bash
python scripts/generate_newsfeed.py --feed nba   # Generate NBA news
python scripts/generate_newsfeed.py --feed stocks # Generate stock news
```

### diagnose_workflow_failure.py
Analyzes workflow failures and categorizes them.
```bash
python scripts/diagnose_workflow_failure.py           # Human-readable
python scripts/diagnose_workflow_failure.py --json    # JSON output
```

### autofix_workflow.py
Applies automated fixes for common failures.
```bash
python scripts/autofix_workflow.py --workflow nba-news.yml --failure-type empty_response
python scripts/autofix_workflow.py --dry-run ...      # Test without applying
```

## Newsfeed Configuration

Located in `config/newsfeeds.json`:
```json
{
  "nba": {
    "output_file": "basketball-news.html",
    "prompt_secret": "NBA_PROMPT",
    "title": "Basketball News",
    "description": "Daily NBA updates with Israeli players spotlight"
  },
  "stocks": {
    "output_file": "stock-market-news.html",
    "prompt_secret": "STOCK_PROMPT",
    "title": "Stock Market News"
  }
}
```

## Monitor Agent Details

**Timing Configuration** (in autofix_workflow.py):
- Cooldown: 60 minutes between fix attempts
- Max attempts: 3 per hour per workflow
- API quota wait: 120 minutes

**Failure Types Detected**:
- `permission_denied` - PAT_TOKEN issues (creates Issue)
- `api_quota` - Gemini rate limits (waits and retries)
- `empty_response` - Transient API error (retries)
- `missing_secret` - Missing prompt secret (creates Issue)
- `encoding_error` - UTF-8 issues (retries)
- `git_conflict` - Push conflicts (retries with rebase)
- `unknown` - Requires human review (creates Issue)

## Development

### Local Testing
```bash
# Set environment variables
export GEMINI_API_KEY="your-key"
export NBA_PROMPT="your-prompt"

# Generate news locally
python scripts/generate_newsfeed.py --feed nba

# Run diagnostics
python scripts/diagnose_workflow_failure.py
```

### Trigger Workflows Manually
```bash
gh workflow run nba-news.yml
gh workflow run stock-news.yml
gh workflow run monitor-and-fix.yml
```

### Check Workflow Status
```bash
gh run list --workflow=nba-news.yml --limit 5
gh run view <run-id> --log
```

---

## Trade Watcher Page (NEW)

A new page for swing trade analysis using the "Micha Stocks" method.

### Architecture
```
User provides tickers → TradeAnalyzer gem analyzes → Returns JSON → React renders TradeCards
```

### TradeAnalyzer Gem (Gemini)

**Purpose**: Analyze stock tickers for swing trade setups

**Analysis Method ("Micha Stocks")**:
- Golden Zone: 0.5 - 0.618 Fibonacci retracement levels
- Moving Averages: Price above 150MA or testing 20MA
- Volume: Rising RVOL on bounce
- Catalysts: Flag earnings within 5 days as high risk

**Output**: JSON array (NOT HTML) matching the TradeCard component schema

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

### Risk Score Guidelines
- 1-3: Low risk (Golden Zone, above 150MA, no earnings)
- 4-6: Medium risk (missing one criteria)
- 7-10: High risk (earnings within 5 days, extended, weak structure)

### Example Files Location
`agents/examples/trade-analyzer/` contains 6 example JSON outputs for:
1. Perfect setup
2. Momentum play
3. Breakout retest
4. Risky (earnings)
5. Avoid (no setup)
6. Multiple tickers

### React Component Structure
The Trade Watcher page uses these components:
- `Header` - Page title and strategy tag
- `TradeCard` - Individual trade setup card with:
  - Ticker/name/sector header
  - Data grid (entry, stop, structure, trend)
  - Analysis text
  - Footer with RiskMeter and footerTag
- `RiskMeter` - Color-coded risk score (green/gold/red)
- `Footer` - Generation timestamp

### Data Flow (After React Migration)
1. Gemini outputs JSON to `public/data/trades.json`
2. React app fetches and renders TradeCards
3. New analyses append to existing data file

---

## Roadmap

### Phase 2A: React Migration
- [ ] Initialize Vite + React + TypeScript
- [ ] Migrate HTML pages to React components
- [ ] Update Python to output JSON instead of HTML
- [ ] Update deploy workflow for npm build

### Phase 2B: Agent System
- [ ] Create `agents/prompts/` directory for version-controlled prompts
- [ ] Implement Writer Agent (content research)
- [ ] Enhance Designer Agent (layout decisions)
- [ ] Topic proposal system via GitHub Issues

### Phase 2C: Polish
- [ ] Add testing infrastructure
- [ ] Performance optimization
- [ ] Agent coordination improvements

## Decisions Made

1. **New topics**: Writer agent proposes via GitHub Issue, user approves
2. **Prompts**: Moving from secrets to version-controlled `agents/prompts/*.md`
3. **Agent coordination**: Sequential (Writer -> Designer -> Deploy)
4. **Framework**: Vite + React + TypeScript + Tailwind

## Common Issues & Fixes

### Workflow fails with 403 error
- PAT_TOKEN needs `contents: write` permission
- Regenerate PAT and update secret: `gh secret set PAT_TOKEN`

### Race condition on concurrent pushes
- Workflows include `git pull --rebase` before push
- Already fixed in nba-news.yml and stock-news.yml

### Empty Gemini response
- Usually transient, monitor auto-retries after 10 min
- Check Gemini API status if persistent

## Notes for Claude

- Monitor Agent is COMPLETE - don't recreate
- Prompts are currently in GitHub Secrets (moving to files)
- All timing intervals are 2x the original plan
- Never modify or check GEMINI_API_KEY in diagnostics
- **Trade Watcher**: Schema and examples are DONE, gem prompt is refined
- TradeAnalyzer gem outputs JSON (not HTML) - see schema above
- Example files in `agents/examples/trade-analyzer/`
- Next: Build React components, create workflow, integrate with gem
