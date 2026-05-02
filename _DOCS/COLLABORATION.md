# BIS Standards RAG — Team Collaboration Guide

**Author**: Person B (Team Lead)  
**Date**: May 2026  
**Status**: Complete Rules - Never to be broken

This document defines the complete working agreement between **Person A** (AI-assisted backend/pipeline developer) and **Person B** (AI-assisted UI/infrastructure developer) for the BIS Standards Hackathon.

---

## 🎯 Mission Statement

Build a **Retrieval-Augmented Generation (RAG) pipeline** that retrieves the top-5 most relevant Bureau of Indian Standards (BIS) specifications based on natural language queries about manufacturing and compliance requirements.

**Success Metrics**:
- ✅ Hit Rate @3: ≥ 80%
- ✅ MRR @5: ≥ 0.74
- ✅ Avg Latency: < 5 seconds
- ✅ Repo is Public, Code Runs, No Hallucinations

---

## 📋 Complete Repository Structure

```
bis-standards-rag/                  (root)
│
├── .gitignore                      🔐 CRITICAL — Person B creates FIRST
├── .env.example                    📄 Committed (example only, no real keys)
├── .env                            🚫 NEVER committed (local only, .gitignore)
│
├── inference.py                    ⭐ Person A — entry point judges run
├── eval_script.py                  🔒 ORIGINAL PROVIDED FILE — DO NOT EDIT
├── requirements.txt                👥 Both contribute
├── README.md                        📖 Person B writes
├── presentation.pdf                🎤 Person B creates (8 slides)
│
├── src/                            📁 Mandatory folder
│   ├── ingest.py                   👤 Person A (parse PDF → chunks.json)
│   ├── indexer.py                  👤 Person A (build TF-IDF index)
│   ├── retriever.py                👤 Person A (cosine similarity search)
│   ├── rationale.py                🧠 Person B (Anthropic API - UI only)
│   └── app.py                      🌐 Person B (Flask web UI)
│
└── data/                           📁 Mandatory folder
    ├── chunks.json                 👤 Person A produces (500-700 entries)
    ├── tfidf_model.pkl             👤 Person A produces (MUST commit)
    ├── public_test_set.json        📥 From organizers (read-only)
    ├── public_results.json         👤 Person A produces (eval output)
    └── BIS_SP_21.* (DO NOT COMMIT) 🚫 Inputs only (.gitignore)
```

---

## 👤 Person A: Backend Pipeline Developer

### 🎯 Primary Responsibilities

**Core Task**: Build the information retrieval pipeline from PDF → Index → Inference

| Component | Input | Output | Tech |
|-----------|-------|--------|------|
| **ingest.py** | BIS_SP_21.txt | `data/chunks.json` | regex, json |
| **indexer.py** | `data/chunks.json` | `data/tfidf_model.pkl` | scikit-learn TF-IDF |
| **retriever.py** | Query + Index | Top-5 IS codes | cosine_similarity |
| **inference.py** | Test queries | JSON results | Main entry point |

### 📋 Task Checklist (Person A)

1. **Parse BIS PDF**
   - [ ] Convert `BIS_SP_21.pdf` → `BIS_SP_21.txt` using `pdftotext` command
   - [ ] Extract 500+ IS standard entries using regex pattern: `IS \d+ (Part \d+)?: \d{4}`
   - [ ] Save to `data/chunks.json` with structure: `{"id": "IS XXX: YYYY", "title": "...", "text": "..."}`

2. **Build Searchable Index**
   - [ ] Use scikit-learn `TfidfVectorizer` with `ngram_range=(1,2)` for bigrams
   - [ ] Build matrix from chunk texts
   - [ ] Pickle and save to `data/tfidf_model.pkl` (DO NOT add to .gitignore)
   - [ ] Include SYNONYMS dictionary in retriever.py for query expansion

3. **Implement Retriever**
   - [ ] Write `retriever.py` with `retrieve(query, index, top_k=5)` function
   - [ ] Expand query using SYNONYMS to boost relevance
   - [ ] Use cosine similarity for ranking
   - [ ] **CRITICAL**: Always return exactly 5 results (pad with last result if fewer retrieved)

