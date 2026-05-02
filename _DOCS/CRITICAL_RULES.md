# 🔴 CRITICAL RULES — NEVER BREAK THESE

**Document Status**: Sacred Rules  
**Last Updated**: May 2026

This document lists the 15 hardest rules that will cause **immediate failure, disqualification, or severe point loss** if violated.

---

## 🔴 TIER 1 (AUTOMATIC DISQUALIFICATION)

These violations result in **0 points** or **disqualification**:

### RULE-CRITICAL-1: Repository Must Be PUBLIC

**What It Means**:
- Judges cannot access private repositories
- Your work must be visible without login
- The moment you create the GitHub repo, set it to PUBLIC

**How to Verify**:
1. Open repo URL in incognito/private browser window
2. If you can see the files **without** logging in → ✅ Public
3. If it says "404" or prompts to login → ❌ Private (FAIL)

**Consequence**: Disqualification (judges cannot see your code)

**How to Fix If Missed**:
- Go to GitHub repo Settings
- Scroll to "Danger Zone"
- Click "Make this repository public"
- Verify again in incognito window

---

### RULE-CRITICAL-2: inference.py Must Be at Repository Root

**What It Means**:
- Judges run: `python inference.py --input ... --output ...`
- NOT: `python src/inference.py`
- If inference.py is inside /src folder, judges can't find it

**Correct Location**:
```
bis-standards-rag/
├── inference.py           ✅ HERE (root)
└── src/
    ├── ingest.py
    ├── indexer.py
    ├── retriever.py
```

**Wrong Location**:
```
bis-standards-rag/
└── src/
    ├── inference.py       ❌ WRONG (inside src)
```

