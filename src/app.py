#!/usr/bin/env python3
"""
Component: Flask Web UI
Web interface for BIS Standards Finder

Usage:
    python src/app.py
    # Open: http://localhost:5000
"""

import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder="templates")

# ---------------------------------------------------------------------------
# DEMO DATA — 12 real BIS standards with full descriptions
# ---------------------------------------------------------------------------
DEMO_BIS_DB = [
    {
        "id": "IS 269: 1989",
        "title": "Ordinary Portland Cement, 33 Grade — Specification",
        "category": "Cement",
        "description": (
            "This standard specifies the chemical composition, physical properties, "
            "and testing procedures for 33 Grade Ordinary Portland Cement (OPC). "
            "It covers requirements for fineness, setting time, soundness, and "
            "compressive strength. Widely used in general construction, plastering, "
            "and non-structural concrete work."
        ),
        "tags": ["cement", "portland", "ordinary", "concrete", "construction", "33 grade"],
    },
    {
        "id": "IS 383: 1970",
        "title": "Coarse and Fine Aggregates from Natural Sources for Concrete",
        "category": "Aggregates",
        "description": (
            "Specifies grading requirements, physical properties, and deleterious "
            "substance limits for coarse and fine aggregates sourced from natural "
            "deposits. Applicable to all structural concrete grades. Covers sieve "
            "analysis, bulk density, moisture content, and soundness tests."
        ),
        "tags": ["aggregates", "concrete", "natural", "coarse", "fine", "structural"],
    },
    {
        "id": "IS 458: 2003",
        "title": "Precast Concrete Pipes (with and without Reinforcement)",
        "category": "Pipes",
        "description": (
            "Governs the manufacture, dimensions, and testing of precast concrete "
            "pipes used for water mains, sewers, and drainage systems. Covers both "
            "plain and reinforced variants. Specifies hydraulic pressure tests, "
            "crushing strength, and jointing requirements."
        ),
        "tags": ["pipes", "precast", "concrete", "water", "reinforcement", "sewage"],
    },
    {
        "id": "IS 2185 (Part 2): 1983",
        "title": "Concrete Masonry Units — Hollow and Solid Lightweight Concrete Blocks",
        "category": "Masonry",
        "description": (
            "Defines dimensional tolerances, minimum compressive strength, and water "
            "absorption limits for hollow and solid lightweight concrete masonry blocks. "
            "Used in load-bearing and non-load-bearing walls. Promotes energy-efficient "
            "construction with reduced dead load."
        ),
        "tags": ["masonry", "blocks", "lightweight", "hollow", "solid", "concrete"],
    },
    {
        "id": "IS 459: 1992",
        "title": "Corrugated and Semi-Corrugated Asbestos Cement Sheets",
        "category": "Roofing",
        "description": (
            "Covers the manufacture, dimensions, and performance requirements for "
            "corrugated and semi-corrugated asbestos cement roofing and cladding sheets. "
            "Specifies transverse load, impermeability, and moisture movement tests "
            "applicable to industrial and agricultural building roofs."
        ),
        "tags": ["roofing", "asbestos", "cement", "sheets", "corrugated", "cladding"],
    },
    {
        "id": "IS 455: 1989",
        "title": "Portland Slag Cement — Specification",
        "category": "Cement",
        "description": (
            "Specifies requirements for Portland slag cement produced by intergrinding "
            "Portland cement clinker and granulated blast furnace slag. Offers improved "
            "resistance to sulphate attack and reduced heat of hydration, making it "
            "suitable for mass concrete, marine structures, and foundations."
        ),
        "tags": ["cement", "slag", "portland", "construction", "marine", "sulphate"],
    },
    {
        "id": "IS 1489 (Part 2): 1991",
        "title": "Portland Pozzolana Cement — Calcined Clay Based",
        "category": "Cement",
        "description": (
            "Covers calcined clay-based Portland pozzolana cement, specifying its "
            "composition, physical properties, and chemical requirements. Offers "
            "lower heat of hydration and enhanced workability. Commonly used in "
            "hydraulic structures, large foundations, and tropical climates."
        ),
        "tags": ["cement", "pozzolana", "calcined", "clay", "portland", "hydraulic"],
    },
    {
        "id": "IS 3466: 1988",
        "title": "Masonry Cement — Specification",
        "category": "Cement",
        "description": (
            "Defines requirements for masonry cement used in mortar for brickwork, "
            "blockwork, and plastering. Not intended for structural concrete. "
            "Provides superior workability and water retention compared to OPC, "
            "improving adhesion and reducing shrinkage cracks in masonry joints."
        ),
        "tags": ["cement", "masonry", "mortar", "general", "brickwork", "plaster"],
    },
    {
        "id": "IS 6909: 1990",
        "title": "Supersulphated Cement — Specification",
        "category": "Cement",
        "description": (
            "Specifies composition and testing of supersulphated cement, manufactured "
            "from granulated blast furnace slag, calcium sulphate, and Portland cement "
            "clinker. Exhibits high resistance to sulphate attack and aggressive water "
            "conditions — ideal for marine works, sewage, and chemical plant foundations."
        ),
        "tags": ["cement", "supersulphated", "marine", "aggressive", "water", "slag"],
    },
    {
        "id": "IS 8042: 1989",
        "title": "White Portland Cement — Specification",
        "category": "Cement",
        "description": (
            "Covers physical and chemical requirements for white Portland cement "
            "produced from raw materials low in iron and manganese oxides. Used "
            "primarily in architectural, decorative, and terrazzo work where colour "
            "consistency is essential. Meets the same strength class as OPC."
        ),
        "tags": ["cement", "white", "portland", "architectural", "decorative", "terrazzo"],
    },
    {
        "id": "IS 8112: 1989",
        "title": "Ordinary Portland Cement, 43 Grade — Specification",
        "category": "Cement",
        "description": (
            "Specifies the 43 Grade OPC, widely used in high-performance reinforced "
            "concrete structures, pre-cast elements, and precast prestressed concrete. "
            "Achieves minimum 43 MPa at 28 days. Balances strength and workability "
            "for most structural concrete applications."
        ),
        "tags": ["cement", "portland", "43 grade", "high strength", "concrete", "precast"],
    },
    {
        "id": "IS 12269: 1987",
        "title": "Ordinary Portland Cement, 53 Grade — Specification",
        "category": "Cement",
        "description": (
            "Defines the highest OPC grade (53 MPa at 28 days) for demanding structural "
            "applications including high-rise buildings, bridges, flyovers, and "
            "prestressed concrete. Requires stricter quality control. Generates higher "
            "heat of hydration — needs careful curing in mass concrete applications."
        ),
        "tags": ["cement", "portland", "53 grade", "prestressed", "high-rise", "bridge"],
    },
]