4. **Create Inference Script**
   - [ ] Accept `--input` and `--output` flags
   - [ ] Load index **once** before loop (NOT inside loop)
   - [ ] Process all queries, measure latency per query
   - [ ] Output exactly 3 keys: `id`, `retrieved_standards` (array of 5), `latency_seconds` (float)
   - [ ] Save as JSON to specified output path

5. **Evaluation & Verification**
   - [ ] Run: `python src/ingest.py` → confirm 500+ chunks extracted
   - [ ] Run: `python src/indexer.py` → confirm index built
   - [ ] Run: `python inference.py --input data/public_test_set.json --output data/public_results.json`
   - [ ] Run: `python eval_script.py --results data/public_results.json`
   - [ ] **MUST ACHIEVE**: Hit Rate ≥ 0.80, MRR ≥ 0.74, Latency < 5s

### ⚠️ AI Coding Rules for Person A (NEVER BREAK)

| Rule ID | What NOT to Do | Consequence | Severity |
|---------|----------------|-------------|----------|
| **A-AI-1** | Place inference.py inside /src folder | Judges can't run it → **Disqualification** | 🔴 CRITICAL |
| **A-AI-2** | Change output JSON keys (use wrong names) | eval_script.py crashes → 0/40 points | 🔴 CRITICAL |
| **A-AI-3** | Load TF-IDF model inside loop | Every query takes 5+ sec → latency fail | 🔴 CRITICAL |
| **A-AI-4** | Return fewer than 5 items per query | Hit Rate/MRR drops significantly | 🔴 CRITICAL |
| **A-AI-5** | Hallucinate IS standard IDs | -10 pts per hallucination | 🔴 CRITICAL |
| **A-AI-6** | Use libraries outside requirements.txt | Code won't run on judge machines | 🟠 HIGH |
| **A-AI-7** | Remove SYNONYMS dict from retriever.py | Query expansion lost → Hit Rate drops | 🟡 MEDIUM |
| **A-AI-8** | Tweak TfidfVectorizer params without testing | May drop Hit Rate below 80% | 🟡 MEDIUM |

### 📦 Data Locations

| Data | Source | Where to Get | License |
|------|--------|--------------|---------|
| **BIS_SP_21.pdf** | Organizers | Provided in hack materials | Use only for parsing |
| **public_test_set.json** | Organizers | Provided in hack materials | Read-only, don't modify |
| **BIS_SP_21.txt** | Generated locally | Convert PDF: `pdftotext BIS_SP_21.pdf BIS_SP_21.txt` | Generated from provided PDF |

---

## 👤 Person B: Infrastructure & UI Developer

### 🎯 Primary Responsibilities

**Core Task**: Build infrastructure, web UI, deployment, and presentation

| Component | Purpose | Tech |
|-----------|---------|------|
| **.gitignore** | Protect secrets, clean git history | First file created |
| **.env.example** | Show required env vars (no real values) | Committed, safe |
| **requirements.txt** | Dependency manifest | With exact versions |
| **README.md** | Setup + run instructions | Markdown, 100% complete |
| **app.py** | Flask web UI for live demo | Flask + Jinja2 inline HTML |
| **rationale.py** | Call Anthropic API for explanations | Demo feature only |
| **presentation.pdf** | 8-slide deck for judges | Exactly 8 slides |

### 📋 Task Checklist (Person B)

1. **Setup Git Repository (DAY 0 — DO THIS FIRST)**
   - [ ] Create local folder: `mkdir bis-standards-rag && cd bis-standards-rag`
   - [ ] **Create .gitignore BEFORE anything else** (see template below)
   - [ ] Create folder structure: `mkdir src data` + touch files
   - [ ] `git init` → `git add .gitignore` → `git commit -m "Add gitignore"`
   - [ ] Create repo on GitHub (set to PUBLIC)
   - [ ] Connect: `git remote add origin ...` → `git push -u origin main`

