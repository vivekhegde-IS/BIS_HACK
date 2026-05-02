# Person A — Backend Pipeline Tasks & Responsibilities

**Role**: AI-Assisted Backend Developer  
**Primary Focus**: PDF Ingestion → Indexing → Retrieval → Inference  
**Partner**: Person B (Infrastructure & UI)

---

## 🎯 Your Mission

Convert BIS SP 21 (929-page PDF with 600+ Indian Standards specifications) into a searchable, ranked index. Deliver a command-line tool (`inference.py`) that processes queries and returns top-5 matching standards with < 5 second latency per query.

**Success = Hit Rate ≥ 0.80 + MRR ≥ 0.74 + Latency < 5s**

---

## 📊 The Data Pipeline You Must Build

```
BIS_SP_21.pdf (organizers provide)
         ↓
    [pdftotext command]
         ↓
BIS_SP_21.txt (intermediate, DO NOT COMMIT)
         ↓
    src/ingest.py
         ↓
data/chunks.json (600+ entries, COMMIT this)
         ↓
    src/indexer.py
         ↓
data/tfidf_model.pkl (10-50 MB, MUST COMMIT this)
         ↓
    src/retriever.py (+ query expansion)
         ↓
    inference.py (judges run this)
         ↓
data/public_results.json (output, COMMIT this)
```

---

## 🔧 Component 1: Ingest (src/ingest.py)

### What It Does
Reads the plain-text conversion of the BIS PDF, extracts individual standard entries, and saves them to a structured JSON file.

### Input
- `BIS_SP_21.txt` — Text file from running: `pdftotext BIS_SP_21.pdf BIS_SP_21.txt`

### Output
- `data/chunks.json` — Array of 500+ standard entries, each with:
  ```json
  {
    "id":    "IS 269: 1989",
    "title": "ORDINARY PORTLAND CEMENT",
    "text":  "IS 269: 1989 ORDINARY PORTLAND CEMENT Specification ... [full description]"
  }
  ```

### Key Extraction Logic

The BIS PDF follows a pattern:
```
IS 269: 1989
    ORDINARY PORTLAND CEMENT — SPECIFICATION
    Scope: Covers the requirements for ordinary portland cement (33/43/53 grades)
    Chemical Requirements:
        - Silica (SiO2): ≥ 17%, ≤ 25%
        - Lime: ...
    Physical Requirements: ...
    ... (600-1500 characters of specs)

IS 455: 1989
    PORTLAND SLAG CEMENT — SPECIFICATION
    ...
```

### Extraction Strategy

```python
import re, json

def extract_standards(txt_path):
    with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    
    # Pattern: "IS XXX: YYYY" or "IS XXX (Part Y): YYYY"
    pattern = r'(IS\s+\d+(?:\s*\(Part\s+\d+\))?\s*:\s*\d{4})'
    
    # Split text by the pattern, keeping the delimiters
    parts = re.split(pattern, text)
    
    chunks = []
    i = 1  # Start at 1 to skip text before first standard
    while i < len(parts) - 1:
        is_id = parts[i].strip()  # e.g., "IS 269: 1989"
        body = parts[i+1].strip()[:2000]  # Next 2000 chars are the description
        
        # Extract title (first capitalized phrase)
        title_match = re.search(r'([A-Z][A-Z\s/,-]{5,80}?(?:\s+—|:|\n))', body)
        title = title_match.group(1).strip() if title_match else is_id
        
        chunks.append({
            "id": is_id,
            "title": title,
            "text": f"{is_id} {title} {body}"
        })
        
        i += 2
    
    return chunks

if __name__ == "__main__":
    chunks = extract_standards("BIS_SP_21.txt")
    with open("data/chunks.json", "w") as f:
        json.dump(chunks, f, indent=2)
    print(f"✓ Extracted {len(chunks)} standards")
    
    # Verify
    if len(chunks) < 500:
        print(f"⚠️  Warning: Only {len(chunks)} standards. Expected 500+")
```

### Success Criteria for Ingest
- [ ] Extracts ≥ 500 standards (ideally 600+)
- [ ] Each entry has: `id`, `title`, `text` (no missing keys)
- [ ] `id` format is consistent: `"IS XXX: YYYY"` or `"IS XXX (Part Y): YYYY"`
- [ ] No duplicates in `id` field
- [ ] Each `text` is at least 200 characters (not empty)

