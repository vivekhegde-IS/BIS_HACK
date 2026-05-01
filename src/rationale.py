#!/usr/bin/env python3
"""
Component: Rationale Generator (PERSON B)
Use Anthropic Claude to generate explanations for retrieved standards

Usage:
    from src.rationale import generate_rationale
    rationale = generate_rationale(standards, query)
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_anthropic_key():
    """Get API key from environment (NEVER hardcode)."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in .env")
    return api_key


def generate_rationale(standards, query):
    """Generate explanation using Anthropic Claude API."""
    pass


if __name__ == "__main__":
    pass