2. **Create Infrastructure Files**
   - [ ] `.gitignore` — blocks .env, __pycache__, PDFs, .venv
   - [ ] `.env.example` — shows `ANTHROPIC_API_KEY=your_key_here` (no real value)
   - [ ] `requirements.txt` — all packages with exact == versions
   - [ ] `README.md` — full setup, run, and deployment instructions

3. **Write Flask Web UI (app.py)**
   - [ ] Single Python file with inline HTML/CSS/JS
   - [ ] Load index at **app startup** (not per-request)
   - [ ] `/` route returns HTML search interface
   - [ ] `/search` POST route accepts `{"query": "..."}`, returns `{"results": [...], "latency": X.XX}`
   - [ ] No separate CSS/JS files (keep everything in app.py)

4. **Write Rationale Generator (rationale.py)**
   - [ ] Use Anthropic Claude API (claude-sonnet-4-20250514)
   - [ ] Accept query + standard_id → return 1-sentence explanation
   - [ ] **NEVER hardcode API key** — use `os.getenv("ANTHROPIC_API_KEY")`
   - [ ] Graceful error handling (if API fails, return placeholder message)

5. **Create Presentation (presentation.pdf)**
   - [ ] Exactly 8 slides in this order:
     1. **Problem**: What problem are we solving?
     2. **Solution**: What's our approach?
     3. **Architecture**: System diagram + components
     4. **Chunking Strategy**: How we process the PDF
     5. **Demo**: Live UI walkthrough or screenshots
     6. **Evaluation Results**: Real numbers from eval_script.py output
     7. **Impact**: Why this matters
     8. **Team**: Team member details + roles
   - [ ] Use consistent design, professional fonts
   - [ ] Slide 6 must show real metrics (not placeholders)

6. **Create README.md**
   - [ ] Overview + purpose
   - [ ] Setup instructions (clone, venv, pip install)
   - [ ] Build index (ingest, indexer steps)
   - [ ] Run inference + evaluation
   - [ ] Run web UI
   - [ ] External APIs disclosure (Anthropic only for UI)
   - [ ] Hardware requirements (no GPU needed)
   - [ ] Dataset attribution (BIS SP 21)

### ⚠️ AI Coding Rules for Person B (NEVER BREAK)

| Rule ID | What NOT to Do | Consequence | Severity |
|---------|----------------|-------------|----------|
| **B-AI-1** | Hardcode API key in Python code | Public repo = key stolen immediately | 🔴 CRITICAL |
| **B-AI-2** | Import rationale.py inside inference.py | Inference becomes API-dependent + slow | 🔴 CRITICAL |
| **B-AI-3** | Create separate CSS/JS files for Flask | Risk files missing from repo | 🟠 HIGH |
| **B-AI-4** | Put presentation slides in wrong order | Subjective score loss from judges | 🟡 MEDIUM |
| **B-AI-5** | Use placeholder metrics on slide 6 | Must have real numbers from Person A | 🟡 MEDIUM |
| **B-AI-6** | Regenerate eval_script.py | That file is sacred — use only original | 🔴 CRITICAL |
| **B-AI-7** | Add new imports without updating requirements.txt | Judges get dependency errors | 🟠 HIGH |
| **B-AI-8** | Load index inside /search route | Every request becomes 5+ seconds slow | 🟠 HIGH |

### 📦 Third-Party Dependencies

| Package | Version | Why | Where Used |
|---------|---------|-----|-----------|
| scikit-learn | 1.2.2 | TF-IDF vectorization | Person A: indexer.py |
| numpy | 1.24.3 | Array operations | Person A: retriever.py |
| Flask | 2.2.5 | Web framework | Person B: app.py |
| python-dotenv | 1.0.0 | Load .env vars | Person B: rationale.py |
| anthropic | 0.25.0+ | Claude API client | Person B: rationale.py |

---

## 🔒 Critical Rules — NEVER BREAK THESE

### Rule Group: Security & Secrets

🚫 **CRITICAL-1: Never commit .env file**
- `.env` contains the real Anthropic API key
- If pushed to public repo, key is visible in git history forever
- Even deleting it later doesn't remove it from history
- **Fix**: Add to .gitignore, use only `.env.example`