### Testing ingest.py

```bash
# Before converting PDF, ensure pdftotext is installed
# macOS: brew install xpdf
# Ubuntu: sudo apt-get install xpdf
# Windows: download from https://www.xpdfreader.com/

# Convert PDF
pdftotext BIS_SP_21.pdf BIS_SP_21.txt

# Run ingest
python src/ingest.py

# Verify output
python -c "
import json
chunks = json.load(open('data/chunks.json'))
print(f'Total standards: {len(chunks)}')
print('Sample:', chunks[0])
"
```

---

## 🔍 Component 2: Indexer (src/indexer.py)

### What It Does
Reads `chunks.json` and builds a TF-IDF (Term Frequency–Inverse Document Frequency) index using scikit-learn. This index enables fast cosine similarity search.

### Input
- `data/chunks.json` — 500+ chunk entries

### Output
- `data/tfidf_model.pkl` — Serialized pickle file containing:
  - The TfidfVectorizer (transformer)
  - The sparse matrix (actual index)
  - The chunks list (for result mapping)

### Why TF-IDF?
- Fast: Cosine similarity in dense vector space
- No GPU needed
- Works well for keyword-heavy domains like standards
- Scikit-learn is in requirements.txt

### Implementation

```python
import json, pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline

def build_index(chunks_path="data/chunks.json",
                output_path="data/tfidf_model.pkl"):
    
    # Load chunks
    with open(chunks_path) as f:
        chunks = json.load(f)
    
    # Extract texts
    texts = [chunk["text"] for chunk in chunks]
    
    # Build TF-IDF vectorizer
    # ngram_range=(1,2): capture both individual words AND bigrams (e.g., "Portland cement")
    # min_df=1: keep even rare terms
    # sublinear_tf=True: apply sublinear term frequency scaling
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
        lowercase=True,
        stop_words='english'
    )
    
    # Build the matrix
    matrix = vectorizer.fit_transform(texts)
    
    # Save everything to one pickle
    index_data = {
        "vectorizer": vectorizer,
        "matrix": matrix,
        "chunks": chunks
    }
    
    with open(output_path, "wb") as f:
        pickle.dump(index_data, f)
    
    print(f"✓ Index built: {matrix.shape[0]} docs, {matrix.shape[1]} features")
    print(f"✓ Saved to {output_path}")

if __name__ == "__main__":
    build_index()
```

### Success Criteria for Indexer
- [ ] TfidfVectorizer builds without errors
- [ ] Sparse matrix has ≥ 500 rows (docs) and ≥ 1000 columns (terms)
- [ ] Pickle file is created and > 1 MB (proves model is saved)
- [ ] Pickle file loads correctly: `pickle.load(open('data/tfidf_model.pkl', 'rb'))`

### Testing indexer.py

```bash
python src/indexer.py

# Verify pickle is valid
python -c "
import pickle
index = pickle.load(open('data/tfidf_model.pkl', 'rb'))
print(f\"Vectorizer: {index['vectorizer']}\")
print(f\"Matrix shape: {index['matrix'].shape}\")
print(f\"Chunks: {len(index['chunks'])} entries\")
"
```

---

## 🎯 Component 3: Retriever (src/retriever.py)

### What It Does
Loads the TF-IDF index and retrieves the top-5 standards for a given query. It also expands queries with synonyms to improve relevance.

### Input
- `data/tfidf_model.pkl` — Saved index
- Natural language query (e.g., "What standard covers Portland cement?")

### Output
- Top-5 IS standard IDs ranked by relevance (e.g., `["IS 269: 1989", "IS 455: 1989", ...]`)

### Key Feature: Query Expansion

Not all users say "Portland cement" — some say "slag," "fly ash," "pozzolana," etc. The SYNONYMS dictionary expands queries to boost recall.

```python
SYNONYMS = {
    "slag":      "portland slag",
    "pozzolana": "fly ash calcined clay",
    "aggregate": "coarse fine gravel",
    "lime":      "building lime quicklime",
    "cement":    "ordinary portland",
    "plywood":   "wood panel board",
    "brick":     "masonry fired clay",
    "pipe":      "tube conduit drainage",
    "steel":     "iron structural metal",
    "tile":      "ceramic floor wall",
    "paint":     "coating surface primer",
    "wire":      "conductor cable electrical",
    "block":     "masonry hollow solid",
    "sand":      "fine aggregate natural",
}
```