**Consequence**: Disqualification (judges can't run inference)

**How to Fix**: Move file to root: `git mv src/inference.py inference.py`

---

### RULE-CRITICAL-3: Output JSON Keys Must Be Exact

**What It Means**:
The eval_script.py **crashes** if JSON keys are wrong. Wrong keys = **0/40 points**.

**Exact Required Keys**:
```json
{
  "id": "PUB-01",
  "retrieved_standards": ["IS 269: 1989", "IS 455: 1989", ...],
  "latency_seconds": 1.2345
}
```

**WRONG** ❌ (will crash eval_script):
```json
{
  "query_id": "PUB-01",           ❌ Should be "id"
  "results": ["IS 269: 1989"],    ❌ Should be "retrieved_standards"
  "time": 1.2345                  ❌ Should be "latency_seconds"
}
```

**Consequence**: eval_script.py crashes → **0/40 points**

**How to Fix**: Edit inference.py output dictionary keys to match exactly

---

### RULE-CRITICAL-4: eval_script.py Is Sacred

**What It Means**:
- Use the ORIGINAL eval_script.py provided by organizers
- Do NOT edit it, rewrite it, or regenerate it
- Do NOT rename it
- Copy it **byte-for-byte**

**Wrong** ❌:
```python
# DO NOT do this:
# - Regenerate eval_script.py from AI
# - Add print statements
# - Change variable names
# - Modify logic
```

**Right** ✅:
```python
# Copy the original file exactly as given
# Use it as-is
```

**Consequence**: Wrong eval_script = **0/40 points** (judges use original)

**How to Fix**: Get original file from organizers, copy it exactly to repo root

---

### RULE-CRITICAL-5: Never Commit .env File

**What It Means**:
- `.env` contains your REAL Anthropic API key
- If pushed to public repo, the key is visible in git history **forever**
- Even deleting it later doesn't remove it from git history
- Anyone can steal and use your key

**Wrong** ❌:
```bash
echo "ANTHROPIC_API_KEY=sk-ant-XXXXXXXXXXXX" > .env
git add .env           ❌ STOP! Don't do this!
git commit -m "Add .env"
git push origin main   ❌ Key is now PUBLIC!
```

**Right** ✅:
```bash
# Create .env locally ONLY
cp .env.example .env
# Edit it with your real key (local machine only)
# .gitignore blocks it:
git status  # .env should NOT appear here
```

**Consequence**: **SECURITY INCIDENT** — key compromised (potential $$$$ charges)

**Recovery** ⚠️ If You Accidentally Pushed It:
1. IMMEDIATELY rotate your API key (go to Anthropic console)
2. `git rm --cached .env && git commit -m "Remove .env"`
3. `git push origin main`
4. The key in git history is still visible — that's why rotation is CRITICAL

---

### RULE-CRITICAL-6: Retrieved Standards Must Not Be Hallucinated

**What It Means**:
- You can **ONLY** return IS standard IDs that actually exist in your chunks.json
- Never invent fake IDs like "IS 99999: 2024"
- Each hallucination = **-10 points**
- 5+ hallucinations = automatic failure

**Example** ❌ WRONG:
```python
# Retriever returns this:
["IS 269: 1989",      # ✅ Real (exists in chunks.json)
 "IS 455: 1989",      # ✅ Real
 "IS 12345: 2024",    # ❌ HALLUCINATED (doesn't exist)
 "IS 99999: 2024"]    # ❌ HALLUCINATED
# Result: -20 points penalty
```

**How to Fix**:
- Ensure retriever ONLY returns IDs from chunks.json
- Verify: `index["chunks"]` contains all returned IDs
- Add assertion: `assert retrieved_id in [c["id"] for c in chunks]`

**Consequence**: -10 pts per hallucination

---

## 🔴 TIER 2 (SEVERE POINT LOSS)

These violations result in **significant score reduction**:

### RULE-CRITICAL-7: Always Return Exactly 5 Items Per Query

**What It Means**:
- Every retrieved_standards list must have **exactly 5 items**
- Fewer than 5 = invalid
- More than 5 = take only first 5

**Wrong** ❌:
```json
{
  "id": "PUB-01",
  "retrieved_standards": ["IS 269: 1989", "IS 455: 1989"]  // ❌ Only 2
}
```

**Right** ✅:
```json
{
  "id": "PUB-01",
  "retrieved_standards": [
    "IS 269: 1989",
    "IS 455: 1989",
    "IS 455: 1989",    // Pad with last result
    "IS 455: 1989",
    "IS 455: 1989"
  ]
}
```

**How to Fix** (in inference.py):
```python
while len(retrieved) < 5:
    retrieved.append(retrieved[-1])  # Pad with last result
retrieved = retrieved[:5]             # Take only first 5
```

**Consequence**: Hit Rate drops significantly

---

### RULE-CRITICAL-8: Load Models OUTSIDE the Loop

**What It Means**:
- Load tfidf_model.pkl **ONCE** before processing queries
- **NEVER** load inside the query loop
- Loading inside loop causes 5+ seconds per query → latency failure

**Wrong** ❌:
```python
for query in queries:
    index = load_index("data/tfidf_model.pkl")  # ❌ Load every iteration!
    results = retrieve(query, index)            # 5+ sec per query
```

**Right** ✅:
```python
index = load_index("data/tfidf_model.pkl")  # Load ONCE
for query in queries:
    results = retrieve(query, index)        # Use same index
```

**Consequence**: Latency > 5s → score loss

---

### RULE-CRITICAL-9: Never Use "git add ."

**What It Means**:
- Always stage files by name: `git add requirements.txt inference.py`
- **NEVER** use: `git add .` (dot adds everything)
- Dot adds .env, __pycache__, PDFs, and other junk

**Wrong** ❌:
```bash
git add .           # ❌ Adds EVERYTHING including .env!
git commit -m "..."
git push            # ❌ .env is now public!
```

**Right** ✅:
```bash
git add requirements.txt inference.py src/app.py
git commit -m "..."
git push
```

**Consequence**: Accidental commits (secrets, large files, clutter)

---

### RULE-CRITICAL-10: Always git pull Before git push

**What It Means**:
- Fetch Person B's (or A's) changes BEFORE pushing yours
- This prevents overwriting their work
- Sequence: `git add` → `git commit` → `git pull` → `git push`