🚫 **CRITICAL-2: Never hardcode API keys**
- Wrong: `api_key = "sk-ant-..."`
- Right: `os.getenv("ANTHROPIC_API_KEY")`
- Wrong gets someone's compromised account

🚫 **CRITICAL-3: Never commit BIS_SP_21.pdf or .txt**
- These are huge (100+ MB) and may have licensing issues
- Judges don't need them — they only need data/chunks.json
- Add to .gitignore

### Rule Group: Output Format (Eval Depends on This)

🚫 **CRITICAL-4: Output JSON keys must be exactly:**
```json
{
  "id": "string",                        // query ID
  "retrieved_standards": ["IS XXX: YYYY", ...],  // EXACTLY 5 items
  "latency_seconds": 0.1234              // float, NOT string
}
```
- Wrong key names = eval_script.py crashes = 0/40 points
- Fewer than 5 items = invalid result
- String latency instead of float = type error

🚫 **CRITICAL-5: Retrieved standards must not be hallucinated**
- Only return IS codes that actually exist in chunks.json
- Never invent "IS 99999: 2024"
- Each hallucination = -10 pts penalty
- Person A: verify retriever only returns real IDs from the index

### Rule Group: Git & Collaboration

🚫 **CRITICAL-6: Always git pull before git push**
- Before pushing, fetch other person's changes: `git pull origin main`
- This prevents overwriting their work
- Sequence: `git add` → `git commit` → `git pull` → `git push`

🚫 **CRITICAL-7: Never use "git add ."**
- This stages ALL files, including .env, PDFs, __pycache__
- Always add files by name: `git add requirements.txt inference.py`

🚫 **CRITICAL-8: Repo must be PUBLIC**
- Judges can't see private repos
- Set to Public immediately after creating on GitHub
- Verify: open in incognito browser — if you see files without login, it's public

🚫 **CRITICAL-9: inference.py must be at root, not in /src**
- Judges run: `python inference.py --input ... --output ...`
- Not: `python src/inference.py`
- Wrong location = disqualification

🚫 **CRITICAL-10: eval_script.py is sacred**
- Use the ORIGINAL file provided by organizers
- Do NOT edit it, regenerate it, or modify it
- Copy byte-for-byte from the provided file

### Rule Group: Performance

🚫 **CRITICAL-11: Load models outside loops**
- Wrong: Load tfidf_model.pkl inside the for-loop for each query
- Right: Load once before loop
- Wrong causes 5+ sec per query latency

🚫 **CRITICAL-12: Always return exactly 5 items**
- Padding logic: `while len(ids) < 5: ids.append(ids[-1])`
- Fewer than 5 = invalid submission
- More than 5 = take first 5: `retrieved_standards[:5]`

---

## 📞 Division of Labor & File Ownership

| File | Owner | Can Read? | Can Edit? | Notes |
|------|-------|-----------|-----------|-------|
| inference.py | Person A | Both | A only | Entry point judges run |
| src/ingest.py | Person A | Both | A only | Parse PDF |
| src/indexer.py | Person A | Both | A only | Build index |
| src/retriever.py | Person A | Both | A only | Cosine search |
| src/app.py | Person B | Both | B only | Flask UI |
| src/rationale.py | Person B | Both | B only | API calls |
| data/chunks.json | Person A | Both | A only | Generated output |
| data/tfidf_model.pkl | Person A | Both | A only | Generated output |
| requirements.txt | **Both** | Both | Both | Coordinate versions |
| README.md | Person B | Both | B only | Setup docs |
| presentation.pdf | Person B | Both | B only | 8 slides |
| .gitignore | Person B | Both | B only | Don't edit after push |
| .env.example | Person B | Both | B only | Example only |
| eval_script.py | **Nobody** | Read only | FORBIDDEN | Original file — sacred |

**Rule**: If you need to edit someone else's file, **communicate first**. They make the edit. This prevents merge conflicts.

---

## 🚀 Git Workflow (Safe Collaboration)

