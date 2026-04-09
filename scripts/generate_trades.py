#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trade Watcher data generator for MarketFlow AI.

This script generates JSON trade setups using Google's Gemini API
with the TradeAnalyzer prompt. Output is consumed by the React app.

Usage:
    python scripts/generate_trades.py
    python scripts/generate_trades.py --tickers AAPL,MSFT,TSLA
    python scripts/generate_trades.py --quiet  # JSON only output

Ticker list is loaded from:
1. --tickers argument (comma-separated)
2. config/watchlist.json (default)
"""

import os
import sys
import io
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from google import genai
from google.genai import types

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def log(message, quiet=False):
    """Print message unless in quiet mode."""
    if not quiet:
        print(message, file=sys.stderr)


def load_watchlist():
    """Load ticker watchlist from config file."""
    config_path = Path(__file__).parent.parent / 'config' / 'watchlist.json'

    if not config_path.exists():
        print(f"Warning: Watchlist not found: {config_path}", file=sys.stderr)
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('tickers', [])
    except Exception as e:
        print(f"Error loading watchlist: {e}", file=sys.stderr)
        return None


def load_prompt():
    """Load the TradeAnalyzer prompt from version-controlled file."""
    prompt_path = Path(__file__).parent.parent / 'agents' / 'prompts' / 'trade-analyzer.md'

    if not prompt_path.exists():
        print(f"Error: Prompt file not found: {prompt_path}", file=sys.stderr)
        return None

    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading prompt: {e}", file=sys.stderr)
        return None


def generate_trades_with_gemini(prompt, api_key, quiet=False):
    """
    Generate trade setups using Gemini API with Google Search grounding.

    Args:
        prompt: The TradeAnalyzer prompt
        api_key: Google Gemini API key
        quiet: Suppress progress messages

    Returns:
        list: Array of trade setup objects, or None if failed
    """
    try:
        client = genai.Client(api_key=api_key)

        # Set up Google Search tool for real-time market data
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )

        log("Calling Gemini API with Google Search grounding...", quiet)

        max_retries = 3
        backoff = [10, 20, 30]
        content = None
        is_503 = False
        model = "gemini-2.5-flash"

        for attempt in range(max_retries):
            try:
                if is_503:
                    model = "gemini-2.5-pro"
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )
            except Exception as e:
                error_msg = str(e)
                if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
                    print("Error: Gemini API quota exhausted. Retry later.", file=sys.stderr)
                    return None
                log(f"Attempt {attempt + 1}/{max_retries}: Gemini API error: {e}", quiet)
                if attempt < max_retries - 1:
                    if '503' in error_msg:
                        log("not your fault: this model is experiencing high demand, switching to another one", quiet)
                        is_503 = True
                    log(f"Retrying in {backoff[attempt]}s...", quiet)
                    time.sleep(backoff[attempt])
                    continue
                log("All retries exhausted.", quiet)
                return None

            if response and response.text:
                content = response.text
                break

            log(f"Attempt {attempt + 1}/{max_retries}: Gemini returned empty response", quiet)
            if attempt < max_retries - 1:
                log(f"Retrying in {backoff[attempt]}s...", quiet)
                time.sleep(backoff[attempt])

        if not content:
            print("Gemini API returned empty response after all retries", file=sys.stderr)
            return None

        # Extract JSON from response
        import re

        # Look for JSON array in code block
        json_match = re.search(r'```(?:json)?\s*(\[[\s\S]*?\])\s*```', content)
        if json_match:
            json_str = json_match.group(1)
            log("Extracted JSON from code block", quiet)
        else:
            # Try to find raw JSON array
            json_match = re.search(r'\[[\s\S]*\]', content)
            if json_match:
                json_str = json_match.group(0)
                log("Found raw JSON array", quiet)
            else:
                print("No JSON array found in response", file=sys.stderr)
                print(f"Response was: {content[:500]}...", file=sys.stderr)
                return None

        # Parse JSON
        try:
            trades = json.loads(json_str)
            log(f"Parsed {len(trades)} trade setups", quiet)
            return trades
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}", file=sys.stderr)
            print(f"JSON string was: {json_str[:500]}...", file=sys.stderr)
            return None

    except Exception as e:
        print(f"Error calling Gemini API: {e}", file=sys.stderr)
        return None


def load_existing_trades(output_path):
    """Load existing trades array from trades.json, returns [] if missing."""
    if not output_path.exists():
        return []
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('trades', [])
    except Exception:
        return []


def validate_trade(trade):
    """Validate a single trade setup matches expected schema."""
    required_fields = [
        'ticker', 'name', 'sector', 'entry', 'stop',
        'structure', 'trend', 'trendLabel', 'analysis',
        'riskScore', 'footerTag', 'setupType'
    ]

    valid_setup_types = ['perfect', 'momentum', 'breakout', 'risky', 'avoid']

    for field in required_fields:
        if field not in trade:
            return False, f"Missing field: {field}"

    if trade['setupType'] not in valid_setup_types:
        return False, f"Invalid setupType: {trade['setupType']}"

    if not isinstance(trade['riskScore'], int) or not 1 <= trade['riskScore'] <= 10:
        return False, f"Invalid riskScore: {trade['riskScore']}"

    return True, None


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Generate trade setups using Gemini AI')
    parser.add_argument('--quiet', '-q', action='store_true', help='Output only JSON')
    parser.add_argument('--tickers', '-t', help='Comma-separated list of tickers (e.g., AAPL,MSFT,TSLA)')
    parser.add_argument('--source', '-s', default='Watchlist', help='Source label for these trades (default: Watchlist)')
    parser.add_argument('--append', '-a', action='store_true', help='Append to existing trades.json instead of overwriting')
    args = parser.parse_args()

    log("\nGenerating trade setups...\n", args.quiet)

    # Get ticker list
    if args.tickers:
        tickers = [t.strip().upper() for t in args.tickers.split(',')]
        log(f"Using tickers from command line: {tickers}", args.quiet)
    else:
        tickers = load_watchlist()
        if not tickers:
            print("Error: No tickers provided. Use --tickers or create config/watchlist.json", file=sys.stderr)
            sys.exit(1)
        log(f"Loaded watchlist: {tickers}", args.quiet)

    # Load prompt from file
    prompt = load_prompt()
    if not prompt:
        sys.exit(1)

    log("Loaded TradeAnalyzer prompt", args.quiet)

    # Add today's date, tickers, and source to prompt
    today = datetime.now().strftime("%B %d, %Y")
    prompt = prompt.replace("{{DATE}}", today)
    prompt = prompt.replace("{{TICKERS}}", ", ".join(f"${t}" for t in tickers))
    prompt = prompt.replace("{{SOURCE}}", args.source)

    # Get API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Generate trades
    trades = generate_trades_with_gemini(prompt, api_key, args.quiet)
    if not trades:
        print("Failed to generate trades", file=sys.stderr)
        sys.exit(1)

    # Validate trades
    valid_trades = []
    for i, trade in enumerate(trades):
        is_valid, error = validate_trade(trade)
        if is_valid:
            valid_trades.append(trade)
        else:
            log(f"Warning: Trade {i+1} invalid - {error}", args.quiet)

    if not valid_trades:
        print("No valid trades generated", file=sys.stderr)
        sys.exit(1)

    log(f"Validated {len(valid_trades)} trades", args.quiet)

    # Determine output path early (needed for --append)
    repo_root = Path(__file__).parent.parent
    output_path = repo_root / 'public' / 'data' / 'trades.json'

    # Merge with existing trades if --append
    if args.append:
        existing = load_existing_trades(output_path)
        new_tickers = {t['ticker'] for t in valid_trades}
        kept = [t for t in existing if t['ticker'] not in new_tickers]
        valid_trades = kept + valid_trades
        log(f"Appended: {len(valid_trades)} total trades ({len(kept)} kept + {len(new_tickers)} new)", args.quiet)

    # Create output structure
    output = {
        "generatedAt": datetime.utcnow().isoformat() + "Z",
        "generatedBy": "trade-analyzer-agent",
        "tradeCount": len(valid_trades),
        "trades": valid_trades
    }

    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write JSON
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        log(f"Saved to {output_path}", args.quiet)
    except Exception as e:
        print(f"Error writing file: {e}", file=sys.stderr)
        sys.exit(1)

    # In quiet mode, output just the JSON to stdout
    if args.quiet:
        print(json.dumps(output, indent=2))
    else:
        print(f"\nTrade generation complete!")
        print(f"Output: public/data/trades.json")
        print(f"Trades: {len(valid_trades)}")


if __name__ == '__main__':
    main()