**Wrong** ❌:
```bash
git add inference.py
git commit -m "Fix retriever"
git push origin main  # ❌ If Person B pushed first, you overwrite their work
```

**Right** ✅:
```bash
git add inference.py
git commit -m "Fix retriever"
git pull origin main  # Get their changes first
git push origin main  # Now push yours
```

**Consequence**: Merge conflicts or lost work

---

### RULE-CRITICAL-11: Repo Must Be Public BEFORE First Push

**What It Means**:
- Create GitHub repo with "Public" visibility setting
- Do this **before** the first `git push`
- If you accidentally create it as Private, change it immediately

**Steps**:
1. GitHub.com → "New" → Create repository
2. Under "Who can see this repository" → Select **PUBLIC**
3. Click "Create repository"
4. Then connect and push

**Consequence**: Disqualification if repo remains private

---

### RULE-CRITICAL-12: Commit tfidf_model.pkl

**What It Means**:
- The serialized TF-IDF index (tfidf_model.pkl) MUST be committed to repo
- Do NOT add it to .gitignore
- It's 10-50 MB, but judges need it to run inference

**Wrong** ❌:
```
.gitignore:
*.pkl           # ❌ Blocks tfidf_model.pkl from being committed!
```

**Right** ✅:
```bash
git add data/tfidf_model.pkl
git commit -m "Add TF-IDF index"
git push
```

**Consequence**: `pickle.load()` fails → nothing works

---

### RULE-CRITICAL-13: requirements.txt Must Have Exact Versions

**What It Means**:
- Every package must use `==` with an exact version
- No `~=` or `>=` allowed
- Judges need reproducible environment

**Wrong** ❌:
```
scikit-learn>=1.0     # ❌ Too loose
numpy~=1.24          # ❌ ~= not allowed
Flask==2.2.5         # ✅ Correct
```

**Right** ✅:
```
scikit-learn==1.2.2
numpy==1.24.3
Flask==2.2.5
python-dotenv==1.0.0
anthropic==0.25.0
```

**Consequence**: Judges can't install or get dependency conflicts

---

### RULE-CRITICAL-14: Presentation Must Have Exactly 8 Slides

**What It Means**:
- Presentation must have **exactly 8 slides**
- Fewer slides = incomplete
- More slides = judged only on first 8

**Required Slides** (in order):
1. Problem
2. Solution
3. Architecture
4. Chunking Strategy
5. Demo
6. Evaluation Results (with REAL numbers)
7. Impact
8. Team

**Consequence**: Presentation score loss if wrong count or order

---

### RULE-CRITICAL-15: Slide 6 Must Have Real Metrics

**What It Means**:
- Slide 6 (Evaluation Results) must show actual numbers from eval_script.py
- Not placeholders like "[YOUR METRIC HERE]"
- Judges notice fake numbers immediately

**Wrong** ❌:
```
Slide 6:
Hit Rate @3: [TBD]
MRR @5: [YOUR METRIC HERE]
Latency: TBD
```

**Right** ✅:
```
Slide 6:
Hit Rate @3: 0.85 (Target: ≥0.80)
MRR @5: 0.78 (Target: ≥0.74)
Latency: 0.92 sec (Target: <5s)
```

**How to Get Real Numbers**:
1. Run: `python eval_script.py --results data/public_results.json`
2. Copy metrics from terminal output
3. Add to slide 6

**Consequence**: Subjective score loss

---

## 🛡️ Safety Mechanisms (Use These)

### Mechanism 1: Pre-Push Checklist

Run these before **every push**:

```bash
# 1. Check repo state
git status              # Nothing left uncommitted?
git log --oneline -3    # Recent commits look good?

# 2. Verify key files exist
ls -la inference.py               # At root?
ls -la src/ingest.py src/indexer.py src/retriever.py
ls -la data/chunks.json data/tfidf_model.pkl

# 3. Verify .env is not tracked
git ls-files | grep -i env       # Should show only .env.example

# 4. Verify PDFs are not tracked
git ls-files | grep -E "\.pdf$|\.txt$"  # Should show no PDFs except presentation.pdf

# 5. If all checks pass:
git push origin main
```