### Phase 1: Day 0 — Person B Sets Up Repository

```bash
# Person B runs this FIRST, before any code is written

mkdir bis-standards-rag
cd bis-standards-rag

# Create .gitignore BEFORE anything else
cat > .gitignore << 'EOF'
.env
__pycache__/
*.pyc
*.pyo
.venv/
venv/
.DS_Store
*.log
BIS_SP_21.txt
BIS_SP_21.pdf
EOF

# Create folder structure
mkdir src data
touch inference.py eval_script.py requirements.txt README.md presentation.pdf
touch src/ingest.py src/indexer.py src/retriever.py src/rationale.py src/app.py
echo "" > data/.gitkeep

# Initialize git
git init
git add .gitignore       # Add FIRST
git commit -m "Add gitignore"

git add .
git commit -m "Initial folder structure"

# On GitHub.com: Create repo "bis-standards-rag", set to PUBLIC

# Connect local repo to GitHub
git remote add origin https://github.com/YOUR_USERNAME/bis-standards-rag.git
git branch -M main
git push -u origin main

# Both persons clone this repo
git clone https://github.com/YOUR_USERNAME/bis-standards-rag.git
```

### Phase 2: Parallel Work — Person A + B Code Independently

**Person A**: Works on src/ingest.py, src/indexer.py, src/retriever.py, inference.py
**Person B**: Works on src/app.py, src/rationale.py, README.md, requirements.txt, presentation.pdf

Each person works in their own clone, commits locally, then pushes.

### Phase 3: Safe Push Workflow (Both Persons)

**Before every push, follow this sequence:**

```bash
# 1. Check what changed
git status

# 2. Review changes locally before committing
git diff HEAD

# 3. Stage your files (by name, not with ".")
git add src/ingest.py src/indexer.py inference.py data/chunks.json

# 4. Review what will be committed
git diff --cached

# 5. Commit with clear message
git commit -m "Add ingest + indexer: extracts 600+ chunks from BIS PDF"

# 6. GET the other person's changes FIRST
git pull origin main

# 7. If there are conflicts, resolve them manually, then:
#    git add (resolved files)
#    git commit -m "Resolve merge conflict"

# 8. Only then push
git push origin main
```

### Phase 4: If Something Goes Wrong (Recovery)

**Scenario 1: Push broke inference.py**
```bash
git log --oneline         # Find last good commit
git revert COMMIT_HASH    # Undo that commit (creates new commit)
git push origin main      # Push the fix
```

**Scenario 2: .env accidentally committed** ⚠️ SERIOUS
```bash
# 1. Rotate API key immediately (go to Anthropic console, revoke, generate new)
# 2. Remove from tracking
git rm --cached .env
git commit -m "Remove .env from tracking"
git push origin main
# 3. The key in git history is still visible — that's why rotation is crucial
```

**Scenario 3: tfidf_model.pkl missing**
```bash
# Person A rebuilds and pushes it
python src/indexer.py
git add data/tfidf_model.pkl
git commit -m "Add rebuilt tfidf model"
git push origin main
```

---

## ✅ Final Verification Checklist

### Checklist Part 1: Code Correctness (Person A)

- [ ] Run: `python src/ingest.py`  
  Expected output: "Extracted 500+ chunks"

- [ ] Run: `python src/indexer.py`  
  Expected output: "Index built: 5XX docs, XXXX terms"

- [ ] Run: `python inference.py --input data/public_test_set.json --output data/public_results.json`  
  No errors, completes in <60 seconds total

- [ ] Run: `python eval_script.py --results data/public_results.json`  
  Output shows: Hit Rate ≥ 0.80, MRR ≥ 0.74, Latency < 5s

- [ ] Verify output structure:
  ```bash
  python -c "
  import json
  data = json.load(open('data/public_results.json'))
  for item in data:
      assert len(item['retrieved_standards']) == 5
      assert isinstance(item['latency_seconds'], (float, int))
  print('PASS: Output format correct')
  "
  ```

### Checklist Part 2: Infrastructure (Person B)

- [ ] `.gitignore` exists and blocks: `.env`, `__pycache__`, `*.pdf`, `*.txt`

