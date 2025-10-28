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
- During deployment, GitHub Actions replaces `PLACEHOLDER_API_KEY` with your actual key
- The deployed site will have the working API key
- The source code remains secure

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