def demo_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Demo keyword-based search over DEMO_BIS_DB.

    ── REPLACE THIS FUNCTION ────────────────────────────────────────────────
    Swap the body below with a call to the real RAG retriever, e.g.:
        from retriever import retrieve
        return retrieve(query, top_k=top_k)
    ─────────────────────────────────────────────────────────────────────────
    """
    query_tokens = set(query.lower().split())
    scored = []
    for entry in DEMO_BIS_DB:
        searchable = " ".join([
            entry["title"].lower(),
            entry["description"].lower(),
            " ".join(entry["tags"]),
        ])
        score = sum(1 for token in query_tokens if token in searchable)
        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored[:top_k]]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Serve the BIS Finder web UI."""
    return render_template("index.html")


@app.route("/api/search", methods=["POST"])
def api_search():
    """
    API endpoint for BIS standard search.

    Request JSON:  { "query": "your search text" }
    Response JSON: { "results": [...], "query": "...", "count": N, "response_time": X.XXX }
    """
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Query cannot be empty."}), 400

    t_start = time.perf_counter()

    # ── REAL SEARCH HOOK ──────────────────────────────────────────────────
    # When the actual retriever is ready, replace demo_search() with:
    #   from retriever import retrieve
    #   results = retrieve(query, top_k=5)
    # ─────────────────────────────────────────────────────────────────────
    results = demo_search(query, top_k=5)

    elapsed = round(time.perf_counter() - t_start, 3)

    return jsonify({
        "query": query,
        "count": len(results),
        "results": results,
        "response_time": elapsed,
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
