#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ticker Scout — extract trade ideas from YouTube via Gemini with Google Search grounding.

Single-stage pipeline: Gemini watches the YouTube video (via grounding) and picks
the top N tickers for swing trading. No transcript fetching needed — Gemini accesses
the video content directly through Google Search, bypassing YouTube cloud IP blocks.

Then chains to generate_trades.py --tickers <list> --source "Micha Stocks YouTube" --append

Usage:
    python scripts/ticker-scout.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
    python scripts/ticker-scout.py --url "VIDEO_ID" --count 3
    python scripts/ticker-scout.py --url "VIDEO_ID" --count 5 --no-trades
"""

import os
import sys
import io
import re
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def log(message):
    print(message, file=sys.stderr)


def extract_video_id(url):
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:v=|youtu\.be/|embed/|shorts/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def select_tickers_with_gemini(video_url, api_key, count, quiet=False):
    """
    Single-stage: Gemini uses Google Search grounding to access the YouTube video
    and select the top N tickers for swing trading.
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        log("Error: google-genai not installed. Run: pip install google-genai")
        sys.exit(1)

    # Load prompt
    prompt_path = Path(__file__).parent.parent / 'agents' / 'prompts' / 'ticker-scout.md'
    if not prompt_path.exists():
        log(f"Error: Prompt not found: {prompt_path}")
        sys.exit(1)

    prompt = prompt_path.read_text(encoding='utf-8')
    prompt = prompt.replace('{{YOUTUBE_URL}}', video_url)
    prompt = prompt.replace('{{COUNT}}', str(count))

    if not quiet:
        log(f"Sending YouTube URL to Gemini with Google Search grounding...")
        log(f"Video: {video_url}")

    client = genai.Client(api_key=api_key)

    # Use Google Search grounding so Gemini can access YouTube content
    grounding_tool = types.Tool(
        google_search=types.GoogleSearch()
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[grounding_tool],
            ),
        )
    except Exception as e:
        error_msg = str(e)
        if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
            log("Error: Gemini API quota exhausted. Retry later.")
        else:
            log(f"Error calling Gemini API: {e}")
        sys.exit(1)

    if not response or not response.text:
        log("Error: Gemini returned empty response")
        sys.exit(1)

    content = response.text.strip()

    if not quiet:
        log(f"Gemini response: {content[:200]}")

    # Extract JSON array
    json_match = re.search(r'\[[\s\S]*?\]', content)
    if not json_match:
        log(f"Error: No JSON array in Gemini response: {content[:300]}")
        sys.exit(1)

    tickers = json.loads(json_match.group(0))
    return [t.strip().upper().lstrip('$') for t in tickers]


def run_trade_analyzer(tickers, source, quiet=False):
    """Call generate_trades.py with extracted tickers and --append."""
    script = Path(__file__).parent / 'generate_trades.py'
    cmd = [
        sys.executable, str(script),
        '--tickers', ','.join(tickers),
        '--source', source,
        '--append',
    ]
    if quiet:
        cmd.append('--quiet')

    log(f"\nRunning TradeAnalyzer for: {', '.join(tickers)}")
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        log("Error: generate_trades.py failed")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Extract tickers from YouTube and trigger TradeAnalyzer')
    parser.add_argument('--url', '-u', required=True, help='YouTube video URL or video ID')
    parser.add_argument('--count', '-c', type=int, default=3, help='Number of tickers to select (default: 3)')
    parser.add_argument('--source', default='Micha Stocks YouTube', help='Source label for trade cards')
    parser.add_argument('--no-trades', action='store_true', help='Skip running TradeAnalyzer (just print tickers)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress progress messages')
    args = parser.parse_args()

    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        log("Error: GEMINI_API_KEY environment variable not set")
        sys.exit(1)

    # Extract video ID and build canonical URL
    video_id = extract_video_id(args.url)
    if not video_id:
        log(f"Error: Could not extract video ID from: {args.url}")
        sys.exit(1)

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    log(f"Video: {video_url}")

    # Single stage: Gemini + Google Search grounding extracts tickers directly
    log("Asking Gemini to analyze video and select tickers...")
    tickers = select_tickers_with_gemini(video_url, api_key, args.count, args.quiet)
    log(f"\nTop {args.count} picks: {', '.join(tickers)}")

    if args.no_trades:
        print(json.dumps(tickers))
        return

    # Chain to TradeAnalyzer
    run_trade_analyzer(tickers, args.source, args.quiet)

    log(f"\nTicker Scout complete. {len(tickers)} tickers analyzed and appended to trades.json")


if __name__ == '__main__':
    main()
