#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal newsfeed generator for Daily News Hub.

This script generates HTML pages for various newsfeeds (NBA, stocks, etc.)
using Google's Gemini API. It's config-driven and works with any newsfeed
defined in config/newsfeeds.json.

Usage:
    python scripts/generate_newsfeed.py --feed nba
    python scripts/generate_newsfeed.py --feed stocks
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


# HTML template for all newsfeeds
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Daily News Hub</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script>
    <style>
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .animate-fade-in {{
            animation: fadeIn 0.6s ease-out forwards;
        }}
        .gradient-bg {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
    </style>
</head>
<body class="bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 min-h-screen text-white">
    <div class="container mx-auto px-4 py-8 md:py-12 max-w-7xl">
        <!-- Back to Hub Button -->
        <div class="mb-8">
            <a href="index.html" class="inline-flex items-center gap-2 text-white hover:text-cyan-400 transition-colors text-lg font-medium">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
                </svg>
                Back to Hub
            </a>
        </div>

        <!-- Generated Content -->
        <main class="animate-fade-in">
            {content}
        </main>

        <!-- Footer -->
        <footer class="mt-16 pt-8 border-t border-gray-700 text-center text-gray-400 text-sm">
            <p>Generated on {timestamp}</p>
            <p class="mt-2">Powered by Gemini AI | Daily News Hub</p>
        </footer>
    </div>
</body>
</html>
"""


def load_config(feed_type):
    """Load newsfeed configuration from config file."""
    config_path = Path(__file__).parent.parent / 'config' / 'newsfeeds.json'

    if not config_path.exists():
        print(f"❌ Error: Config file not found: {config_path}", file=sys.stderr)
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            all_configs = json.load(f)

        if feed_type not in all_configs:
            print(f"❌ Error: Feed type '{feed_type}' not found in config", file=sys.stderr)
            print(f"Available feeds: {', '.join(all_configs.keys())}", file=sys.stderr)
            return None

        config = all_configs[feed_type]
        print(f"✅ Loaded configuration for '{feed_type}' feed")
        return config

    except Exception as e:
        print(f"❌ Error loading config: {e}", file=sys.stderr)
        return None


def adapt_prompt(original_prompt):
    """
    Adapt the user's prompt to work with our pipeline.

    Removes file-saving instructions and adds formatting requirements.
    """
    from datetime import datetime

    adapted = original_prompt

    # Get today's date
    today = datetime.now().strftime("%B %d, %Y")

    # Instructions to add at the end
    formatting_instructions = f"""

CRITICAL DATE REQUIREMENT:
- TODAY'S DATE IS: {today}
- Use Google Search to find CURRENT, REAL-TIME information from {today}
- DO NOT use historical or training data
- All games, scores, and stats MUST be from {today} or the most recent available date
- If no games are scheduled today, show the most recent games and upcoming schedule

IMPORTANT OUTPUT REQUIREMENTS:
- Return ONLY the HTML body content (no <html>, <head>, or <body> tags)
- Do NOT include any file-saving or download instructions
- Use Tailwind CSS classes for all styling (CDN is already included)
- Use blue/teal/purple gradient themes to match the Daily News Hub design
- Make the design modern, responsive, and visually appealing
- Include proper spacing, cards, and gradients for visual hierarchy
- The content will be wrapped in our site template automatically

CRITICAL TEXT COLOR REQUIREMENTS FOR CARDS:
- All cards with white backgrounds (bg-white) MUST use black text for readability
- Card headlines/titles: Use "text-gray-900" class (dark gray/black)
- Card body text/descriptions: Use "text-black" class
- Section headers: Use "text-gray-900" class
- List items: Use "text-black" class
- This ensures proper contrast and readability on white card backgrounds

Return the complete HTML content ready to inject into the page.
"""

    # Remove file-saving related text (if present)
    lines_to_remove = [
        "saved to /mnt/user-data/outputs/",
        "[View your",
        "computer:///mnt/",
        "Provide the download link"
    ]

    adapted_lines = []
    for line in adapted.split('\n'):
        should_keep = True
        for remove_phrase in lines_to_remove:
            if remove_phrase in line:
                should_keep = False
                break
        if should_keep:
            adapted_lines.append(line)

    adapted = '\n'.join(adapted_lines)
    adapted += formatting_instructions

    return adapted


def generate_content_with_gemini(prompt, api_key):
    """
    Generate HTML content using Gemini API with Google Search grounding.

    Args:
        prompt: The adapted prompt to send to Gemini
        api_key: Google Gemini API key

    Returns:
        str: Generated HTML content, or None if failed
    """
    try:
        # Initialize Gemini client with API key
        client = genai.Client(api_key=api_key)

        # Set up Google Search tool for real-time grounding
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        # Create generation config with the tool
        config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )

        print("🔄 Calling Gemini API with Google Search grounding...")

        # Generate content with grounding enabled
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config,
        )

        if not response or not response.text:
            print("❌ Gemini API returned empty response", file=sys.stderr)
            return None

        content = response.text

        # Extract content from markdown code blocks if present
        import re

        # Look for content between ```html and ``` or ``` and ```
        html_block_match = re.search(r'```html\s*(.*?)\s*```', content, re.DOTALL)
        if html_block_match:
            content = html_block_match.group(1).strip()
            print("✅ Extracted HTML from code block")
        else:
            # Try generic code block
            code_block_match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
            if code_block_match:
                content = code_block_match.group(1).strip()
                print("✅ Extracted content from code block")
            else:
                # No code blocks, use as-is but remove common prefixes
                # Remove explanatory text that Gemini sometimes adds
                if content.startswith('Okay, I will') or content.startswith('Here\'s'):
                    # Try to find where the actual content starts
                    lines = content.split('\n')
                    # Skip lines until we find something that looks like HTML or content
                    content_start = 0
                    for i, line in enumerate(lines):
                        if line.strip().startswith('<') or line.strip().startswith('#'):
                            content_start = i
                            break
                    content = '\n'.join(lines[content_start:])

                content = content.strip()

        print(f"✅ Generated {len(content)} characters of HTML content")

        return content

    except Exception as e:
        print(f"❌ Error calling Gemini API: {e}", file=sys.stderr)
        return None


def markdown_to_html(text):
    """
    Convert markdown text to HTML with proper styling.

    Args:
        text: Markdown formatted text

    Returns:
        str: HTML formatted text with Tailwind CSS classes
    """
    if not text:
        return ""

    import re

    # First, convert bold text before processing lines
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong class="font-semibold text-white">\1</strong>', text)

    lines = text.split('\n')
    formatted_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append('')
            continue

        # Handle headers (must check before they're modified)
        if stripped.startswith('### '):
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            header_text = stripped[4:].strip()
            formatted_lines.append(f'<h3 class="text-xl font-semibold text-blue-300 mt-6 mb-3">{header_text}</h3>')
        elif stripped.startswith('## '):
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            header_text = stripped[3:].strip()
            formatted_lines.append(f'<h2 class="text-2xl font-bold text-blue-300 mt-8 mb-4">{header_text}</h2>')
        elif stripped.startswith('# '):
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            header_text = stripped[2:].strip()
            formatted_lines.append(f'<h1 class="text-3xl font-bold text-blue-400 mt-10 mb-5">{header_text}</h1>')
        # Handle bullet points
        elif stripped.startswith('* ') or stripped.startswith('- '):
            if not in_list:
                formatted_lines.append('<ul class="list-disc list-inside space-y-2 ml-4 my-4 text-gray-200">')
                in_list = True
            item_text = stripped[2:].strip()  # Remove '* ' or '- '
            formatted_lines.append(f'    <li class="leading-relaxed">{item_text}</li>')
        # Regular text
        else:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            # Don't wrap if it's already HTML
            if not stripped.startswith('<'):
                formatted_lines.append(f'<p class="text-gray-200 my-3 leading-relaxed">{stripped}</p>')
            else:
                formatted_lines.append(line)

    # Close any open list
    if in_list:
        formatted_lines.append('</ul>')

    return '\n'.join(formatted_lines)


def create_html_page(content, title, output_path):
    """
    Wrap generated content in site template or inject into existing template.

    Args:
        content: Generated HTML content
        title: Page title
        output_path: Path to output file

    Returns:
        str: Complete HTML page
    """
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    # Convert markdown to HTML if needed
    formatted_content = markdown_to_html(content)

    # Check if output file already exists (template-based approach)
    if output_path.exists():
        print(f"📄 Found existing template at {output_path.name}, injecting content...")
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                template_html = f.read()

            # Replace the content placeholder
            if '<!-- CONTENT_PLACEHOLDER -->' in template_html:
                html = template_html.replace(
                    '<!-- CONTENT_PLACEHOLDER -->',
                    formatted_content
                )
                print(f"✅ Injected formatted content into existing template")
                return html
            else:
                print(f"⚠️  Template found but no CONTENT_PLACEHOLDER, using generic template")
        except Exception as e:
            print(f"⚠️  Error reading template: {e}, using generic template")

    # Use generic template
    html = HTML_TEMPLATE.format(
        title=title,
        content=formatted_content,
        timestamp=timestamp
    )

    return html


def update_index_html(docs_dir, config):
    """
    Update index.html to activate the newsfeed card (first run only).

    Args:
        docs_dir: Path to docs directory
        config: Feed configuration dict
    """
    index_path = docs_dir / 'index.html'

    if not index_path.exists():
        print(f"⚠️  Warning: {index_path} not found, skipping index update")
        return False

    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()

        card_class = config['card_class']
        output_file = config['output_file']

        # Check if card is already active (has href)
        if f'href="{output_file}"' in content:
            print(f"✅ Index.html card already active for {card_class}")
            return True

        # Update card from coming-soon to active
        original_content = content

        # Replace coming-soon div with link
        content = content.replace(
            f'<div class="news-card {card_class} coming-soon-card',
            f'<a href="{output_file}" class="news-card {card_class}'
        )

        # Update badge
        # Find the card section and update only its badge
        if card_class in content:
            lines = content.split('\n')
            in_target_card = False
            badge_updated = False

            for i, line in enumerate(lines):
                if f'news-card {card_class}' in line:
                    in_target_card = True
                if in_target_card and '<span class="badge">Coming Soon</span>' in line and not badge_updated:
                    lines[i] = line.replace('Coming Soon', 'Active')
                    badge_updated = True
                if in_target_card and '</div>' in line or '</a>' in line:
                    in_target_card = False

            content = '\n'.join(lines)

        # Update "Coming Soon" text to "Explore Dashboard →"
        # This is trickier - we need to be more specific
        content = content.replace(
            '<span class="text-sm font-semibold opacity-50">Coming Soon</span>',
            '<span class="text-sm font-semibold">Explore Dashboard →</span>'
        )

        if content != original_content:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated index.html to activate {card_class} card")
            return True
        else:
            print(f"⚠️  No changes made to index.html")
            return False

    except Exception as e:
        print(f"❌ Error updating index.html: {e}", file=sys.stderr)
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Generate newsfeed HTML page using Gemini AI')
    parser.add_argument('--feed', required=True, help='Feed type (e.g., nba, stocks)')
    args = parser.parse_args()

    print(f"\n📰 Generating {args.feed} newsfeed...\n")

    # Load configuration
    config = load_config(args.feed)
    if not config:
        sys.exit(1)

    # Get API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Get prompt from environment (secret)
    prompt_secret_name = config['prompt_secret']
    original_prompt = os.environ.get(prompt_secret_name)
    if not original_prompt:
        print(f"❌ Error: {prompt_secret_name} environment variable not set", file=sys.stderr)
        print(f"Please add this secret to GitHub repository settings", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Loaded prompt from {prompt_secret_name}")

    # Adapt prompt for our pipeline
    adapted_prompt = adapt_prompt(original_prompt)

    # Generate content with Gemini
    generated_content = generate_content_with_gemini(adapted_prompt, api_key)
    if not generated_content:
        print("❌ Failed to generate content", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    repo_root = Path(__file__).parent.parent
    docs_dir = repo_root / 'docs'
    output_path = docs_dir / config['output_file']

    # Create full HTML page (with template injection support)
    full_html = create_html_page(generated_content, config['title'], output_path)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        print(f"✅ Successfully saved to {output_path}")
    except Exception as e:
        print(f"❌ Error writing file: {e}", file=sys.stderr)
        sys.exit(1)

    # Update index.html to activate card
    print(f"\n📝 Updating index.html...")
    update_index_html(docs_dir, config)

    print(f"\n✨ Newsfeed generation complete!")
    print(f"📄 Output: {config['output_file']}")
    print(f"🌐 Will be live at: https://eyal270704-lab.github.io/websites/{config['output_file']}\n")


if __name__ == '__main__':
    main()
