#!/usr/bin/env python3
"""
Component 3: Retriever (PERSON A)
Retrieve top-5 relevant IS standards using TF-IDF + cosine similarity + query expansion.

Usage (standalone test):
    python src/retriever.py

Import usage:
    from src.retriever import retrieve, load_model_once
"""

import pickle
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()

MODEL_PATH = os.getenv('MODEL_PATH', './tfidf_model.pkl')

# ─── Query Expansion Synonym Dictionary ───────────────────────────────────────
# Maps common query terms to BIS-domain synonyms for better recall.
SYNONYMS = {
    'cement':         ['portland', 'OPC', 'clinker', 'binder', 'cementitious', 'mortar', 'binding'],
    'portland':       ['OPC', 'cement', 'clinker', 'IS 269'],
    'slag':           ['blast furnace', 'GGBS', 'portland slag', 'PSC'],
    'pozzolana':      ['fly ash', 'PPC', 'calcined clay', 'volcanic', 'silica fume'],
    'pozzolanic':     ['fly ash', 'pozzolana', 'PPC', 'calcined'],
    'aggregate':      ['sand', 'gravel', 'crushed stone', 'coarse', 'fine', 'ballast', 'natural'],
    'concrete':       ['RCC', 'reinforced', 'precast', 'prestressed', 'structural', 'mix'],
    'pipe':           ['tube', 'conduit', 'pipeline', 'culvert', 'precast concrete pipe'],
    'brick':          ['masonry', 'clay brick', 'burnt', 'block'],
    'masonry':        ['brick', 'block', 'mortar', 'wall', 'stone'],
    'block':          ['masonry block', 'concrete block', 'hollow', 'solid', 'lightweight'],
    'roofing':        ['roof', 'sheet', 'corrugated', 'cladding', 'asbestos', 'tile'],
    'asbestos':       ['AC sheet', 'corrugated', 'fibre cement', 'semi-corrugated'],
    'steel':          ['iron', 'TMT', 'rebar', 'reinforcement', 'structural steel', 'bars'],
    'reinforcement':  ['rebar', 'steel bar', 'TMT', 'deformed bar', 'mild steel'],
    'water':          ['hydraulic', 'waterproof', 'moisture resistant', 'aqueous'],
    'supersulphated': ['sulphate resistant', 'marine', 'aggressive environment', 'sulfate'],
    'white':          ['architectural', 'decorative', 'white portland', 'aesthetic'],
    'lightweight':    ['aerated', 'cellular', 'foam concrete', 'hollow block', 'AAC'],
    'chemical':       ['composition', 'compound', 'content', 'requirement', 'specification'],
    'physical':       ['strength', 'property', 'characteristic', 'mechanical', 'performance'],
    'specification':  ['requirement', 'standard', 'code', 'BIS', 'regulation', 'IS code'],
    'manufacture':    ['manufacturing', 'production', 'plant', 'process', 'fabrication'],
    'testing':        ['test', 'method', 'procedure', 'evaluation', 'assessment'],
    'grade':          ['class', 'type', 'category', 'designation', 'quality'],
    'precast':        ['prefabricated', 'factory made', 'precast concrete', 'cast'],
    'structural':     ['load bearing', 'RCC', 'concrete', 'steel structure', 'frame'],
    'ordinary':       ['OPC', 'general purpose', 'standard', '33 grade', '43 grade', '53 grade'],
}

# ─── Singleton model cache ────────────────────────────────────────────────────
_model_cache = None


def load_model_once():
    """
    Load TF-IDF model from disk ONCE and cache in memory.
    Subsequent calls return the cached model (Rule A-3: load outside loop).
    """
    global _model_cache
    if _model_cache is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at '{MODEL_PATH}'.\n"
                "Run the pipeline first:\n"
                "  python src/ingest.py\n"
                "  python src/indexer.py"
            )
        print(f"Loading model from {MODEL_PATH} ...")
        with open(MODEL_PATH, 'rb') as f:
            _model_cache = pickle.load(f)
        n_chunks = len(_model_cache['chunks'])
        vocab_size = len(_model_cache['vectorizer'].vocabulary_)
        print(f"  Model loaded: {n_chunks} standards, vocab={vocab_size}")
    return _model_cache


def expand_query(query: str) -> str:
    """
    Expand query with domain synonyms to improve recall.

    Example:
        "Portland slag cement requirements"
        → adds 'blast furnace GGBS portland slag PSC OPC cement clinker ...'
    """
    query_lower = query.lower()
    extra_terms = []

    for keyword, synonyms in SYNONYMS.items():
        if keyword in query_lower:
            extra_terms.extend(synonyms[:4])   # Add up to 4 synonyms

    expanded = query + ' ' + ' '.join(extra_terms) if extra_terms else query
    return expanded


def retrieve(query: str, top_k: int = 5) -> list:
    """
    Retrieve top-k IS standards most relevant to the query.

    Args:
        query:  Natural language query string
        top_k:  Number of results (ALWAYS 5 per Rule A-4)

    Returns:
        List of exactly top_k IS standard strings, e.g.:
        ["IS 269: 1989", "IS 8112: 1989", "IS 12269: 1987", "IS 455: 1989", "IS 1489 (Part 1): 1991"]
    """
    model = load_model_once()
    vectorizer   = model['vectorizer']
    tfidf_matrix = model['tfidf_matrix']
    chunks       = model['chunks']

    # Expand query for better coverage
    expanded_query = expand_query(query)

    # Vectorize and compute cosine similarities
    query_vec    = vectorizer.transform([expanded_query])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()

    # Sort by descending similarity, collect unique standards
    top_indices = np.argsort(similarities)[::-1]

    results = []
    seen    = set()
    for idx in top_indices:
        standard = chunks[idx]['standard']
        if standard not in seen:
            seen.add(standard)
            results.append(standard)
        if len(results) >= top_k:
            break

    # Safety net: pad if fewer than top_k found (shouldn't happen with real data)
    fallback_pool = [
        "IS 269: 1989", "IS 383: 1970", "IS 455: 1989",
        "IS 456: 2000", "IS 1489 (Part 1): 1991", "IS 2185 (Part 1): 1979",
    ]
    for fb in fallback_pool:
        if len(results) >= top_k:
            break
        if fb not in seen:
            results.append(fb)

    return results[:top_k]   # Always exactly 5 (Rule A-4)


# ─── Quick standalone test ────────────────────────────────────────────────────
if __name__ == "__main__":
    test_queries = [
        "33 Grade Ordinary Portland Cement chemical and physical requirements",
        "coarse and fine aggregates from natural sources for structural concrete",
        "Portland slag cement manufacture and testing",
        "lightweight concrete masonry blocks hollow and solid",
        "supersulphated cement marine works aggressive water",
    ]

    try:
        load_model_once()
        print("\n--- Retrieval Test ---")
        for q in test_queries:
            results = retrieve(q)
            print(f"\nQ: {q[:60]}...")
            for rank, std in enumerate(results, 1):
                print(f"  {rank}. {std}")
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
