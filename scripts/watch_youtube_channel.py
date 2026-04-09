#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Watch YouTube Channel — auto-detects new Micha Stocks videos via Gemini + Google Search.

Uses Gemini API with Google Search grounding to find the latest video (bypasses
YouTube's cloud IP blocks on RSS/API). If a new video is found, runs ticker-scout.py.
Stores the last-processed video ID in scripts/.last-video.txt (local-only, gitignored).

Usage:
    python scripts/watch_youtube_channel.py              # Check + run if new video
    python scripts/watch_youtube_channel.py --dry-run    # Check only, don't run scout
    python scripts/watch_youtube_channel.py --force      # Run scout even if no new video
"""

import os
import sys
import io
import re
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load env vars from youtube_watcher.env (sibling of this script)
_env_file = Path(__file__).parent / 'youtube_watcher.env'
if _env_file.exists():
    for _line in _env_file.read_text(encoding='utf-8').splitlines():
        _line = _line.strip()
        if _line and not _line.startswith('#') and '=' in _line:
            _k, _v = _line.split('=', 1)
            os.environ.setdefault(_k.strip(), _v.strip())

CHANNEL_NAME = "Micha Stocks"
CHANNEL_HANDLE = "@Micha.Stocks"
STATE_FILE = Path(__file__).parent / ".last-video.txt"
REPO_ROOT = Path(__file__).parent.parent

DEFAULT_COUNT = 3
DEFAULT_SOURCE = "Micha Stocks YouTube"

def log(msg):
    print(msg, file=sys.stderr)


def fetch_latest_video(api_key):
    """Use Gemini + Google Search grounding to find the latest Micha Stocks video."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        log("Error: google-genai not installed. Run: pip install google-genai")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    grounding_tool = types.Tool(google_search=types.GoogleSearch())

    prompt = (
        f"Find the most recent YouTube video uploaded by the channel {CHANNEL_NAME} "
        f"(handle: {CHANNEL_HANDLE}). This is a Hebrew-language stock market channel.\n\n"
        "Return ONLY a JSON object with these fields:\n"
        '{"video_id": "<11-char YouTube ID>", "title": "<video title>", '
        '"url": "https://www.youtube.com/watch?v=<ID>"}\n\n'
        "No markdown, no backticks, no explanation. Raw JSON only."
    )

    max_retries = 3
    backoff = [10, 20, 30]
    content = None
    is_503 = False
    model = "gemini-2.5-flash"
    for attempt in range(max_retries):
        try:
            if is_503:
                model = 'gemini-2.5-pro'
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(tools=[grounding_tool]),
            )
            
        except Exception as e:
            error_msg = str(e)
            if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
                log("Error: Gemini API quota exhausted. Retry later.")
                sys.exit(1)
            log(f"Attempt {attempt + 1}/{max_retries}: Gemini API error: {e}")
            if attempt < max_retries - 1:
                if '503' in error_msg:
                    log("not your fault: this model is experiencing high demand, switching to another one")
                    is_503 =  True
                log(f"Retrying in {backoff[attempt]}s...")
                time.sleep(backoff[attempt])
                continue
            log("All retries exhausted.")
            sys.exit(1)

        if response and response.text:
            content = response.text.strip()
            break

        # Debug: log what Gemini actually returned
        log(f"Attempt {attempt + 1}/{max_retries}: Gemini returned empty response")
        if response:
            candidates = getattr(response, 'candidates', None)
            if candidates:
                log(f"  candidates[0].finish_reason: {getattr(candidates[0], 'finish_reason', 'N/A')}")
            parts = getattr(response, 'parts', None)
            if parts:
                log(f"  parts: {parts[:200]}")

        if attempt < max_retries - 1:
            log(f"Retrying in {backoff[attempt]}s...")
            time.sleep(backoff[attempt])

    if not content:
        log("Error: Gemini returned empty response after all retries")
        sys.exit(1)
    log(f"Gemini response: {content[:300]}")

    # Extract JSON object from response
    json_match = re.search(r'\{[\s\S]*?\}', content)
    if not json_match:
        log(f"Error: No JSON object in Gemini response: {content[:300]}")
        sys.exit(1)

    try:
        data = json.loads(json_match.group(0))
    except json.JSONDecodeError as e:
        log(f"Error parsing JSON: {e}\nRaw: {json_match.group(0)}")
        sys.exit(1)

    video_id = data.get('video_id', '').strip()
    title = data.get('title', video_id).strip()
    url = data.get('url', f"https://www.youtube.com/watch?v={video_id}").strip()

    if not video_id or len(video_id) != 11:
        # Try extracting video ID from the URL as fallback
        id_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
        if id_match:
            video_id = id_match.group(1)
        else:
            log(f"Error: Invalid video ID '{video_id}' from Gemini response")
            sys.exit(1)

    return video_id, title, url