### Implementation

```python
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

SYNONYMS = {
    # ... (see above)
}

def expand_query(query: str) -> str:
    """Expand query with synonyms to improve recall."""
    q = query.lower()
    for keyword, expansion in SYNONYMS.items():
        if keyword in q:
            q = q + " " + expansion
    return q

def load_index(path="data/tfidf_model.pkl"):
    """Load the TF-IDF index from disk."""
    with open(path, "rb") as f:
        return pickle.load(f)

def retrieve(query: str, index: dict, top_k: int = 5) -> list:
    """
    Retrieve top-k standards for a query.
    
    Args:
        query: Natural language query (e.g., "Portland cement requirements")
        index: Loaded index (dict with vectorizer, matrix, chunks)
        top_k: Number of results to return
    
    Returns:
        List of top_k standard IDs (e.g., ["IS 269: 1989", ...])
    """
    # Expand query with synonyms
    expanded = expand_query(query)
    
    # Vectorize expanded query
    query_vec = index["vectorizer"].transform([expanded])
    
    # Compute cosine similarity with all documents
    scores = cosine_similarity(query_vec, index["matrix"])[0]
    
    # Get indices of top-k highest scoring documents
    top_indices = np.argsort(scores)[::-1][:top_k]
    
    # Map indices back to standard IDs
    result_ids = [index["chunks"][i]["id"] for i in top_indices]
    
    return result_ids

if __name__ == "__main__":
    # Test retrieval
    index = load_index()
    
    test_queries = [
        "Portland cement requirements",
        "Coarse aggregate for concrete",
        "Ceramic floor tiles",
        "Steel bars for construction"
    ]
    
    for q in test_queries:
        results = retrieve(q, index)
        print(f"\nQuery: {q}")
        print(f"Results: {results[:3]}")
```

### Success Criteria for Retriever
- [ ] load_index() returns a dict with `vectorizer`, `matrix`, `chunks`
- [ ] retrieve() always returns a list of exactly 5 items (padding with last result if needed)
- [ ] All returned IDs are real (no hallucinations, all come from chunks.json)
- [ ] SYNONYMS dictionary is present and used in expand_query()

### Testing retriever.py

```bash
# Minimal test
python -c "
from src.retriever import load_index, retrieve

index = load_index('data/tfidf_model.pkl')
results = retrieve('cement', index)
print(f'Top 5 for cement: {results}')
assert len(results) == 5
assert all(isinstance(r, str) for r in results)
print('✓ Retriever works')
"
```

---

## ⚡ Component 4: Inference (inference.py)

### What It Does
This is the **entry point judges run**. It loads the index once, processes all queries from a test set file, and outputs ranked results with latency measurements.

### Command Judges Run

```bash
python inference.py \
  --input data/public_test_set.json \
  --output data/public_results.json
```

### Input Format (`data/public_test_set.json`)

```json
[
  {
    "id": "PUB-01",
    "query": "We manufacture 33 Grade Ordinary Portland Cement. What standard covers requirements?"
  },
  {
    "id": "PUB-02",
    "query": "Coarse and fine aggregates for structural concrete..."
  }
]
```

### Output Format (`data/public_results.json`)

```json
[
  {
    "id": "PUB-01",
    "retrieved_standards": [
      "IS 269: 1989",
      "IS 8112: 1989",
      "IS 12269: 1987",
      "IS 455: 1989",
      "IS 1489 (Part 1): 1991"
    ],
    "latency_seconds": 0.0234
  }
]
```

### Critical Implementation

