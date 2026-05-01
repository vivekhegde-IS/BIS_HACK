#!/usr/bin/env python3
"""
Component: Rationale Generator (PERSON B)
Integration with OpenRouter for fast rationales.
"""

import os
import re
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


def re_rank_standards(query, candidates):
    """
    Use LLM to re-rank the top-10 candidates back to top-5.
    Returns list of standard IDs in order of relevance.
    """
    client = get_ai_client()
    if not client:
        return [c.get('standard') for c in candidates][:5]

    context = ""
    for i, c in enumerate(candidates):
        context += f"[{i}] {c.get('standard')}: {c.get('description', '')}\n"

    prompt = f"""
Query: "{query}"

Candidates:
{context}

Based on the query, identify the TOP 5 most relevant standards from the candidates above.
Output ONLY the standard IDs (e.g. IS 269: 1989), one per line, in descending order of relevance.
Do not include indices or descriptions.
"""

    try:
        response = client.chat.completions.create(
            model="liquid/lfm-2.5-1.2b-instruct:free",
            messages=[
                {"role": "system", "content": "You are a BIS ranking expert. Output ONLY standard IDs, one per line."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.0
        )
        llm_lines = [line.strip() for line in response.choices[0].message.content.split('\n') if line.strip()]
        
        # Fuzzy match LLM output back to original IDs
        valid_map = {re.sub(r'[\s\(\)]', '', cid).lower(): cid for cid in [c.get('standard') for c in candidates]}
        
        final_ids = []
        for line in llm_lines:
            norm_line = re.sub(r'[\s\(\)]', '', line).lower()
            if norm_line in valid_map:
                std_id = valid_map[norm_line]
                if std_id not in final_ids:
                    final_ids.append(std_id)
        
        # Pad with remaining candidates if needed
        original_ids = [c.get('standard') for c in candidates]
        for oid in original_ids:
            if len(final_ids) >= 5: break
            if oid not in final_ids:
                final_ids.append(oid)
                
        return final_ids[:5]
    except Exception as e:
        print(f"[-] Re-rank Error: {str(e)}")
        return [c.get('standard') for c in candidates][:5]

if __name__ == "__main__":
    pass
