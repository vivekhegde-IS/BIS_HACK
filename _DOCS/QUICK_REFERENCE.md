# 📊 COMPLETE RULES SUMMARY — One-Page Reference

**As Person B (Team Lead): I have finalized all rules. Print this page and keep it visible.**

---

## 🎯 PROJECT AT A GLANCE

**BIS Standards RAG**: Retrieve top-5 relevant Indian Standards from 600+ entries based on natural language queries.

| Metric | Target | Your Goal |
|--------|--------|-----------|
| Hit Rate @3 | ≥ 80% | |
| MRR @5 | ≥ 0.74 | |
| Latency | < 5s | |
| Repo | PUBLIC | |
| Deadline | May 3, 11:59 PM IST | |

---

## 👥 ROLES & RESPONSIBILITIES

### Person A: Backend Pipeline Developer
```
BIS_SP_21.pdf → ingest.py → chunks.json → indexer.py → tfidf_model.pkl
                                                          ↓
                                                      retriever.py → inference.py
Files to write: inference.py, src/ingest.py, src/indexer.py, src/retriever.py
```

### Person B: Infrastructure & UI Developer (You!)
```
Git Repo Setup (Day 0) → Flask Web UI → Anthropic Rationale → Presentation
Files to write: src/app.py, src/rationale.py, README.md, presentation.pdf
Files to create: .gitignore, .env.example, requirements.txt
```

---

## 🔴 15 CRITICAL RULES (MEMORIZE THESE)

| # | Rule | Violate? | Consequence |
|---|------|----------|-------------|
| 1 | Repo must be PUBLIC | ❌ | Disqualification |
| 2 | inference.py at root | ❌ | Disqualification |
| 3 | JSON keys: id, retrieved_standards, latency_seconds | ❌ | 0/40 pts |
| 4 | Don't edit eval_script.py | ❌ | Wrong scoring |
| 5 | Never commit .env | ❌ | Security breach |
| 6 | No hallucinated IS codes | ❌ | -10 pts each |
| 7 | Always 5 results per query | ❌ | Hit Rate drops |
| 8 | Load models outside loop | ❌ | Latency > 5s |
| 9 | Never use "git add ." | ❌ | Accidental commits |
| 10 | Always git pull before push | ❌ | Merge conflicts |
| 11 | Repo public before first push | ❌ | Disqualification |
| 12 | Commit tfidf_model.pkl | ❌ | Nothing runs |
| 13 | requirements.txt with == | ❌ | Install fails |
| 14 | Presentation: 8 slides | ❌ | Score loss |
| 15 | Slide 6: REAL metrics | ❌ | Obvious fake |

---

## 📋 PERSON B TASK CHECKLIST

### Day 0: Repository Setup (CRITICAL — DO FIRST)
- [ ] Create local folder: `mkdir bis-standards-rag && cd bis-standards-rag`
- [ ] Create `.gitignore` BEFORE anything else
- [ ] `git init` → first commit: `.gitignore`
- [ ] Create folder structure: `mkdir src data`
- [ ] Create GitHub repo (set to PUBLIC)
- [ ] Connect: `git remote add origin https://...`
- [ ] Verify: Open in incognito → can see files without login

### Day 1-3: Development
- [ ] `.env.example` — template with placeholder values (COMMIT)
- [ ] `requirements.txt` — all packages with == versions (COMMIT)
- [ ] `README.md` — complete documentation (COMMIT)
- [ ] `src/app.py` — Flask web UI with inline HTML (COMMIT)
- [ ] `src/rationale.py` — Anthropic API integration (COMMIT)
- [ ] `presentation.pdf` — 8 slides in correct order (COMMIT)

### Day 4: Integration & Testing
- [ ] Test: `python src/app.py` → opens UI at http://localhost:5000
- [ ] Test: Search query works → results appear with explanations
- [ ] Verify: Slide 6 has REAL metrics from Person A
- [ ] Commit and push

### Day 5: Final Verification
- [ ] Run complete checklist (see VERIFICATION_CHECKLIST.md)
- [ ] All metrics pass targets
- [ ] No secrets in repo
- [ ] Final push before deadline

---

## 🔐 SECRETS PROTECTION CHECKLIST

**Before EVERY push:**

```bash
# Check .env is not tracked
git ls-files | grep "\.env$"
# Should return: NOTHING (empty)

# Check no API keys in code
grep -r "sk-ant-" src/ *.py
# Should return: NOTHING

# Check no PDFs except presentation
git ls-files | grep -E "\.pdf$|\.txt$"
# Should return only: presentation.pdf
```

---

## 🚀 GIT WORKFLOW (Standard Process)

### Every Time You Commit:

```bash
# 1. Stage your files (by name, NOT dot)
git add requirements.txt src/app.py README.md

# 2. Review before committing
git diff --cached

# 3. Commit with clear message
git commit -m "Add Flask UI and README"

# 4. GET partner's changes FIRST
git pull origin main

# 5. Only then push
git push origin main
```

### NEVER Do This:
```bash
git add .           # ❌ Adds everything (risks .env!)
git add -A          # ❌ Same problem
git commit --all    # ❌ Same problem
```

---

## 📊 FILES YOU MUST CREATE