```python
import argparse, json, time, sys
sys.path.insert(0, "src")  # Allow importing from src/

from retriever import load_index, retrieve

def main():
    parser = argparse.ArgumentParser(
        description="BIS Standards Inference Pipeline"
    )
    parser.add_argument("--input", required=True, help="Input test set JSON")
    parser.add_argument("--output", required=True, help="Output results JSON")
    args = parser.parse_args()
    
    # CRITICAL: Load index ONCE before loop
    print("[1/3] Loading TF-IDF index...")
    index = load_index("data/tfidf_model.pkl")
    print(f"     ✓ Index loaded: {index['matrix'].shape[0]} docs")
    
    # Load test queries
    print("[2/3] Loading test queries...")
    with open(args.input) as f:
        queries = json.load(f)
    print(f"     ✓ {len(queries)} queries loaded")
    
    # Process each query
    print("[3/3] Processing queries...")
    results = []
    
    for i, item in enumerate(queries, 1):
        # Measure latency
        t0 = time.time()
        retrieved = retrieve(item["query"], index, top_k=5)
        elapsed = time.time() - t0
        
        # Ensure exactly 5 results
        while len(retrieved) < 5:
            retrieved.append(retrieved[-1])
        retrieved = retrieved[:5]
        
        # Build result
        result = {
            "id": item["id"],
            "retrieved_standards": retrieved,
            "latency_seconds": round(elapsed, 4)
        }
        results.append(result)
        
        if i % 5 == 0:
            print(f"     {i}/{len(queries)} queries processed")
    
    # Save results
    print(f"[4/4] Saving results to {args.output}...")
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"✓ Done! Processed {len(results)} queries")
    print(f"  Average latency: {sum(r['latency_seconds'] for r in results) / len(results):.4f}s")

if __name__ == "__main__":
    main()
```

### Critical Rules (DO NOT VIOLATE)

🔴 **RULE-A1**: inference.py must be at REPO ROOT, not inside /src

🔴 **RULE-A2**: Output JSON keys MUST be exactly:
- `id` (not `query_id`, not `standard_id`)
- `retrieved_standards` (not `results`, not `standards`)
- `latency_seconds` (not `latency`, not `time`)

🔴 **RULE-A3**: Load index BEFORE the loop, never inside it

🔴 **RULE-A4**: Always return exactly 5 items (pad with last result if fewer retrieved)

🔴 **RULE-A5**: Never hallucinate IS codes — all must come from chunks.json

### Testing inference.py

```bash
# Full inference + eval pipeline
python inference.py --input data/public_test_set.json --output data/public_results.json

# Then run eval (see Component 5)
python eval_script.py --results data/public_results.json
```

---

## 📊 Component 5: Evaluation (eval_script.py)

### What It Does
Judges run this to score your submission. It compares your retrieved standards against ground truth and computes three metrics:

- **Hit Rate @3**: % of queries where at least 1 correct standard appears in top-3
- **MRR @5**: Mean Reciprocal Rank (average of 1/position of first correct standard in top-5)
- **Latency**: Average seconds per query

### The Scoring Formula

```
Hit Rate @3 = (# queries with ≥1 match in top-3) / total_queries
              Target: ≥ 0.80 (80%)

MRR @5 = Average of:
  - For each query, if correct standard is at position 1: add 1.0
  - If at position 2: add 0.5
  - If at position 3: add 0.333
  - If at position 4: add 0.25
  - If at position 5: add 0.2
  - If not in top-5: add 0.0
              Target: ≥ 0.74

Latency = Average of latency_seconds across all queries
          Target: < 5.0 seconds
```

### Example Output

```
========================================
   BIS HACKATHON EVALUATION RESULTS
========================================
Total Queries Evaluated : 10
Hit Rate @3             : 0.90 (90%)     ✓ Target: >80%
MRR @5                  : 0.85           ✓ Target: >0.74
Avg Latency             : 0.45 sec       ✓ Target: <5 sec
========================================
```

### Your Task
You do NOT write eval_script.py — organizers provide it. You just:

1. Run it after inference.py completes
2. Review the metrics
3. Optimize if scores are low
4. Commit and push the results

### How to Run Evaluation

```bash
# Full workflow
python inference.py --input data/public_test_set.json --output data/public_results.json
python eval_script.py --results data/public_results.json

# Or just the eval (if output file already exists)
python eval_script.py --results data/public_results.json
```

---

## 📈 Optimization Tips for Better Scores

### If Hit Rate is Low (< 0.80)

**Problem**: Your retriever isn't finding the correct standards.

**Solutions**:
1. Improve query expansion: Add more synonym pairs to SYNONYMS dict
2. Check chunking: Are chunks too short or too long? (Target: 500-1500 chars)
3. Verify ingest: Are all 600+ standards actually extracted?
4. Tweak TfidfVectorizer: Try different ngram_range or min_df values
   - Test: `ngram_range=(1,3)` for trigrams
   - Test: `min_df=2` to ignore very rare terms

