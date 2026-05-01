#!/usr/bin/env python3
"""
Component 4: Inference (PERSON A)
Main entry point for judges — MUST stay at root directory (./inference.py)

Usage:
    python inference.py --input public_test_set.json --output results.json

Output format (flat list, as expected by eval_script.py):
[
    {
        "id": "PUB-01",
        "query": "...",
        "expected_standards": ["IS 269: 1989"],
        "retrieved_standards": ["IS 269: 1989", "IS 8112: 1989", ...],
        "latency_seconds": 0.245
    },
    ...
]
"""

import json
import time
import argparse
import sys
import os
from pathlib import Path

# Add src/ to Python path so retriever can be imported
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from retriever import retrieve, load_model_once   # noqa: E402


def run_inference(input_path: str, output_path: str) -> list:
    """
    Run full inference pipeline on all queries.

    Args:
        input_path:  Path to input JSON (list of {id, query, expected_standards})
        output_path: Path to write output JSON (flat list)

    Returns:
        List of result dicts.
    """
    # ── Load queries ──────────────────────────────────────────────────────────
    print(f"\n[1/3] Loading queries from '{input_path}' ...")
    with open(input_path, 'r', encoding='utf-8') as f:
        queries = json.load(f)
    print(f"      {len(queries)} queries loaded.")

    # ── Load model ONCE before the loop (Rule A-3) ───────────────────────────
    print("[2/3] Loading TF-IDF model (once) ...")
    load_model_once()
    print("      Model ready.")

    # ── Run retrieval loop ────────────────────────────────────────────────────
    print(f"[3/3] Running inference on {len(queries)} queries ...")
    results = []

    for i, item in enumerate(queries, start=1):
        query_id   = item.get('id', f'Q-{i}')
        query_text = item.get('query', '')
        expected   = item.get('expected_standards', [])

        # Measure per-query latency
        t0 = time.perf_counter()
        retrieved = retrieve(query_text, top_k=5)   # Always 5 (Rule A-4)
        latency   = round(time.perf_counter() - t0, 4)

        print(f"  [{i:2d}/{len(queries)}] {query_id:10s} | {latency:.3f}s | top={retrieved[0]}")

        results.append({
            "id":                  query_id,
            "query":               query_text,
            "expected_standards":  expected,
            "retrieved_standards": retrieved,     # Exactly 5 strings (Rule A-4)
            "latency_seconds":     latency,
        })

    # ── Save output ───────────────────────────────────────────────────────────
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    avg_lat = sum(r['latency_seconds'] for r in results) / len(results)
    print(f"\n[+] Results saved to '{output_path}'")
    print(f"  Queries processed : {len(results)}")
    print(f"  Avg latency       : {avg_lat:.3f}s  (target: <5s)")
    print(f"\nNext: python eval_script.py --results {output_path}")

    return results


def main():
    """Main inference entry point (CLI)."""
    parser = argparse.ArgumentParser(
        description='BIS Standards RAG — Inference Pipeline'
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Path to input queries JSON file (e.g. public_test_set.json)',
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Path to write output results JSON file (e.g. results.json)',
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: Input file not found: '{args.input}'")
        sys.exit(1)

    run_inference(args.input, args.output)


if __name__ == "__main__":
    main()
