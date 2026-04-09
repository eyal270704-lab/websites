#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
List available Gemini models and their capabilities.
"""

import os
import sys
import io
from google import genai

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def list_models():
    """List all available Gemini models."""
    api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyADPpFAd2Xfy9diJry6YTTi4Lhv3-RmsWQ')
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    try:
        client = genai.Client(api_key=api_key)

        print("🔍 Fetching available Gemini models...\n")

        # List all models
        models = client.models.list()

        print(f"Found {len(list(models))} models:\n")

        # Re-fetch to iterate (generator can only be consumed once)
        models = client.models.list()

        for model in models:
            print(f"📦 Model: {model.name}")
            if hasattr(model, 'display_name'):
                print(f"   Display Name: {model.display_name}")
            if hasattr(model, 'description'):
                print(f"   Description: {model.description}")
            if hasattr(model, 'supported_generation_methods'):
                print(f"   Supported Methods: {', '.join(model.supported_generation_methods)}")
            print()

    except Exception as e:
        print(f"❌ Error listing models: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    list_models()
