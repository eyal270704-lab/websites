#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ticker Scout — two-stage pipeline for extracting trade ideas from YouTube.

Stage 1: Extract ticker mentions locally from transcript (no AI cost)
         Uses youtube-transcript-api (same library as the local youtube-transcript skill)
         Skill reference: C:/Users/eyal2/.claude/skills/youtube-transcript/skill.md

Stage 2: Gemini selects top N tickers from condensed mentions (not full transcript)
         Sends only {ticker: [context snippets]} — keeps token usage tiny (~1-2 KB)

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

# Common stock name → ticker mapping for implicit mentions
NAME_TO_TICKER = {
    'nvidia': 'NVDA', 'nvdia': 'NVDA',
    'apple': 'AAPL',
    'tesla': 'TSLA',
    'microsoft': 'MSFT',
    'amazon': 'AMZN',
    'meta': 'META', 'facebook': 'META',
    'google': 'GOOGL', 'alphabet': 'GOOGL',
    'applovin': 'APP',
    'palantir': 'PLTR',
    'coinbase': 'COIN',
    'robinhood': 'HOOD',
    'riot': 'RIOT',
    'mara': 'MARA', 'marathon digital': 'MARA',
    'iris energy': 'IREN', 'iren': 'IREN',
    'kratos': 'KTOS',
    'reddit': 'RDDT',
    'arm': 'ARM',
    'broadcom': 'AVGO',
    'amd': 'AMD', 'advanced micro': 'AMD',
    'intel': 'INTC',
    'qualcomm': 'QCOM',
    'netflix': 'NFLX',
    'spotify': 'SPOT',
    'uber': 'UBER',
    'airbnb': 'ABNB',
    'snowflake': 'SNOW',
    'datadog': 'DDOG',
    'cloudflare': 'NET',
    'rcat': 'RCAT',
    'oilk': 'OILK',
}


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


def fetch_transcript(video_id):
    """Fetch plain text transcript using youtube-transcript-api."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US'])
        return ' '.join(entry['text'] for entry in transcript_list)
    except ImportError:
        log("Error: youtube-transcript-api not installed. Run: pip install youtube-transcript-api")
        sys.exit(1)
    except Exception as e:
        log(f"Error fetching transcript: {e}")
        sys.exit(1)


def extract_ticker_mentions(transcript):
    """
    Stage 1: Scan transcript for ticker mentions and collect surrounding context.

    Returns dict: { "TICKER": ["context snippet 1", "context snippet 2", ...] }
    """
    # Split into sentences for context windowing
    sentences = re.split(r'(?<=[.!?])\s+', transcript)

    mentions = {}

    for i, sentence in enumerate(sentences):
        found_tickers = set()

        # Explicit: $TICKER patterns
        explicit = re.findall(r'\$([A-Z]{2,5})', sentence)
        found_tickers.update(explicit)

        # Explicit: standalone all-caps 2-5 letter words (likely tickers)
        caps_words = re.findall(r'\b([A-Z]{2,5})\b', sentence)
        # Filter to only likely tickers (exclude common English words)
        COMMON_WORDS = {'I', 'A', 'AN', 'THE', 'IN', 'ON', 'AT', 'TO', 'OR', 'AND',
                        'BUT', 'SO', 'IF', 'AS', 'IS', 'IT', 'BE', 'WE', 'DO', 'GO',
                        'NO', 'UP', 'MY', 'US', 'OK', 'PM', 'AM', 'CEO', 'IPO', 'AI',
                        'ETF', 'SEC', 'FED', 'GDP', 'CPI', 'EPS', 'ATH', 'MA', 'RSI',
                        'MACD', 'RVOL', 'SMA', 'EMA', 'PE', 'NYSE', 'NASDAQ'}
        found_tickers.update(t for t in caps_words if t not in COMMON_WORDS and len(t) >= 2)

        # Implicit: company name mentions
        sentence_lower = sentence.lower()
        for name, ticker in NAME_TO_TICKER.items():
            if name in sentence_lower:
                found_tickers.add(ticker)

        # Collect context: current sentence + one before + one after
        context_start = max(0, i - 1)
        context_end = min(len(sentences), i + 2)
        context = ' '.join(sentences[context_start:context_end]).strip()

        # Cap context at 200 chars to keep token usage small
        if len(context) > 200:
            context = context[:197] + '...'

        for ticker in found_tickers:
            if ticker not in mentions:
                mentions[ticker] = []
            # Avoid duplicate context
            if context not in mentions[ticker]:
                mentions[ticker].append(context)

    # Keep max 5 snippets per ticker (most representative)
    return {t: snips[:5] for t, snips in mentions.items() if snips}


def select_tickers_with_gemini(mentions, api_key, count, quiet=False):
    """
    Stage 2: Send condensed mentions to Gemini for ticker selection.
    Input is tiny (~1-2 KB), not the full transcript.
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
    prompt = prompt.replace('{{TICKER_MENTIONS}}', json.dumps(mentions, indent=2))
    prompt = prompt.replace('{{COUNT}}', str(count))

    if not quiet:
        log(f"Sending {len(mentions)} ticker mentions to Gemini for selection...")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=prompt,
        config=types.GenerateContentConfig(),
    )

    if not response or not response.text:
        log("Error: Gemini returned empty response")
        sys.exit(1)

    content = response.text.strip()

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

    # Extract video ID
    video_id = extract_video_id(args.url)
    if not video_id:
        log(f"Error: Could not extract video ID from: {args.url}")
        sys.exit(1)

    log(f"Video ID: {video_id}")

    # Stage 1: Fetch transcript and extract mentions locally
    log("Fetching transcript...")
    transcript = fetch_transcript(video_id)
    log(f"Transcript: {len(transcript.split())} words")

    log("Extracting ticker mentions...")
    mentions = extract_ticker_mentions(transcript)
    log(f"Found {len(mentions)} unique tickers mentioned: {', '.join(sorted(mentions.keys()))}")

    if not mentions:
        log("No ticker mentions found in transcript")
        sys.exit(1)

    # Stage 2: Gemini selects top N
    tickers = select_tickers_with_gemini(mentions, api_key, args.count, args.quiet)
    log(f"\nTop {args.count} picks: {', '.join(tickers)}")

    if args.no_trades:
        print(json.dumps(tickers))
        return

    # Chain to TradeAnalyzer
    run_trade_analyzer(tickers, args.source, args.quiet)

    log(f"\nTicker Scout complete. {len(tickers)} tickers analyzed and appended to trades.json")


if __name__ == '__main__':
    main()