def read_last_video():
    """Return last-processed video ID, or None if state file doesn't exist."""
    if STATE_FILE.exists():
        content = STATE_FILE.read_text(encoding='utf-8').strip()
        return content if content else None
    return None


def save_last_video(video_id):
    """Persist the processed video ID to state file."""
    STATE_FILE.write_text(video_id + '\n', encoding='utf-8')


def run_scout(url, count, source, quiet=False):
    """Run ticker-scout.py for the given YouTube URL."""
    scout_script = Path(__file__).parent / 'ticker-scout.py'
    cmd = [
        sys.executable, str(scout_script),
        '--url', url,
        '--count', str(count),
        '--source', source,
    ]
    if quiet:
        cmd.append('--quiet')

    log(f"Running Ticker Scout for: {url}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def git_commit_and_push(title):
    """Commit updated trades.json and push."""
    date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    commit_msg = f"📺 Ticker Scout: {title} - {date_str}"

    trades_path = REPO_ROOT / 'public' / 'data' / 'trades.json'
    if not trades_path.exists():
        log("Warning: trades.json not found, skipping git operations")
        return False

    try:
        subprocess.run(['git', 'add', str(trades_path)], cwd=REPO_ROOT, check=True)
        result = subprocess.run(
            ['git', 'diff', '--staged', '--quiet'],
            cwd=REPO_ROOT
        )
        if result.returncode == 0:
            log("No changes to commit (trades.json unchanged)")
            return True

        subprocess.run(['git', 'commit', '-m', commit_msg], cwd=REPO_ROOT, check=True)
        subprocess.run(['git', 'pull', '--rebase'], cwd=REPO_ROOT, check=True)
        subprocess.run(['git', 'push'], cwd=REPO_ROOT, check=True)
        log(f"Committed and pushed: {commit_msg}")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Git error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Watch Micha Stocks YouTube channel for new videos')
    parser.add_argument('--dry-run', action='store_true', help='Check only, do not run scout')
    parser.add_argument('--force', action='store_true', help='Run scout even if no new video')
    parser.add_argument('--count', type=int, default=DEFAULT_COUNT, help=f'Tickers to extract (default: {DEFAULT_COUNT})')
    parser.add_argument('--source', default=DEFAULT_SOURCE, help=f'Source label (default: {DEFAULT_SOURCE})')
    parser.add_argument('--no-git', action='store_true', help='Skip git commit/push (for CI where workflow handles git)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress progress messages')
    args = parser.parse_args()

    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        log("Error: GEMINI_API_KEY environment variable not set")
        log("Set it with: $env:GEMINI_API_KEY='your-key-here'  (PowerShell)")
        log("         or: set GEMINI_API_KEY=your-key-here      (cmd)")
        sys.exit(1)

    log(f"Searching for latest {CHANNEL_NAME} video via Gemini...")
    video_id, title, url = fetch_latest_video(api_key)
    log(f"Latest video: [{video_id}] {title}")
    log(f"URL: {url}")

    if args.dry_run:
        last = read_last_video()
        if last == video_id:
            print(f"No new video (last processed: {video_id})")
        else:
            print(f"New video detected: {video_id}")
            print(f"Title: {title}")
            print(f"URL: {url}")
        return

    last_video_id = read_last_video()

    if last_video_id == video_id and not args.force:
        print(f"No new video since last check (last: {video_id})")
        return

    if args.force and last_video_id == video_id:
        log("--force flag set, running scout on latest video anyway")

    success = run_scout(url, args.count, args.source, args.quiet)

    if success:
        save_last_video(video_id)
        if not args.no_git:
            git_commit_and_push(title)
        print(f"Done. Scout completed for: {title}")
    else:
        log("Scout failed — state not updated")
        sys.exit(1)


if __name__ == '__main__':
    main()
