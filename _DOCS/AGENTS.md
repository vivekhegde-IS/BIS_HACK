# BIS Standards Recommendation Engine - Agent Instructions

## Project Overview

**BIS Standards Recommendation Engine** is a hackathon project building a **Retrieval-Augmented Generation (RAG) pipeline** to help users find the correct Bureau of Indian Standards (BIS) specifications based on natural language queries.

**Goal**: Given a query about manufacturing/compliance requirements, return the top-5 most relevant BIS standards ranked by relevance.

**Example**: 
- Query: *"We manufacture 33 Grade Ordinary Portland Cement. What standard covers requirements?"*
- Expected Output: `["IS 269: 1989", ...]`

---

## Quick Start for Agents

### Essential Commands

**Run Evaluation** (validates solution against test set):
```bash
python eval_script.py --results path/to/output.json
```

**Expected Output Format**:
```json
[
  {
    "id": "PUB-01",
    "query": "...",
    "expected_standards": ["IS 269: 1989"],
    "retrieved_standards": ["IS 269: 1989", "IS 8112: 1989", ...],
    "latency_seconds": 1.24
  }
]
```

### Success Metrics (Evaluation Targets)
- **Hit Rate @3**: ≥80% (correct standard in top-3 results)
- **MRR @5**: ≥0.70 (Mean Reciprocal Rank at top-5)
- **Avg Latency**: <5 seconds per query

---

## Key Files & Responsibilities

| File | Purpose | Mutability |
|------|---------|-----------|
| [public_test_set.json](public_test_set.json) | Test queries with ground-truth standards | Read-only |
| [sample_output.json](sample_output.json) | Reference output format (template for solutions) | Read-only |
| [eval_script.py](eval_script.py) | Evaluation script (computes Hit@3, MRR@5, latency) | Read-only |
| [dataset_bis.pdf](dataset_bis.pdf) | Complete BIS standards database (indexing source) | Read-only |
| [BIS Standards Recommendation Engine- Hackathon.pdf](BIS%20Standards%20Recommendation%20Engine-%20Hackathon.pdf) | Problem statement & full requirements | Reference |

### Implementation Responsibility
Participants must create: `submission.json` (or equivalent) in the format of [sample_output.json](sample_output.json)

---

## Data Format Conventions

### Input Format: [public_test_set.json](public_test_set.json)
```json
{
  "id": "PUB-01",                          // Unique identifier
  "query": "natural language question",    // User's query about BIS standards
  "expected_standards": ["IS XXX: YYYY"]   // Ground truth (1+ standards)
}
```

### Output Format: [sample_output.json](sample_output.json)
```json
{
  "id": "PUB-01",
  "query": "natural language question",
  "expected_standards": ["IS XXX: YYYY"],
  "retrieved_standards": [                 // Top-5 ranked results
    "IS 269: 1989",
    "IS 8112: 1989",
    "IS 12269: 1987",
    "IS 455: 1989",
    "IS 1489 (Part 1): 1991"
  ],
  "latency_seconds": 1.24                  // Float with 2 decimal precision
}
```

### BIS Standard Naming Convention
- **Format**: `IS XXX: YYYY` or `IS XXX (Part Y): YYYY`
- **Examples**:
  - `IS 269: 1989` (Ordinary Portland Cement)
  - `IS 2185 (Part 2): 1983` (Lightweight Concrete Masonry Blocks)
  - `IS 383: 1970` (Coarse and Fine Aggregates)

---

## Evaluation Logic (eval_script.py)

### Hit Rate @3
- **Calculation**: Percentage of queries where ≥1 expected standard appears in `retrieved_standards[:3]`
- **Formula**: `(# queries with hit) / total_queries × 100%`
- **Target**: >80%

### MRR @5 (Mean Reciprocal Rank)
- **Calculation**: Average of `1 / rank_of_first_correct_standard` for each query (top-5 only)
- **Formula**: `Σ(1 / first_match_position) / total_queries`
- **Target**: >0.70
- **Note**: Only the position of the *first* matching standard matters

### Avg Latency
- **Calculation**: Mean response time across all queries
- **Formula**: `Σ latency_seconds / total_queries`
- **Target**: <5 seconds
- **Note**: Loosely monitored; prioritize correctness over speed

### Normalization for Matching
The evaluator **normalizes** both expected and retrieved standards:
- Remove spaces: `"IS 269: 1989"` → `"IS269:1989"`
- Convert to lowercase: `"IS269:1989"` → `"is269:1989"`

