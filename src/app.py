#!/usr/bin/env python3
"""
Component: Flask Web UI (PERSON B)
Web interface for BIS Standards RAG System - connects frontend with backend pipeline

Features:
- Loads TF-IDF model at startup (NOT per-request) - Rule B-2
- Uses backend retriever for real search
- Integrates Anthropic Claude for explanations
- Beautiful single-page app with gradient UI
- Real-time search results with latency tracking

Usage:
    python src/app.py
    # Open: http://localhost:5000

CRITICAL REQUIREMENTS:
- Model must exist at data/tfidf_model.pkl (run: python src/indexer.py first)
- ANTHROPIC_API_KEY must be set in .env (optional, demo mode if missing)
- Flask templates in src/templates/
"""

import time
import sys
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify

# ─── Add src/ to Python path ────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent / ".."))

# ─── Import backend modules ────────────────────────────────────────────────
from src.retriever import retrieve, load_model_once
from src.rationale import generate_rationale

app = Flask(__name__, template_folder="templates")

# ─── Global state ───────────────────────────────────────────────────────────
MODEL_LOADED = False
MODEL_ERROR = None
MODEL_DATA = None

# ─── DEMO DATA (fallback if model not available) ────────────────────────────
DEMO_BIS_DB = [
    {
        "id": "IS 269: 1989",
        "title": "Ordinary Portland Cement, 33 Grade — Specification",
        "description": "This standard specifies chemical composition, physical properties for OPC. Widely used in general construction.",
        "tags": ["cement", "portland", "ordinary", "concrete"],
    },
    {
        "id": "IS 383: 1970",
        "title": "Coarse and Fine Aggregates from Natural Sources for Concrete",
        "description": "Specifies grading requirements and physical properties for aggregates used in concrete.",
        "tags": ["aggregates", "concrete", "natural", "coarse", "fine"],
    },
    {
        "id": "IS 455: 1989",
        "title": "Portland Slag Cement — Specification",
        "description": "Specifies Portland slag cement with improved resistance to sulphate attack.",
        "tags": ["cement", "slag", "portland", "construction", "marine"],
    },
    {
        "id": "IS 456: 2000",
        "title": "Plain and Reinforced Concrete — Code of Practice",
        "description": "Code of practice for plain and reinforced concrete for general building construction.",
        "tags": ["concrete", "reinforced", "code", "practice"],
    },
    {
        "id": "IS 1489 (Part 1): 1991",
        "title": "Portland Pozzolana Cement — Specification",
        "description": "Covers Portland pozzolana cement specifications with lower heat of hydration.",
        "tags": ["cement", "pozzolana", "portland"],
    },
]


def init_model():
    """
    Load TF-IDF model at app startup (NOT per-request).
    Implements Rule B-2: Load model outside request handlers.
    """
    global MODEL_LOADED, MODEL_ERROR, MODEL_DATA
    try:
        print("[*] Initializing BIS Standards RAG System...")
        MODEL_DATA = load_model_once()
        MODEL_LOADED = True
        print("[✓] TF-IDF model loaded successfully")
        print(f"    Standards: {len(MODEL_DATA['chunks'])}")
        print(f"    Vocabulary: {len(MODEL_DATA['vectorizer'].vocabulary_)}")
        return True
    except FileNotFoundError as e:
        MODEL_ERROR = f"Model not found: {str(e)}"
        print(f"[✗] {MODEL_ERROR}")
        print("    Hint: Run these commands first:")
        print("      python src/ingest.py")
        print("      python src/indexer.py")
        return False
    except Exception as e:
        MODEL_ERROR = f"Model load error: {str(e)}"
        print(f"[✗] {MODEL_ERROR}")
        return False


def demo_search(query: str, top_k: int = 5):
    """
    Demo keyword-based search over DEMO_BIS_DB (fallback only).
    """
    query_tokens = set(query.lower().split())
    scored = []
    for entry in DEMO_BIS_DB:
        searchable = " ".join([
            entry.get("title", "").lower(),
            entry.get("description", "").lower(),
            " ".join(entry.get("tags", [])),
        ])
        score = sum(1 for token in query_tokens if token in searchable)
        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored[:top_k]]


def real_search(query: str, top_k: int = 5):
    """
    Real search using TF-IDF backend + query expansion.
    Returns list of standard dicts with id, title, description, rationale.
    """
    if not MODEL_LOADED or MODEL_DATA is None:
        return None

    try:
        # ─── Retrieve top-k standards using TF-IDF ──────────────────────────
        retrieved_ids = retrieve(query, top_k=top_k)
        
        # ─── Build result dicts ──────────────────────────────────────────────
        chunks = MODEL_DATA['chunks']
        results = []
        
        for std_id in retrieved_ids:
            # Find the chunk data
            chunk_data = None
            for chunk in chunks:
                if chunk.get('standard') == std_id:
                    chunk_data = chunk
                    break
            
            if chunk_data:
                result = {
                    "id": std_id,
                    "title": chunk_data.get('title', std_id),
                    "description": chunk_data.get('description', ''),
                    "rationale": "",
                }
                
                # ─── Generate rationale using Claude (if API key configured) ──
                try:
                    rationale = generate_rationale([chunk_data], query)
                    result["rationale"] = rationale
                except Exception as e:
                    result["rationale"] = f"Standard retrieved for: {query}"
                
                results.append(result)
        
        return results if results else None
    except Exception as e:
        print(f"[✗] Search error: {str(e)}")
        return None


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the BIS Finder web UI."""
    return render_template("index.html")


@app.route("/api/search", methods=["POST"])
def api_search():
    """
    API endpoint for BIS standard search.

    Request JSON:  { "query": "your search text" }
    Response JSON: { "results": [...], "query": "...", "count": N, "latency": X.XXX }
    
    Uses real backend if model loaded, falls back to demo if not available.
    """
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Query cannot be empty."}), 400

    t_start = time.perf_counter()

    # ─── Try real search first, fallback to demo ────────────────────────────
    if MODEL_LOADED and MODEL_DATA:
        results = real_search(query, top_k=5)
    else:
        results = None
    
    # ─── Fallback to demo search ─────────────────────────────────────────────
    if results is None:
        results = demo_search(query, top_k=5)
        fallback = True
    else:
        fallback = False

    latency = round(time.perf_counter() - t_start, 4)

    return jsonify({
        "query": query,
        "count": len(results),
        "results": results,
        "latency": latency,
        "backend": "demo" if fallback else "real",
        "model_status": "loaded" if MODEL_LOADED else ("error: " + MODEL_ERROR if MODEL_ERROR else "initializing"),
    })


@app.route("/api/status", methods=["GET"])
def api_status():
    """Return system status for debugging."""
    status = {
        "model_loaded": MODEL_LOADED,
        "model_error": MODEL_ERROR,
    }
    if MODEL_DATA:
        status["chunks_count"] = len(MODEL_DATA['chunks'])
        status["vocab_size"] = len(MODEL_DATA['vectorizer'].vocabulary_)
    return jsonify(status)


# ─── Error handlers ──────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔍 BIS Standards RAG System - Web Interface")
    print("="*70)
    
    # ─── Load model at startup (Rule B-2) ────────────────────────────────
    init_model()
    
    print("\n[*] Starting Flask server...")
    print("    URL: http://localhost:5000")
    print("    Press Ctrl+C to stop\n")
    
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