- [ ] `.env` is NOT in the repo (check: `git ls-files | grep env` returns nothing)

- [ ] `.env.example` is in the repo and shows: `ANTHROPIC_API_KEY=your_key_here`

- [ ] `requirements.txt` has all packages with == pinned versions

- [ ] Run web UI test:
  ```bash
  cp .env.example .env
  # Edit .env and add real API key
  python src/app.py
  # Open http://localhost:5000
  # Type a query, press Search
  # Verify results appear with explanations
  ```

- [ ] `presentation.pdf` exists and has exactly 8 slides in this order:
  1. Problem
  2. Solution
  3. Architecture
  4. Chunking
  5. Demo
  6. Evaluation Results (with REAL numbers)
  7. Impact
  8. Team

- [ ] `README.md` includes:
  - Overview
  - Setup instructions (clone, venv, pip install)
  - Build commands (ingest, indexer)
  - Inference + evaluation commands
  - Web UI run command
  - External APIs disclosure
  - Hardware requirements
  - Dataset attribution

### Checklist Part 3: Git Repository

- [ ] Repo URL is public (verify in incognito: can see files without login)

- [ ] All expected files are committed:
  ```bash
  git ls-files | sort
  # Must include: inference.py, src/*, data/*, .gitignore, requirements.txt, etc.
  ```

- [ ] No large files in `.gitignore` violations:
  ```bash
  git ls-files | grep -E "\.pdf$|\.txt$|__pycache__|\.pyc" 
  # Should return nothing
  ```

### Checklist Part 4: Final Metrics

- [ ] Hit Rate @3: ≥ **0.80** (80% of queries have correct answer in top 3)
- [ ] MRR @5: ≥ **0.74** (ranking quality is good)
- [ ] Avg Latency: < **5.0** seconds per query
- [ ] Hallucination Count: **0** (all IS codes are real)
- [ ] Presentation Slides: **8** (exact count)

---

## 📞 Emergency Contact Points

**If merge conflict happens:**  
→ One person stops, other person resolves, communicate before pushing

**If eval score drops suddenly:**  
→ Check git log for recent changes, git diff to find what broke

**If .env is committed:**  
→ STOP. Rotate API key immediately. This is a security incident.

**If inference.py can't be found by judges:**  
→ Check: Is it in repo root (not /src)? Is eval_script.py able to import it?

**If tfidf_model.pkl is missing:**  
→ Person A rebuilds: `python src/indexer.py && git add data/tfidf_model.pkl && git push`

---

## 📅 Timeline & Submission

| Phase | Deadline | Owner | Tasks |
|-------|----------|-------|-------|
| **Setup** | Day 0 | Person B | Repo, .gitignore, structure |
| **Core Dev** | Day 2-4 | Both | Pipeline (A) + UI (B) in parallel |
| **Integration** | Day 4 | Both | Test together, fix issues |
| **Verification** | Day 4 Evening | Both | Run all checklists |
| **Presentation Prep** | Day 4 | Person B | Finalize slides + demo video |
| **Final Push** | Day 5 | Both | Last tests, submit before 11:59 PM IST |
| **Submission** | May 3, 11:59 PM IST | Both | All files in public GitHub repo |

---

## ✨ Success Looks Like

✅ Judges clone the repo  
✅ `pip install -r requirements.txt` — no errors  
✅ `python src/ingest.py` — extracts chunks  
✅ `python src/indexer.py` — builds index  
✅ `python inference.py --input data/public_test_set.json --output data/public_results.json` — runs in <60s  
✅ `python eval_script.py --results data/public_results.json` — shows Hit Rate 0.85+, MRR 0.80+  
✅ `python src/app.py` — web UI works, live demo ready  
✅ presentation.pdf — 8 professional slides with real metrics  
✅ README.md — complete and clear  
✅ No secrets in repo, no PDFs committed  
✅ Team is declared, roles are clear  

---

**Last Updated**: May 2026  
**Status**: Active  
**Maintained By**: Person B (Team Infrastructure Lead)