This allows fuzzy matching across case/spacing variations.

---

## Architecture Insights

### System Type
Information Retrieval + Ranking (not necessarily ML-based)

### Typical Pipeline
1. **Indexing Phase**: Parse [dataset_bis.pdf](dataset_bis.pdf) → create searchable corpus
2. **Retrieval Phase**: Accept query → match against corpus → return top-5 ranked candidates
3. **Optimization**: Minimize latency while maximizing relevance

### Approach Options (Not Prescriptive)
- **Keyword-based**: TF-IDF, BM25
- **Semantic Search**: BERT embeddings, dense retrieval vectors
- **Hybrid**: Keyword + semantic ranking
- **LLM-based**: Language model with retrieval-augmented generation (RAG)

---

## Common Participant Tasks

### Task 1: Parse dataset_bis.pdf
Extract BIS standards database and create an indexable corpus.

**Pseudocode**:
```python
# Load dataset_bis.pdf
# Extract standard codes (IS XXX: YYYY format)
# Extract descriptions/scope
# Create searchable index
```

### Task 2: Implement Retriever
Given a query, return top-5 relevant standards.

**Signature**:
```python
def retrieve_standards(query: str) -> List[str]:
    # Return 5 standard codes ranked by relevance
    # Example: ["IS 269: 1989", "IS 8112: 1989", ...]
```

### Task 3: Batch Process Queries
Load [public_test_set.json](public_test_set.json), retrieve standards, measure latency, save to JSON.

**Pseudocode**:
```python
def process_queries(input_file, output_file):
    queries = json.load(open(input_file))
    results = []
    
    for query in queries:
        start = time.time()
        retrieved = retrieve_standards(query['query'])
        latency = time.time() - start
        
        results.append({
            'id': query['id'],
            'query': query['query'],
            'expected_standards': query['expected_standards'],
            'retrieved_standards': retrieved[:5],
            'latency_seconds': round(latency, 2)
        })
    
    json.dump(results, open(output_file, 'w'), indent=2)
    # Run evaluation
    evaluate_results(output_file)
```

### Task 4: Evaluate Solution
```bash
python eval_script.py --results your_submission.json
```

---

## Troubleshooting & Common Issues

### Issue: "Error reading results file"
**Cause**: Output JSON is malformed or missing required fields
**Fix**: Validate against [sample_output.json](sample_output.json) structure
- All queries must have: `id`, `query`, `expected_standards`, `retrieved_standards`, `latency_seconds`
- Ensure valid JSON syntax (trailing commas, quotes, etc.)

### Issue: Low Hit Rate @3
**Cause**: Retrieved standards don't match expected standards in top-3
**Fix**: 
- Improve retrieval ranking/relevance
- Ensure exact standard code matching (check normalization logic)
- Consider semantic similarity if keyword matching is insufficient

### Issue: High Latency (>5 seconds)
**Cause**: Inefficient indexing or retrieval
**Fix**:
- Profile the retrieval step
- Consider pre-computed embeddings or cached indices
- Optimize PDF parsing if still in indexing phase

---

## Additional Resources

- **Problem Statement & Requirements**: See [BIS Standards Recommendation Engine- Hackathon.pdf](BIS%20Standards%20Recommendation%20Engine-%20Hackathon.pdf)
- **Standards Database**: [dataset_bis.pdf](dataset_bis.pdf) (contains all ~100+ BIS standards)
- **Test Set Sample** (10 queries): [public_test_set.json](public_test_set.json)
- **Output Template**: [sample_output.json](sample_output.json)

---

## Development Workflow for AI Agents

When a user requests implementation/debugging:

1. **Clarify Scope**: Ask if they're building the retriever, improving ranking, or debugging evaluation
2. **Check Files**: Validate output against [sample_output.json](sample_output.json) format
3. **Evaluate**: Always run `eval_script.py` to benchmark progress
4. **Iterate**: Focus on metrics (Hit@3 → MRR@5 → Latency)
5. **Reference**: Link to [BIS Standards Recommendation Engine- Hackathon.pdf](BIS%20Standards%20Recommendation%20Engine-%20Hackathon.pdf) for detailed rules

---

**Last Updated**: May 2026 | **Project Type**: Hackathon - Information Retrieval | **Status**: Active Development
