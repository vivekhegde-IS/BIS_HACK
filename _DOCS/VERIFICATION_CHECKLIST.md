# ✅ FINAL VERIFICATION CHECKLIST

**Purpose**: Complete verification before final submission  
**Deadline**: 1 hour before submission  
**Participants**: Person A + Person B (together)

---

## 📋 SECTION 1: Repository & Git (Person B Leads)

### Git Repository Status
- [ ] Repository is PUBLIC (verify in incognito window)
- [ ] Repository URL: https://github.com/[USERNAME]/bis-standards-rag
- [ ] All expected files are tracked:
  ```bash
  git ls-files | sort
  # Should list: inference.py, eval_script.py, requirements.txt, README.md, 
  # presentation.pdf, .gitignore, .env.example, src/*, data/*
  ```

### Sensitive Files Protection
- [ ] `.gitignore` exists and is first commit
- [ ] `.env` is **NOT** in `git ls-files`:
  ```bash
  git ls-files | grep "\.env$"  # Should return NOTHING
  ```
- [ ] No PDFs except presentation.pdf:
  ```bash
  git ls-files | grep -E "\.pdf$|\.txt$"
  # Should ONLY show: presentation.pdf
  ```
- [ ] No Python cache or compiled files:
  ```bash
  git ls-files | grep -E "__pycache__|\.pyc|\.pyo"  # Should return NOTHING
  ```

### Git History
- [ ] At least 5 commits in history:
  ```bash
  git log --oneline | wc -l  # Should be 5+
  ```
- [ ] Recent commits have clear messages:
  ```bash
  git log --oneline -5  # Review last 5 commits
  ```
- [ ] Working directory is clean:
  ```bash
  git status  # Should show "nothing to commit, working tree clean"
  ```

---

## 🏗️ SECTION 2: Files & Structure (Both Review)

### File Count & Locations
- [ ] inference.py exists at **root** (not in src):
  ```bash
  test -f inference.py && echo "✓ Found" || echo "✗ Missing"
  ```

- [ ] eval_script.py exists at root:
  ```bash
  test -f eval_script.py && echo "✓ Found" || echo "✗ Missing"
  ```

- [ ] src/ folder contains 5 files:
  ```bash
  ls -1 src/ | wc -l  # Should be 5
  # Files: ingest.py, indexer.py, retriever.py, rationale.py, app.py
  ```

- [ ] data/ folder contains 4 files:
  ```bash
  ls -1 data/ | wc -l  # Should be 4
  # Files: chunks.json, tfidf_model.pkl, public_test_set.json, public_results.json
  ```

### File Sizes (Sanity Check)
- [ ] requirements.txt is < 1 KB (text file)
- [ ] README.md is > 5 KB (substantial documentation)
- [ ] presentation.pdf is > 500 KB (has 8 slides with content)
- [ ] data/chunks.json is > 1 MB (600+ entries)
- [ ] data/tfidf_model.pkl is 10-50 MB (serialized model)

### File Permissions
- [ ] All .py files are readable:
  ```bash
  find . -name "*.py" -exec test -r {} \; && echo "✓ All readable"
  ```

- [ ] All .json files are readable:
  ```bash
  find data -name "*.json" -exec test -r {} \; && echo "✓ All readable"
  ```

---

## 📊 SECTION 3: Data Pipeline (Person A Leads)

### Step 1: Ingestion
```bash
python src/ingest.py
```
- [ ] Command completes without errors
- [ ] Output includes: "Extracted XXX chunks" (XXX should be 500+)
- [ ] `data/chunks.json` exists and is > 1 MB
- [ ] Spot check:
  ```bash
  python -c "
  import json
  chunks = json.load(open('data/chunks.json'))
  print(f'Total: {len(chunks)}')
  print(f'First chunk: {chunks[0].keys()}')
  assert all(k in chunks[0] for k in ['id', 'title', 'text'])
  print('✓ Chunks are valid')
  "
  ```

