#!/usr/bin/env python3
"""
Component: Rationale Generator (PERSON B)
Use Anthropic Claude to generate explanations for retrieved standards
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()


def get_anthropic_client():
    """Get Anthropic client using env API key (NEVER hardcode)."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key or api_key == "your_anthropic_api_key_here":
        return None
    return anthropic.Anthropic(api_key=api_key)


def generate_rationale(standards, query):
    """
    Generate explanation using Anthropic Claude API.
    standards: list of dicts with 'standard' and 'description'
    """
    client = get_anthropic_client()
    if not client:
        return "Anthropic API key not configured. Rationale generation skipped."

    # Format context
    context = "\n".join([f"- {s.get('id', s.get('standard', ''))}: {s.get('description', '')}" for s in standards])
    
    prompt = f"""
You are a Bureau of Indian Standards (BIS) expert assistant.
A user asked: "{query}"

Here are the top retrieved standards:
{context}

Provide a very concise, 2-3 sentence rationale explaining why these standards are relevant to the user's query.
Do not hallucinate any IS codes not listed above.
"""

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=150,
            temperature=0.0,
            system="You are a helpful BIS standards expert.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error generating rationale: {str(e)}"

if __name__ == "__main__":
    pass
