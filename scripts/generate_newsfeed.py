#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal newsfeed generator for Daily News Hub.

Generates JSON data for React newsfeeds using Google's Gemini API.
Config-driven and works with any newsfeed defined in config/newsfeeds.json.

Usage:
    python scripts/generate_newsfeed.py --feed nba
    python scripts/generate_newsfeed.py --feed stocks
    python scripts/generate_newsfeed.py --feed nba --format html  # Legacy mode
"""

import os
import sys
import io
import json
import re
import argparse
from pathlib import Path
from datetime import datetime, timezone
from google import genai
from google.genai import types

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# JSON output instructions appended to prompts
JSON_INSTRUCTIONS = """

CRITICAL OUTPUT REQUIREMENTS:
- Return ONLY valid JSON matching the schema below
- Do NOT include any markdown code blocks or explanation
- Use Google Search to find CURRENT, REAL-TIME information from today
- Today's date is: {date}

JSON SCHEMA:
{{
  "generatedAt": "ISO timestamp",
  "generatedBy": "{agent_id}",
  "feedType": "{feed_type}",
  "title": "Feed Title",
  "subtitle": "Optional subtitle with date",
  "badge": "Optional badge like 'LIVE' or 'Updated 2h ago'",
  "sections": [
    {{
      "id": "unique-section-id",
      "title": "Section Title",
      "cardType": "breaking|game|stock|article|stat|quote|alert",
      "layout": "grid|list|featured",
      "items": [
        {{
          "id": "unique-item-id",
          "headline": "Main headline text",
          "summary": "Optional longer description",
          "tags": ["tag1", "tag2"],
          "timestamp": "Optional timestamp",

          // For cardType: "game"
          "homeTeam": "Team Name",
          "awayTeam": "Team Name",
          "homeScore": 105,
          "awayScore": 102,
          "gameStatus": "scheduled|live|final",
          "gameTime": "7:30 PM ET",

          // For cardType: "stock"
          "ticker": "$AAPL",
          "price": "$185.50",
          "change": "+$2.30",
          "changePercent": "+1.25%",
          "direction": "up|down|flat",

          // For cardType: "stat"
          "statLabel": "Label",
          "statValue": "Value",
          "statContext": "Context",

          // For cardType: "quote"
          "quote": "The quote text",
          "author": "Author Name",
          "source": "Source"
        }}
      ]
    }}
  ]
}}

Return ONLY the JSON, no other text.
"""


def load_config(feed_type):
    """Load newsfeed configuration from config file."""
    config_path = Path(__file__).parent.parent / 'config' / 'newsfeeds.json'

    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}", file=sys.stderr)
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            all_configs = json.load(f)

        if feed_type not in all_configs:
            print(f"Error: Feed type '{feed_type}' not found in config", file=sys.stderr)
            print(f"Available feeds: {', '.join(all_configs.keys())}", file=sys.stderr)
            return None

        config = all_configs[feed_type]
        print(f"Loaded configuration for '{feed_type}' feed", file=sys.stderr)
        return config

    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        return None


def load_prompt(config, feed_type):
    """Load prompt from file or environment variable."""
    repo_root = Path(__file__).parent.parent

    # Try loading from prompt file first (preferred)
    if 'promptFile' in config:
        prompt_path = repo_root / config['promptFile']
        if prompt_path.exists():
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    prompt = f.read()
                print(f"Loaded prompt from {config['promptFile']}", file=sys.stderr)
                return prompt
            except Exception as e:
                print(f"Warning: Could not load prompt file: {e}", file=sys.stderr)

    # Fall back to environment variable (legacy)
    if 'prompt_secret' in config:
        prompt = os.environ.get(config['prompt_secret'])
        if prompt:
            print(f"Loaded prompt from {config['prompt_secret']} env var", file=sys.stderr)
            return prompt

    print(f"Error: No prompt found for {feed_type}", file=sys.stderr)
    return None


def generate_json_with_gemini(prompt, api_key, feed_type):
    """Generate JSON content using Gemini API with Google Search grounding."""
    try:
        client = genai.Client(api_key=api_key)

        # Set up Google Search tool for real-time data
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        gen_config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )

        # Add JSON instructions to prompt
        today = datetime.now().strftime("%B %d, %Y")
        agent_id = f"{feed_type}-agent"

        full_prompt = prompt + JSON_INSTRUCTIONS.format(
            date=today,
            agent_id=agent_id,
            feed_type=feed_type
        )

        print("Calling Gemini API with Google Search grounding...", file=sys.stderr)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
            config=gen_config,
        )

        if not response or not response.text:
            print("Gemini API returned empty response", file=sys.stderr)
            return None

        content = response.text

        # Extract JSON from response
        # Try to find JSON object in code block first
        json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', content)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON object
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                json_str = json_match.group(0)
            else:
                print("No JSON object found in response", file=sys.stderr)
                print(f"Response was: {content[:500]}...", file=sys.stderr)
                return None

        # Parse and validate JSON
        try:
            data = json.loads(json_str)

            # Ensure required fields
            if 'generatedAt' not in data:
                data['generatedAt'] = datetime.now(timezone.utc).isoformat()
            if 'generatedBy' not in data:
                data['generatedBy'] = agent_id
            if 'feedType' not in data:
                data['feedType'] = feed_type

            print(f"Parsed JSON with {len(data.get('sections', []))} sections", file=sys.stderr)
            return data

        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}", file=sys.stderr)
            print(f"JSON string was: {json_str[:500]}...", file=sys.stderr)
            return None

    except Exception as e:
        print(f"Error calling Gemini API: {e}", file=sys.stderr)
        return None


def save_json(data, config):
    """Save JSON data to public/data/ directory."""
    repo_root = Path(__file__).parent.parent
    output_dir = repo_root / 'public' / 'data'
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = config.get('dataFile', f"{config['id']}.json")
    output_path = output_dir / output_file

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved to {output_path}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"Error writing file: {e}", file=sys.stderr)
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Generate newsfeed data using Gemini AI')
    parser.add_argument('--feed', required=True, help='Feed type (e.g., nba, stocks)')
    parser.add_argument('--format', choices=['json', 'html'], default='json',
                        help='Output format (default: json)')
    args = parser.parse_args()

    print(f"\nGenerating {args.feed} newsfeed...\n", file=sys.stderr)

    # Load configuration
    config = load_config(args.feed)
    if not config:
        sys.exit(1)

    # Get API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Load prompt
    prompt = load_prompt(config, args.feed)
    if not prompt:
        sys.exit(1)

    # Generate content
    if args.format == 'json':
        data = generate_json_with_gemini(prompt, api_key, args.feed)
        if not data:
            print("Failed to generate JSON content", file=sys.stderr)
            sys.exit(1)

        if not save_json(data, config):
            sys.exit(1)

        print(f"\nNewsfeed generation complete!", file=sys.stderr)
        print(f"Output: public/data/{config.get('dataFile', args.feed + '.json')}", file=sys.stderr)
    else:
        # Legacy HTML mode - keep for backwards compatibility
        print("HTML mode is deprecated. Please use JSON mode.", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
