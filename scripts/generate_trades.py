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

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config,
        )

        if not response or not response.text:
            print("Gemini API returned empty response", file=sys.stderr)
            return None

        content = response.text

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

    # Add today's date and tickers to prompt
    today = datetime.now().strftime("%B %d, %Y")
    prompt = prompt.replace("{{DATE}}", today)
    prompt = prompt.replace("{{TICKERS}}", ", ".join(f"${t}" for t in tickers))

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

    # Create output structure
    output = {
        "generatedAt": datetime.utcnow().isoformat() + "Z",
        "generatedBy": "trade-analyzer-agent",
        "tradeCount": len(valid_trades),
        "trades": valid_trades
    }

    # Determine output path
    repo_root = Path(__file__).parent.parent
    output_path = repo_root / 'public' / 'data' / 'trades.json'

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