| File | Type | Owner | Size | Committed? |
|------|------|-------|------|-----------|
| .gitignore | Text | B | < 1 KB | ✓ YES (FIRST) |
| .env.example | Text | B | < 1 KB | ✓ YES |
| .env | Text | B | < 1 KB | ✗ NO (.gitignore) |
| requirements.txt | Text | B | < 1 KB | ✓ YES |
| README.md | Markdown | B | > 5 KB | ✓ YES |
| presentation.pdf | PDF | B | > 500 KB | ✓ YES |
| src/app.py | Python | B | > 10 KB | ✓ YES |
| src/rationale.py | Python | B | > 2 KB | ✓ YES |

---

## 🎬 PRESENTATION SLIDES (Exact Order)

1. **Problem**: What problem are we solving?
2. **Solution**: Our approach
3. **Architecture**: System diagram
4. **Chunking**: How we parse PDF
5. **Demo**: Live walkthrough
6. **Evaluation Results**: ⭐ **REAL NUMBERS HERE**
7. **Impact**: Use cases & benefits
8. **Team**: Names, roles, contact

---

## 🧪 QUICK TEST COMMANDS

```bash
# Test 1: Flask UI loads
python src/app.py
# Check: http://localhost:5000 works

# Test 2: Requirements install
python -m venv .venv_test
source .venv_test/bin/activate
pip install -r requirements.txt
# Check: No errors

# Test 3: No secrets in repo
git log -p --all -- ".env" | head -1
# Check: No output (clean)

# Test 4: Repo is public
# Open in incognito: https://github.com/USERNAME/bis-standards-rag
# Check: Can see files WITHOUT login
```

---

## ⚠️ EMERGENCY FIXES

### If You Committed .env:
```bash
# STOP. Rotate API key immediately (Anthropic console)
git rm --cached .env
git commit -m "Remove .env"
git push origin main
# Key in history is still visible (that's why rotation matters)
```

### If Repo is Still Private:
```bash
# GitHub Settings → "Make this repository public"
# Verify in incognito window again
```

### If inference.py is in /src:
```bash
git mv src/inference.py inference.py
git commit -m "Move inference to root"
git push origin main
```

---

## 📞 WHEN TO USE EACH DOCUMENT

| Situation | Document |
|-----------|----------|
| "What's my job?" | COLLABORATION.md |
| "How do I set up Flask?" | PERSON_B_SETUP.md Task 3 |
| "What's Person A building?" | PERSON_A_TASKS.md |
| "I'm about to push — what could go wrong?" | CRITICAL_RULES.md |
| "Is my code ready to submit?" | VERIFICATION_CHECKLIST.md |
| "Which documents should I read first?" | MASTER_README.md |

---

## ✅ PRE-SUBMISSION CHECKLIST (Last 24 Hours)

```bash
# 1. Repo is public?
# Open in incognito: GitHub URL works without login ✓

# 2. .env not in repo?
git ls-files | grep "\.env$"
# Returns: NOTHING ✓

# 3. All files present?
git ls-files | wc -l
# Returns: 15+ ✓

# 4. Presentation has 8 slides?
# Count slides in PDF ✓

# 5. Person A's metrics meet targets?
# Hit Rate ≥ 0.80, MRR ≥ 0.74, Latency < 5s ✓

# 6. Slide 6 has REAL numbers (not placeholders)?
# Check presentation.pdf ✓

# 7. Flask UI works?
python src/app.py
# Open http://localhost:5000, search works ✓

# 8. No uncommitted changes?
git status
# Returns: "nothing to commit" ✓

# If ALL ✓, you're ready to submit
```

---

## 🎯 SUCCESS INDICATORS

✅ **Done Right If**:
- Code runs: `pip install -r requirements.txt` → no errors
- Pipeline works: `python inference.py --input ... --output ...` → completes in <60s
- Metrics pass: `python eval_script.py` → Hit ≥0.80, MRR ≥0.74
- Web UI works: `python src/app.py` → search → results appear
- Repo accessible: Incognito window → GitHub → files visible without login
- No secrets: `git ls-files` → no .env, no API keys
- Documentation complete: README has all sections, presentation has 8 slides
- Presentation professional: Real metrics on slide 6, proper slide order

---

## 📅 TIMELINE (Critical Dates)

| Date | Phase | Owner | Action |
|------|-------|-------|--------|
| **May 1** | Day 0 | B | Setup repo, .gitignore, structure |
| **May 2-3** | Dev | A+B | Code in parallel |
| **May 3 AM** | Integration | A+B | Test together |
| **May 3, 8 PM** | Final Check | A+B | Run verification checklist |
| **May 3, 11 PM** | Submit | A+B | Final push to GitHub |
| **May 3, 11:59 PM** | **DEADLINE** | Judge | Repo locked for evaluation |

---

## 🔐 GOLDEN RULES (Read 3x Per Day)

1. **Make Repo PUBLIC before first push** ← Check this Daily
2. **Never commit .env** ← Check this before every push
3. **Output JSON keys: id, retrieved_standards, latency_seconds** ← Check when testing
4. **Exactly 5 results per query** ← Check in inference.py
5. **All IS codes must be real (no hallucinations)** ← Check in retriever.py

---

## 📞 DECISION TREE (Quick Help)

**"Where should I look for..."**

- Setup instructions? → PERSON_B_SETUP.md
- Git workflow? → COLLABORATION.md
- eval_script.py? → PERSON_A_TASKS.md
- Critical rules? → CRITICAL_RULES.md
- Final verification? → VERIFICATION_CHECKLIST.md
- Everything? → MASTER_README.md

---

**Print this page. Keep it visible. Reference daily.**

**Status**: 🟢 FINAL & LOCKED  
**Version**: 1.0  
**Author**: Person B (Team Lead)  
**Date**: May 2026