### Step 2: Indexing
```bash
python src/indexer.py
```
- [ ] Command completes without errors
- [ ] Output includes: "Index built: XXX docs" (XXX should be 500+)
- [ ] `data/tfidf_model.pkl` exists and is > 5 MB
- [ ] Spot check:
  ```bash
  python -c "
  import pickle
  index = pickle.load(open('data/tfidf_model.pkl', 'rb'))
  assert 'vectorizer' in index
  assert 'matrix' in index
  assert 'chunks' in index
  print(f'Matrix shape: {index[\"matrix\"].shape}')
  print('✓ Index is valid')
  "
  ```

### Step 3: Inference
```bash
python inference.py --input data/public_test_set.json --output data/public_results.json
```
- [ ] Command completes without errors
- [ ] Output includes: "Done: X queries processed"
- [ ] `data/public_results.json` exists
- [ ] Spot check:
  ```bash
  python -c "
  import json
  results = json.load(open('data/public_results.json'))
  print(f'Total results: {len(results)}')
  
  # Check first result
  r = results[0]
  assert 'id' in r, 'Missing id'
  assert 'retrieved_standards' in r, 'Missing retrieved_standards'
  assert 'latency_seconds' in r, 'Missing latency_seconds'
  assert len(r['retrieved_standards']) == 5, f'Expected 5 results, got {len(r[\"retrieved_standards\"])}'
  assert isinstance(r['latency_seconds'], float), 'latency_seconds must be float'
  
  print('Sample:', r)
  print('✓ Output format is correct')
  "
  ```

### Step 4: Evaluation
```bash
python eval_script.py --results data/public_results.json
```
- [ ] Command completes without errors
- [ ] Output shows metrics:
  ```
  Hit Rate @3: X.XX% (Target: >80%)
  MRR @5:      X.XXXX (Target: >0.74)
  Avg Latency: X.XXX sec (Target: <5.0)
  ```
- [ ] Metrics meet targets:
  - [ ] Hit Rate @3: **≥ 0.80** (80%)
  - [ ] MRR @5: **≥ 0.74**
  - [ ] Avg Latency: **< 5.0 seconds**

### Step 5: Sanity Checks
- [ ] No hallucinated IS codes:
  ```bash
  python -c "
  import json
  
  chunks = json.load(open('data/chunks.json'))
  real_ids = set(c['id'] for c in chunks)
  
  results = json.load(open('data/public_results.json'))
  
  hallucinations = 0
  for r in results:
      for std_id in r['retrieved_standards']:
          if std_id not in real_ids:
              print(f'❌ HALLUCINATION: {std_id}')
              hallucinations += 1
  
  if hallucinations == 0:
      print('✓ No hallucinations detected')
  else:
      print(f'⚠️ {hallucinations} hallucinations found')
  "
  ```

---

## 🌐 SECTION 4: Web UI (Person B Leads)

### Setup
- [ ] `.env.example` exists at root
- [ ] `.env` exists locally (with real API key)
- [ ] `.env` is NOT in git:
  ```bash
  git ls-files | grep "\.env$"  # Should return NOTHING
  ```

### Functionality
```bash
# Start Flask server
python src/app.py
```
- [ ] Server starts without errors
- [ ] Output shows: "Running on http://127.0.0.1:5000"

