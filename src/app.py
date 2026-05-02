#!/usr/bin/env python3
"""
Component: Flask Web UI (Backend API)
Serves the BIS Standards RAG System as a REST API.

Deployment:
  - Backend  → Render  (gunicorn "src.app:create_app()")
  - Frontend → Vercel  (frontend/index.html)

Routes:
  GET  /api/status   — health check
  POST /api/search   — main search endpoint

CORS: Allowed origins are configured via FRONTEND_URL env var.
"""

import time
import sys
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# ─── Load env from .env file (local dev only; Render injects vars directly) ──
load_dotenv()

# ─── Add project root to Python path ─────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent / ".."))

# ─── Import backend modules ───────────────────────────────────────────────────
from src.retriever import retrieve, load_model_once
from src.rationale import generate_rationale

# ─── Global state (shared across requests within one worker) ─────────────────
MODEL_LOADED = False
MODEL_ERROR  = None
MODEL_DATA   = None

# ─── DEMO DATA (fallback if model not available) ─────────────────────────────
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
    Load TF-IDF model once at startup (NOT per-request).
    Rule B-2: Model must be loaded outside request handlers.
    """
    global MODEL_LOADED, MODEL_ERROR, MODEL_DATA
    try:
        print("[*] Initializing BIS Standards RAG System...")
        MODEL_DATA   = load_model_once()
        MODEL_LOADED = True
        print("[+] TF-IDF model loaded successfully")
        print(f"    Standards : {len(MODEL_DATA['chunks'])}")
        print(f"    Vocabulary: {len(MODEL_DATA['vectorizer'].vocabulary_)}")
        return True
    except FileNotFoundError as e:
        MODEL_ERROR = f"Model not found: {str(e)}"
        print(f"[-] {MODEL_ERROR}")
        print("    Hint: Run:  python src/ingest.py  &&  python src/indexer.py")
        return False
    except Exception as e:
        MODEL_ERROR = f"Model load error: {str(e)}"
        print(f"[-] {MODEL_ERROR}")
        return False


def demo_search(query: str, top_k: int = 5):
    """Keyword fallback search over DEMO_BIS_DB."""
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
    """TF-IDF search (or fallback) with LLM-generated rationales."""
    try:
        if MODEL_LOADED and MODEL_DATA:
            retrieved_ids = retrieve(query, top_k=top_k)
            chunks = MODEL_DATA["chunks"]
            selected_chunks = []
            for std_id in retrieved_ids:
                for chunk in chunks:
                    if chunk.get("standard") == std_id:
                        selected_chunks.append(chunk)
                        break
        else:
            selected_chunks = demo_search(query, top_k=top_k)
            # Map 'id' to 'standard' for compatibility with rationale.py
            for c in selected_chunks:
                if 'standard' not in c:
                    c['standard'] = c['id']
            
        rationales = generate_rationale(selected_chunks, query)

        results = []
        for i, chunk in enumerate(selected_chunks):
            rat_text = rationales[i] if i < len(rationales) else f"Standard retrieved for: {query}"
            results.append({
                "id":          chunk.get("standard", chunk.get("id")),
                "title":       chunk.get("title", chunk.get("standard")),
                "description": chunk.get("description", ""),
                "rationale":   rat_text,
            })
        return results if results else None
    except Exception as e:
        print(f"[-] Search error: {str(e)}")
        # Ultimate fallback
        return demo_search(query, top_k=top_k)


# ─── Application factory ──────────────────────────────────────────────────────
def create_app():
    """
    Flask application factory.
    Gunicorn on Render calls this as:  gunicorn "src.app:create_app()"
    """
    app = Flask(__name__, template_folder="templates")

    # ── CORS: allow all origins since this is a public search API ──────────────
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Load model at factory time (once per worker process) ─────────────────
    init_model()

    # ── Routes ────────────────────────────────────────────────────────────────

    @app.route("/")
    def index():
        """Serve the built-in UI (useful for local dev / Render preview)."""
        return render_template("index.html")

    @app.route("/api/search", methods=["POST"])
    def api_search():
        """
        POST /api/search
        Body:     { "query": "..." }
        Response: { "results": [...], "query": "...", "count": N, "latency": X.XXX, "backend": "real|demo" }
        """
        data  = request.get_json(silent=True) or {}
        query = data.get("query", "").strip()

        if not query:
            return jsonify({"error": "Query cannot be empty."}), 400

        t_start = time.perf_counter()

        results = real_search(query, top_k=5)
        if results is None:
            results = demo_search(query, top_k=5)
            fallback = True
        else:
            # We don't necessarily know if it was fallback internally, but it has rationales now!
            fallback = False

        latency = round(time.perf_counter() - t_start, 4)

        return jsonify({
            "query":        query,
            "count":        len(results),
            "results":      results,
            "latency":      latency,
            "backend":      "demo" if fallback else "real",
            "model_status": "loaded" if MODEL_LOADED else ("error: " + MODEL_ERROR if MODEL_ERROR else "initializing"),
        })

    @app.route("/api/status", methods=["GET"])
    def api_status():
        """GET /api/status — health check / debugging."""
        status = {
            "model_loaded": MODEL_LOADED,
            "model_error":  MODEL_ERROR,
        }
        if MODEL_DATA:
            status["chunks_count"] = len(MODEL_DATA["chunks"])
            status["vocab_size"]   = len(MODEL_DATA["vectorizer"].vocabulary_)
        return jsonify(status)

    # ── Error handlers ────────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app


# ─── Local development entry point ───────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("[*] BIS Standards RAG System — Local Dev Server")
    print("=" * 70)
    print("    URL: http://localhost:5000")
    print("    Press Ctrl+C to stop\n")
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