### If MRR is Low (< 0.74)

**Problem**: Correct standards are found, but not in top positions.

**Solutions**:
1. Expand SYNONYMS: More keywords = better ranking
2. Increase term frequency weight: `sublinear_tf=True` (already in code)
3. Increase bigram contribution: `ngram_range=(1,3)` captures more context
4. Manually review: Look at queries where correct answer is at position 4-5. Why?

### If Latency is High (> 5s per query)

**Problem**: Inference is slow.

**Solutions**:
1. Check memory: Is the sparse matrix too large?
2. Profile: Time each step (load, vectorize, similarity, sort)
3. Ensure: Load index only ONCE before loop (not inside)
4. Cache: Pre-compute expansions? (unlikely to help much)
5. Hardware: More RAM helps, but not critical

---

## 🔄 Git Workflow for Person A

### Before Your First Push

```bash
# 1. Create all files locally
#    src/ingest.py
#    src/indexer.py
#    src/retriever.py
#    inference.py

# 2. Test the pipeline
python src/ingest.py
python src/indexer.py
python inference.py --input data/public_test_set.json --output data/public_results.json
python eval_script.py --results data/public_results.json

# 3. Verify metrics
#    Hit Rate ≥ 0.80?
#    MRR ≥ 0.74?
#    Latency < 5s?

# 4. Commit (never use "git add .")
git add src/ingest.py src/indexer.py src/retriever.py inference.py
git add data/chunks.json data/tfidf_model.pkl data/public_results.json
git diff --cached  # Review before committing

# 5. Commit with clear message
git commit -m "Add pipeline: ingest, indexer, retriever, inference"

# 6. Get Person B's changes
git pull origin main

# 7. Push to repo
git push origin main
```

### For Subsequent Pushes

```bash
# After any changes:
git status                                    # What changed?
git diff HEAD                                 # Review changes
git add <files by name, not ".">              # Never use "git add ."
git diff --cached                             # Review before commit
git commit -m "Improve query expansion: added 3 new synonyms"
git pull origin main                          # Get updates
git push origin main                          # Push your changes
```

### Files You Must Commit (Person A Responsibility)

| File | Status | Reason |
|------|--------|--------|
| src/ingest.py | COMMIT | Your code |
| src/indexer.py | COMMIT | Your code |
| src/retriever.py | COMMIT | Your code |
| inference.py | COMMIT | Your code |
| data/chunks.json | COMMIT | Generated output, 500+ entries |
| data/tfidf_model.pkl | COMMIT | Generated index, required for running |
| data/public_results.json | COMMIT | Your submission output |
| BIS_SP_21.txt | .gitignore | Intermediate, 100+ MB |
| BIS_SP_21.pdf | .gitignore | Original input, licensing |

---

## ✅ Pre-Submission Checklist

Before your final push, verify:

- [ ] `python src/ingest.py` → outputs "Extracted 500+ chunks"
- [ ] `python src/indexer.py` → outputs "Index built: 5XX docs"
- [ ] `python inference.py --input data/public_test_set.json --output data/public_results.json` → completes in < 60s
- [ ] `python eval_script.py --results data/public_results.json` → Hit Rate ≥ 0.80, MRR ≥ 0.74
- [ ] `git ls-files | grep -E "\.pkl|\.json|\.py" | wc -l` → at least 10 files tracked
- [ ] `git ls-files | grep -E "\.pdf|\.txt"` → returns nothing (PDFs not committed)
- [ ] `git ls-files | grep "__pycache__"` → returns nothing (cache not committed)

---

## 📚 Data Sources & Attribution

| Data | Source | Purpose | License |
|------|--------|---------|---------|
| BIS SP 21 (PDF) | Organizers | Official BIS Standards | Use for parsing only |
| public_test_set.json | Organizers | Test queries | Read-only, don't modify |
| chunks.json | YOU generate | Intermediate | Generated |
| tfidf_model.pkl | YOU generate | Index | Generated |
| public_results.json | YOU generate | Submission | Generated |

---

**Last Updated**: May 2026  
**Status**: Active Development  
**Role**: Person A (Backend Pipeline)