### Mechanism 2: Pre-Submission Test

Run these **24 hours before submission**:

```bash
# Full pipeline test
python src/ingest.py
python src/indexer.py
python inference.py --input data/public_test_set.json --output data/public_results.json
python eval_script.py --results data/public_results.json

# Check metrics meet targets
# Hit Rate @3 ≥ 0.80?
# MRR @5 ≥ 0.74?
# Latency < 5s?

# If not, optimize before final push
```

### Mechanism 3: Final Verification (Hour Before Submission)

```bash
# 1. Is repo public?
# Open in incognito: https://github.com/USERNAME/bis-standards-rag
# Can you see files without login?

# 2. Are all files present?
git ls-files | wc -l    # Should be 15+ files

# 3. Is .env exposed?
git ls-files | grep "\.env$"  # Should return NOTHING

# 4. Is presentation.pdf valid PDF?
file presentation.pdf   # Should show "PDF"

# 5. Does README.md have all sections?
grep -c "^## " README.md  # Should be 8+

# 6. Final push
git status              # Clean?
git push origin main
```

---

## 📞 Emergency Recovery Steps

### Emergency 1: "I Accidentally Committed .env"

```bash
# STOP immediately

# Step 1: Rotate API key (Anthropic console)
# Your old key is compromised

# Step 2: Remove from git
git rm --cached .env
git commit -m "Remove .env from tracking"
git push origin main

# Step 3: The key in git history is still visible
# That's why rotation was necessary
# Do NOT try to rewrite git history
```

### Emergency 2: "inference.py is Inside /src"

```bash
# Move to root
git mv src/inference.py inference.py
git commit -m "Move inference.py to root"
git push origin main
```

### Emergency 3: "My Metrics Are Below Target"

```bash
# With 24 hours before submission:

# 1. Check if all 600+ standards were extracted
python src/ingest.py

# 2. Rebuild index
python src/indexer.py

# 3. Test retrieval
python -c "from src.retriever import retrieve, load_index; index = load_index(); print(retrieve('cement', index))"

# 4. Add more synonyms to src/retriever.py SYNONYMS dict

# 5. Re-run inference
python inference.py --input data/public_test_set.json --output data/public_results.json

# 6. Check metrics
python eval_script.py --results data/public_results.json

# 7. If better: commit and push
git add data/public_results.json src/retriever.py
git commit -m "Improve retriever with more synonyms"
git push origin main
```

### Emergency 4: "eval_script.py is Broken"

```bash
# Get original from organizers
# Copy EXACTLY to repo root
# Replace your modified version
git add eval_script.py
git commit -m "Restore original eval_script.py"
git push origin main
```

---

## ✅ Sacred Violations Checklist

Before final submission, verify NONE of these apply:

- [ ] ❌ Repo is still private
- [ ] ❌ inference.py is inside /src
- [ ] ❌ JSON output keys are wrong (not id, retrieved_standards, latency_seconds)
- [ ] ❌ .env is committed to repo
- [ ] ❌ Retrieved standards include hallucinated IDs
- [ ] ❌ Some queries return fewer than 5 results
- [ ] ❌ Loaded TF-IDF model inside query loop
- [ ] ❌ Used "git add ." instead of adding files by name
- [ ] ❌ Didn't git pull before git push
- [ ] ❌ presentation.pdf is missing or has wrong slide count
- [ ] ❌ Slide 6 has placeholder metrics (not real numbers)
- [ ] ❌ eval_script.py was edited or regenerated
- [ ] ❌ requirements.txt has loose version specifiers (not ==)
- [ ] ❌ tfidf_model.pkl is in .gitignore or not committed
- [ ] ❌ PDFs (BIS_SP_21.pdf, BIS_SP_21.txt) are committed

If **ANY** are checked, FIX IMMEDIATELY.

---

**Last Updated**: May 2026  
**Status**: Final  
**Severity**: 🔴 CRITICAL — Read Before Every Commit