**In Browser**:
1. [ ] Open http://localhost:5000
2. [ ] Search interface loads (purple gradient background)
3. [ ] Type a query: "cement"
4. [ ] Click "Search" button
5. [ ] Results appear (within 5 seconds)
6. [ ] Each result shows:
   - [ ] Number (#1, #2, etc.)
   - [ ] Standard ID (e.g., "IS 269: 1989")
   - [ ] AI-generated explanation (1-2 sentences)
7. [ ] Latency appears at bottom (e.g., "Response time: 0.45s")
8. [ ] Stop server: Ctrl+C

---

## 📄 SECTION 5: Documentation (Person B Leads)

### README.md
- [ ] File exists at root: `ls -la README.md`
- [ ] Contains all 8 required sections:
  - [ ] Overview
  - [ ] Requirements
  - [ ] Quick Start
  - [ ] Build Index
  - [ ] Run Inference
  - [ ] Evaluate Results
  - [ ] Run Web UI
  - [ ] Project Structure
  - [ ] Architecture
  - [ ] Configuration
  - [ ] Dependencies
  - [ ] Evaluation Metrics
  - [ ] Demo
  - [ ] External APIs
  - [ ] Attribution & Licensing
  - [ ] Troubleshooting

- [ ] Commands are copy-pasteable (not pseudocode)
- [ ] Project structure diagram matches actual files
- [ ] No placeholder text (like "[YOUR_USERNAME_HERE]")

### presentation.pdf
- [ ] File exists: `ls -la presentation.pdf`
- [ ] Is valid PDF:
  ```bash
  file presentation.pdf  # Should show "PDF"
  ```
- [ ] Has exactly 8 slides:
  ```bash
  # Open in PDF reader and count, or use tool:
  pdfinfo presentation.pdf  # Shows page count
  ```

- [ ] Slide order is correct:
  1. Problem
  2. Solution
  3. Architecture
  4. Chunking
  5. Demo
  6. Evaluation Results
  7. Impact
  8. Team

- [ ] Slide 6 (Evaluation Results) has REAL numbers:
  - [ ] Hit Rate @3: (actual value, not placeholder)
  - [ ] MRR @5: (actual value, not placeholder)
  - [ ] Latency: (actual value, not placeholder)

- [ ] Slide 8 (Team) includes:
  - [ ] Person A: Name, Role, Contact
  - [ ] Person B: Name, Role, Contact

- [ ] File size is reasonable (< 20 MB)

### requirements.txt
- [ ] File exists: `ls -la requirements.txt`
- [ ] Has all packages with exact == versions:
  ```bash
  cat requirements.txt
  # Should show lines like:
  # scikit-learn==1.2.2
  # numpy==1.24.3
  # Flask==2.2.5
  # python-dotenv==1.0.0
  # anthropic==0.25.0
  ```

- [ ] No ~ or >= versions:
  ```bash
  grep -E "~=|>=" requirements.txt  # Should return NOTHING
  ```

- [ ] Can be installed fresh:
  ```bash
  python -m venv .venv_test
  source .venv_test/bin/activate
  pip install -r requirements.txt
  # Should install without errors
  ```

---

## 🔒 SECTION 6: Security & Secrets (Both Review)

### Secrets Protection
- [ ] `.env` is NOT in repo:
  ```bash
  git log -p --all -- ".env" | head -1  # Should show nothing
  ```

- [ ] No API keys in any Python files:
  ```bash
  grep -r "sk-ant-" src/ *.py 2>/dev/null  # Should return NOTHING
  grep -r "ANTHROPIC_API_KEY=" src/ *.py 2>/dev/null | grep -v "os.getenv"  # Should return NOTHING
  ```

- [ ] No API keys in any config files:
  ```bash
  grep -r "sk-ant-" data/ 2>/dev/null  # Should return NOTHING
  ```

### Safe API Usage
- [ ] src/rationale.py uses `os.getenv()`:
  ```bash
  grep -n "os.getenv.*ANTHROPIC" src/rationale.py
  # Should find at least 1 line
  ```

- [ ] No hardcoded values in src/app.py:
  ```bash
  grep -n "sk-ant-" src/app.py  # Should return NOTHING
  ```

---

## 📦 SECTION 7: Dependencies & Installation

### Fresh Install Test
```bash
# Start from scratch
rm -rf .venv_test

python -m venv .venv_test
source .venv_test/bin/activate  # On Windows: .venv_test\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
```

- [ ] All packages install without errors
- [ ] No version conflicts

### Import Test
```bash
# Still in .venv_test

python -c "
import sys
sys.path.insert(0, '.')

# Test imports
from src.ingest import parse_standards
from src.indexer import build_index
from src.retriever import load_index, retrieve
from src.rationale import get_rationale

print('✓ All imports successful')
"
```
- [ ] All imports succeed without errors

---

## 🎯 SECTION 8: Performance Targets

### Metrics Summary
```bash
# Last run of eval_script.py
python eval_script.py --results data/public_results.json
```

Fill in actual values:

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Hit Rate @3 | ≥ 0.80 | _____ | ✓/✗ |
| MRR @5 | ≥ 0.74 | _____ | ✓/✗ |
| Avg Latency | < 5.0s | _____ | ✓/✗ |

- [ ] Hit Rate ✓ (≥ 80%)
- [ ] MRR ✓ (≥ 0.74)
- [ ] Latency ✓ (< 5 seconds)

### Quality Metrics
- [ ] No hallucinated IS codes: **0** hallucinations
- [ ] Presentation slides: **8** (exact count)
- [ ] Data entries: **500+** standards

---

## 🚀 SECTION 9: Final Git Operations

### Pre-Push Verification
```bash
# 1. Check status
git status
```
- [ ] Output shows: "nothing to commit, working tree clean"

```bash
# 2. List tracked files
git ls-files | wc -l
```
- [ ] Should be 15+ files

```bash
# 3. Verify no untracked files
git status | grep "Untracked"
```
- [ ] Should return NOTHING (or no relevant files)

### Final Commit (if needed)
```bash
# If changes were made in verification:
git add <specific files>
git diff --cached         # Review before committing
git commit -m "Final verification and fixes"
git pull origin main      # Get latest from partner
git push origin main      # Push to GitHub
```

- [ ] `git pull` completes without conflicts
- [ ] `git push` succeeds without errors

---

## 🎬 SECTION 10: Submission Readiness

### Public Visibility
- [ ] Open repo URL in incognito window:
  ```
  https://github.com/[USERNAME]/bis-standards-rag
  ```
- [ ] Can see files **without** logging in: ✓
- [ ] Does NOT prompt for login: ✓

### Complete File List (Verify All Present)

```bash
git ls-files | sort
```

Expected output (all these files should be present):
```
.env.example
.gitignore
README.md
data/.gitkeep
data/chunks.json
data/public_results.json
data/public_test_set.json
data/tfidf_model.pkl
eval_script.py
inference.py
presentation.pdf
requirements.txt
src/app.py
src/ingest.py
src/indexer.py
src/rationale.py
src/retriever.py
```

Check off:
- [ ] .env.example ✓
- [ ] .gitignore ✓
- [ ] README.md ✓
- [ ] data/chunks.json ✓
- [ ] data/public_results.json ✓
- [ ] data/public_test_set.json ✓
- [ ] data/tfidf_model.pkl ✓
- [ ] eval_script.py ✓
- [ ] inference.py ✓
- [ ] presentation.pdf ✓
- [ ] requirements.txt ✓
- [ ] src/app.py ✓
- [ ] src/ingest.py ✓
- [ ] src/indexer.py ✓
- [ ] src/rationale.py ✓
- [ ] src/retriever.py ✓

### Submission Deadline
- [ ] Submission deadline: **May 3, 11:59 PM IST**
- [ ] Current time: ___________
- [ ] Time until deadline: ___________ hours
- [ ] All checks complete: **YES**

---

## ✅ FINAL SIGNATURE

When all checks are complete, sign here:

**Person A (Backend)**
- Name: _____________________
- Date: ____________________
- Signature: _________________
- All backend tasks complete: YES / NO

**Person B (Infrastructure)**
- Name: _____________________
- Date: ____________________
- Signature: _________________
- All infrastructure tasks complete: YES / NO

**Joint Verification**
- [ ] Both persons have reviewed all checks
- [ ] No critical violations found
- [ ] Repo is public and accessible
- [ ] All metrics meet targets
- [ ] Ready to submit: **YES**

---

**Document Version**: 1.0  
**Last Updated**: May 2026  
**Status**: Final Checklist
