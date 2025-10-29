#!/usr/bin/env python3
"""
Inject API keys and secrets into HTML files during GitHub Pages deployment.

This script replaces placeholder values with actual secrets from environment variables.
It's designed to be run as part of a GitHub Actions workflow.
"""

import os
import sys
from pathlib import Path


def inject_secret(file_path, placeholder, secret_name):
    """
    Replace a placeholder in a file with the actual secret value.

    Args:
        file_path: Path to the file to modify
        placeholder: The placeholder string to replace
        secret_name: Name of the environment variable containing the secret

    Returns:
        bool: True if successful, False otherwise
    """
    # Get secret from environment
    secret_value = os.environ.get(secret_name)

    if not secret_value:
        print(f"❌ Error: {secret_name} environment variable not set", file=sys.stderr)
        return False

    # Check if file exists
    if not file_path.exists():
        print(f"❌ Error: File not found: {file_path}", file=sys.stderr)
        return False

    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}", file=sys.stderr)
        return False

    # Check if placeholder exists
    if placeholder not in content:
        print(f"⚠️  Warning: Placeholder '{placeholder}' not found in {file_path}")
        return True  # Not an error, just skip

    # Replace placeholder with secret
    updated_content = content.replace(placeholder, secret_value)

    # Write back to file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
    except Exception as e:
        print(f"❌ Error writing to {file_path}: {e}", file=sys.stderr)
        return False

    print(f"✅ Successfully injected {secret_name} into {file_path.name}")
    return True


def main():
    """Main function to inject all secrets."""
    print("🔐 Starting secret injection process...\n")

    # Get the repository root (parent of scripts directory)
    repo_root = Path(__file__).parent.parent
    docs_dir = repo_root / 'docs'

    # Define files and their placeholders
    injections = [
        {
            'file': docs_dir / 'creator-monetization.html',
            'placeholder': 'PLACEHOLDER_API_KEY',
            'secret': 'GEMINI_API_KEY'
        },
        {
            'file': docs_dir / 'stock-market-news.html',
            'placeholder': 'PLACEHOLDER_API_KEY',
            'secret': 'GEMINI_API_KEY'
        },
        # Add more files here as you create new pages that need secrets
    ]

    # Track success
    all_successful = True

    # Process each injection
    for injection in injections:
        success = inject_secret(
            injection['file'],
            injection['placeholder'],
            injection['secret']
        )
        if not success:
            all_successful = False

    # Exit with appropriate code
    if all_successful:
        print("\n✨ All secrets injected successfully!")
        sys.exit(0)
    else:
        print("\n💥 Secret injection failed!", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
