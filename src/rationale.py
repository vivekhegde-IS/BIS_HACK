#!/usr/bin/env python3
"""
Component: Rationale Generator (PERSON B)
Integration with OpenRouter for fast rationales.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def get_ai_client():
    """Get OpenAI-compatible client for OpenRouter."""
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        return None
    
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


def generate_rationale(standards, query):
    """
    Generate explanations using OpenRouter.
    """
    client = get_ai_client()
    if not client:
        return [f"Relevant to: {query}"] * len(standards)

    # Format context
    context = ""
    for i, s in enumerate(standards):
        context += f"{i+1}. {s.get('id', s.get('standard', ''))}: {s.get('description', '')}\n"
    
    prompt = f"""
You are a Bureau of Indian Standards (BIS) expert assistant.
A user asked: "{query}"

Here are the top retrieved standards:
{context}

For EACH of the {len(standards)} standards above, provide a very concise, 1-sentence rationale explaining why it is relevant.
IMPORTANT: Separate each of the {len(standards)} rationales with a triple hashtag '###'.
Example: Rationale 1 ### Rationale 2 ### Rationale 3...
"""

    try:
        # Using the fast Liquid AI model
        response = client.chat.completions.create(
            model="liquid/lfm-2.5-1.2b-instruct:free",
            messages=[
                {"role": "system", "content": "You are a helpful BIS standards expert who provides rationales separated by ###."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.0
        )
        full_text = response.choices[0].message.content
        # Split by delimiter and return list
        rationales = [r.strip() for r in full_text.split('###')]
        return rationales
    except Exception as e:
        print(f"[-] OpenRouter Error: {str(e)}")
        return [f"Relevant to: {query}"] * len(standards)

if __name__ == "__main__":
    pass
