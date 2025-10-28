# Setup Instructions

## Adding the Gemini API Key

This repository uses GitHub Actions to securely inject your Gemini API key during deployment. Follow these steps:

### Step 1: Add the Secret to GitHub

1. Go to your repository: `https://github.com/eyal270704-lab/websites`
2. Click on **Settings** (top navigation)
3. In the left sidebar, expand **Secrets and variables** → Click **Actions**
4. Click **New repository secret**
5. Enter:
   - **Name**: `GEMINI_API_KEY`
   - **Secret**: `your secret api key`
6. Click **Add secret**

### Step 2: Configure GitHub Pages

1. In your repository, go to **Settings** → **Pages**
2. Under "Build and deployment":
   - **Source**: Select "GitHub Actions"
3. Save the settings

### Step 3: Trigger Deployment

The workflow will automatically run when you push to the main branch. You can also trigger it manually:

1. Go to **Actions** tab
2. Click on "Deploy to GitHub Pages"
3. Click **Run workflow** → **Run workflow**

### How It Works

- Your API key is stored securely in GitHub Secrets (never visible in code)
- During deployment, a Python script (`scripts/inject_secrets.py`) runs automatically
- The script replaces `PLACEHOLDER_API_KEY` with your actual key in the HTML files
- The deployed site will have the working API key
- The source code remains secure

**Technical Details:**
- Uses a clean Python script instead of `sed` for better maintainability
- Easy to extend for multiple pages with different API keys
- Includes error handling and validation
- See [scripts/inject_secrets.py](scripts/inject_secrets.py) for implementation

### Security Notes

- The API key will be visible in the deployed HTML (client-side requirement)
- **IMPORTANT**: Restrict your API key in Google AI Studio:
  1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
  2. Select your API key
  3. Add application restriction (HTTP referrer): `https://eyal270704-lab.github.io/websites/*`
  4. This prevents misuse of your key on other domains

### Your Site URL

Once deployed, your site will be available at:
`https://eyal270704-lab.github.io/websites/`

---

## Automated Newsfeed Generation

This repository includes automated newsfeed generation for various daily news pages (NBA, stocks, etc.).

### How It Works

1. **Config-Driven System**: All newsfeeds are defined in `config/newsfeeds.json`
2. **Universal Generator**: One script (`scripts/generate_newsfeed.py`) handles all feeds
3. **Scheduled Workflows**: Each feed has its own workflow with custom schedule
4. **Gemini AI**: Uses Google's Gemini API (free tier) to generate content

### Adding a Newsfeed Prompt Secret

For each newsfeed (e.g., NBA news), you need to add a prompt secret:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Enter:
   - **Name**: `NBA_PROMPT` (or `STOCK_PROMPT`, etc.)
   - **Secret**: Your complete prompt for that newsfeed
4. Click **Add secret**

### Current Newsfeeds

**NBA News** (`basketball-news.html`)
- Schedule: Daily at 10 AM Israel time (8 AM UTC)
- Secret needed: `NBA_PROMPT`
- Workflow: `.github/workflows/nba-news.yml`
- Manual trigger: Actions → "Generate NBA News" → "Run workflow"

**Stock Market News** (`stock-market-news.html`)
- Schedule: 3x daily (9 AM, 2 PM, 6 PM Israel time)
- Secret needed: `STOCK_PROMPT`
- Workflow: `.github/workflows/stock-news.yml`
- Status: Disabled until `STOCK_PROMPT` is added

### Adding a New Newsfeed

1. **Add to config** (`config/newsfeeds.json`):
```json
"tech": {
  "output_file": "tech-news.html",
  "prompt_secret": "TECH_PROMPT",
  "card_id": "tech",
  "title": "Tech News",
  "card_class": "tech",
  "overrun_files": true
}
```

2. **Create workflow** (e.g., `.github/workflows/tech-news.yml`):
```yaml
name: Generate Tech News
on:
  schedule:
    - cron: '0 9 * * *'  # Your desired schedule
env:
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  TECH_PROMPT: ${{ secrets.TECH_PROMPT }}
run: python scripts/generate_newsfeed.py --feed tech
```

3. **Add secret**: `TECH_PROMPT` to GitHub Secrets
4. **Update lobby**: Add card to `docs/index.html` (will auto-activate on first run)

### Prompt Format Guidelines

Your prompts should:
- Focus on **content and data requirements** (what to research/include)
- **NOT** include file-saving or download instructions
- Let the script handle HTML structure and styling
- The generator will automatically:
  - Wrap content in site template (header, footer, navigation)
  - Apply Tailwind CSS styling
  - Match your site's design theme
  - Handle the "Back to Hub" link

### Testing Newsfeeds

1. Add your prompt secret to GitHub
2. Go to **Actions** tab
3. Select the newsfeed workflow (e.g., "Generate NBA News")
4. Click **Run workflow** → **Run workflow**
5. Wait ~1 minute for completion
6. Check the deployed site

### Secrets Summary

Required secrets for full functionality:
- `GEMINI_API_KEY` - ✅ For static pages (Creator Monetization) and newsfeeds
- `NBA_PROMPT` - For NBA news generation
- `STOCK_PROMPT` - For stock market news generation
- Additional prompts as you add more newsfeeds
