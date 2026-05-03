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

Provide a concise 1-2 sentence rationale for EACH of the {len(standards)} standards, explaining why it is specifically relevant to the user's query.

Respond strictly in JSON format with a single key "rationales" containing a list of strings, in the exact same order as the standards.
Example:
{{
  "rationales": [
    "Rationale for the first standard...",
    "Rationale for the second standard...",
    ...
  ]
}}
"""

    try:
        import json
        import re
        
        models_to_try = [
            "google/gemma-2-9b-it:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "qwen/qwen-2.5-72b-instruct:free",
            "nvidia/nemotron-3-super-120b-a12b:free"
        ]
        
        rationales = []
        for model_id in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": "You are a helpful BIS standards expert. Respond ONLY in valid JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=600,
                    temperature=0.1,
                    timeout=12.0
                )
                content = response.choices[0].message.content
                
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
                    
                data = json.loads(content)
                rationales = data.get("rationales", [])
                
                if len(rationales) > 0:
                    break # Success!
            except Exception as loop_e:
                print(f"[*] Model {model_id} failed: {str(loop_e)}")
                continue
                
        # Ensure we return exactly len(standards) items
        if len(rationales) < len(standards):
            rationales += [f"Relevant to: {query}"] * (len(standards) - len(rationales))
        elif len(rationales) > len(standards):
            rationales = rationales[:len(standards)]
            
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
        models_to_try = [
            "google/gemma-2-9b-it:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "qwen/qwen-2.5-72b-instruct:free",
            "nvidia/nemotron-3-super-120b-a12b:free"
        ]
        
        llm_lines = []
        for model_id in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": "You are a BIS ranking expert. Output ONLY standard IDs, one per line."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.0,
                    timeout=10.0
                )
                llm_lines = [line.strip() for line in response.choices[0].message.content.split('\n') if line.strip()]
                if len(llm_lines) > 0:
                    break
            except Exception as loop_e:
                print(f"[*] Rerank model {model_id} failed: {str(loop_e)}")
                continue
        
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
