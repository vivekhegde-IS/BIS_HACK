# PERSON B: INFRASTRUCTURE DEVELOPER - CRITICAL RULES

**You are the Infrastructure Lead. These are the RULES you MUST NEVER BREAK.**

---

## 🔴 TIER 1 (AUTOMATIC DISQUALIFICATION)

### Rule B-1: GitHub Repo Must Be PUBLIC
```bash
# ✅ CORRECT
# GitHub Settings → Make public
# Verify: Open in incognito → URL loads without login

# ❌ WRONG
# Repo is Private
```
**Why**: Judges need to access without authentication  
**Penalty**: Disqualification

### Rule B-2: Never Commit .env File
```bash
# ✅ CORRECT
git ls-files | grep "\.env$"
# Returns: (nothing)

# ❌ WRONG
# .env is in git repository
```
**Why**: Exposes API keys to public GitHub  
**Penalty**: Disqualification + Security Breach

### Rule B-3: .gitignore Must Block .env FIRST
```bash
# Your first commit MUST be .gitignore with:
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Initial: Add gitignore"
git push origin main
```
**Why**: Prevents accidental .env commits  
**Penalty**: If .env is exposed, -50 points minimum

### Rule B-4: Create Repo Public BEFORE First Push
```bash
# ✅ CORRECT
# Create GitHub repo as PUBLIC
# Then: git push origin main

# ❌ WRONG
# Create as PRIVATE
# Push code
# Then change to PUBLIC (too late, code is exposed to repo history)
```
**Why**: Public setting must be set from the beginning  
**Penalty**: Disqualification (judges can't access)

### Rule B-5: Never Hardcode API Keys in Code
```python
# ✅ CORRECT
api_key = os.getenv('ANTHROPIC_API_KEY')

# ❌ WRONG
api_key = "sk-ant-xxxxxxxxxxxxx"  # Exposed!
```
**Why**: API keys must only come from .env  
**Penalty**: -50 points + Security breach

---

## 🟡 TIER 2 (SEVERE POINT LOSS)

### Rule B-6: Never Use "git add ."
```bash
# ✅ CORRECT
git add requirements.txt src/app.py src/rationale.py README.md

# ❌ WRONG
git add .  # Might add .env, __pycache__, *.pkl
```
**Why**: Prevents accidental file commits  
**Penalty**: -10 points per wrong file

### Rule B-7: Always git pull Before Push
```bash
# ✅ CORRECT
git add src/app.py
git commit -m "Add Flask UI"
git pull origin main  # Get Person A's changes
git push origin main

# ❌ WRONG
git add src/app.py
git commit -m "Add Flask UI"
git push origin main  # Skipped pull!
```
**Why**: Prevents merge conflicts  
**Penalty**: -5 points + Manual conflict resolution needed

### Rule B-8: requirements.txt Must Have == Versions
```bash
# ✅ CORRECT
Flask==2.2.5
scikit-learn==1.2.2
numpy==1.24.3

# ❌ WRONG
Flask  # No version!
scikit-learn>=1.0  # Loose version!
```
**Why**: Exact versions ensure reproducibility  
**Penalty**: -5 points (if installation fails on judge's machine)

---

## 📋 PERSON B SPECIFIC RULES

### Rule B-9: Flask App Must Load Model at Startup
```python
# ✅ CORRECT
app = Flask(__name__)

@app.before_first_request
def load_model():
    global vectorizer, tfidf_matrix
    vectorizer, tfidf_matrix = load_model_once()

# ❌ WRONG
@app.route('/search')
def search():
    vectorizer, tfidf_matrix = load_model()  # SLOW!
```
**Why**: Loading on every request causes latency spike  
**Penalty**: -5 points (UI becomes slow)

### Rule B-10: Presentation Must Have 8 Slides
```
Slide 1: Title
Slide 2: Problem
Slide 3: Solution
Slide 4: Architecture
Slide 5: Chunking
Slide 6: RESULTS (with REAL metrics from Person A)
Slide 7: Impact
Slide 8: Team
```
**Why**: Judges expect exactly 8 slides  
**Penalty**: -5 points (if wrong count or Slide 6 has placeholder metrics)

---

## 📊 PERSON B CHECKLIST (Before Any Push)

- [ ] GitHub repo is PUBLIC
- [ ] First commit is .gitignore (check git log)
- [ ] .env file is in .gitignore
- [ ] .env.example exists with placeholders
- [ ] requirements.txt has exact versions (==)
- [ ] README.md is complete with all sections
- [ ] src/app.py loads model at startup (not per request)
- [ ] src/rationale.py uses os.getenv() for API key
- [ ] No hardcoded API keys in any file
- [ ] presentation.pdf has exactly 8 slides
- [ ] Slide 6 has REAL metrics (not placeholders)
- [ ] .git/config has correct remote URL
- [ ] No changes to eval_script.py
- [ ] All Python files have shebang (#!/usr/bin/env python3)

---

## 🧪 TESTING COMMANDS (Person B)

```bash
# Test 1: Repo is public
# Open in incognito: https://github.com/USERNAME/bis-standards-rag
# If you see files WITHOUT login → ✓ Public

# Test 2: .env is not tracked
git ls-files | grep "\.env$"
# Should return: (nothing)

# Test 3: .gitignore is first commit
git log --oneline | tail -1
# Should show: ".gitignore" in message

# Test 4: No API keys in code
grep -r "sk-ant-" src/ *.py 2>/dev/null
# Should return: (nothing)

# Test 5: requirements.txt format
grep -E "==" requirements.txt
# Should show: All packages with == versions

# Test 6: Flask loads model at startup
grep -A5 "@app.before_first_request" src/app.py
# Should show: Model loading code

# Test 7: Git remote is correct
git remote -v
# Should show: Your GitHub URL

# Test 8: No uncommitted changes
git status
# Should show: "nothing to commit"
```

---

## 🔒 SECRET MANAGEMENT (CRITICAL)

### Setup .env Correctly:
```bash
# 1. Copy template
cp .env.example .env

# 2. Edit .env (never commit this!)
# Add your ANTHROPIC_API_KEY

# 3. Verify it's ignored
git status | grep .env
# Should return: (nothing - not tracked)

# 4. Check .gitignore has .env
grep "^\.env$" .gitignore
# Should return: .env
```

### If You Accidentally Commit .env:
```bash
# ❌ STOP - Do this immediately:

# 1. Remove from git history
git rm --cached .env
git commit -m "Remove .env from tracking"
git push origin main

# 2. Rotate API key (Anthropic dashboard)
# The key is still in history, so rotate it

# 3. Update .gitignore if not already done
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
git push origin main
```

---

## 📁 FOLDER STRUCTURE (Verify Before Pushing)

```
bis-standards-rag/
├── .git/                    # Git folder
├── .gitignore               # ✓ First commit
├── .env.example             # ✓ Committed
├── .env                     # ✗ NOT committed
├── README.md                # ✓ Complete
├── requirements.txt         # ✓ With == versions
├── RULES_PERSON_A.md       # ✓ Person A rules
├── RULES_PERSON_B.md       # ✓ This file
├── inference.py             # ✓ Person A's file
├── eval_script.py           # ✓ Don't modify
├── chunks.json              # ✓ Person A generates
├── tfidf_model.pkl          # ✓ Person A generates
├── presentation.pdf         # ✓ 8 slides, Slide 6 real metrics
├── src/
│   ├── ingest.py            # ✓ Person A
│   ├── indexer.py           # ✓ Person A
│   ├── retriever.py         # ✓ Person A
│   ├── app.py               # ✓ You create
│   └── rationale.py         # ✓ You create
├── data/
│   ├── .gitkeep             # ✓ For git to track folder
│   └── BIS_SP_21.pdf        # ✗ NOT committed (in .gitignore)
└── _DOCS/                   # ✗ NOT pushed (documentation only)
    └── (all markdown files)
```

---

## ⚠️ EMERGENCY RECOVERY

### If Repo is Still Private:
```bash
# Go to GitHub Settings
# Repository Visibility → Make Public
# Wait 1-2 minutes for propagation
# Verify: Incognito window → GitHub URL works
```

### If You Added Wrong Files:
```bash
# Check what's staged
git status

# Unstage wrong files
git reset HEAD wrong_file.py

# Stage only correct files
git add src/app.py src/rationale.py requirements.txt

# Commit
git commit -m "Add Flask UI and rationale"
```

### If Presentation Metrics Are Placeholders:
```bash
# Get Person A's real metrics
python eval_script.py

# Insert into presentation.pdf Slide 6:
# Hit Rate: 0.82 (from eval output)
# MRR: 0.75 (from eval output)
# Latency: 0.34s (from eval output)
```

---

## 📞 WORKING WITH PERSON A

### Daily Sync:
```bash
# Check what Person A committed
git log --oneline -5

# Pull their changes
git pull origin main

# Verify their files exist
test -f inference.py && echo "✓ inference.py exists"
test -f tfidf_model.pkl && echo "✓ model exists"
test -f chunks.json && echo "✓ chunks exist"
```

### Coordinating on Presentation:
```bash
# Person A sends you the metrics
# Hit Rate @3: 0.82
# MRR @5: 0.76
# Latency: 0.32s

# You update Slide 6 of presentation.pdf
# Commit and push
```

---

## 📊 GIT WORKFLOW (Step-by-Step)

### Initial Setup (Day 0):
```bash
# 1. Create local folder
mkdir bis-standards-rag && cd bis-standards-rag

# 2. Initialize git
git init

# 3. Create .gitignore FIRST
echo ".env" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pkl" >> .gitignore

# 4. Commit .gitignore
git add .gitignore
git commit -m "Initial: Add gitignore"

# 5. Create folder structure
mkdir src data

# 6. Create GitHub repo (PUBLIC)
# https://github.com/new → Create Repository as PUBLIC

# 7. Connect local to GitHub
git remote add origin https://github.com/USERNAME/bis-standards-rag.git
git branch -M main
git push -u origin main
```

### Daily Development:
```bash
# 1. Pull latest from Person A
git pull origin main

# 2. Make your changes
# Edit src/app.py, etc.

# 3. Stage specific files
git add src/app.py src/rationale.py

# 4. Review changes
git diff --cached

# 5. Commit with clear message
git commit -m "Add Flask UI with search functionality"

# 6. Pull again (Person A might have pushed)
git pull origin main

# 7. Push your changes
git push origin main
```

---

**Status**: 🟢 FINAL & LOCKED  
**Version**: 1.0  
**Remember**: You are the integrator. Your job is to keep the repo clean, secure, and organized.
