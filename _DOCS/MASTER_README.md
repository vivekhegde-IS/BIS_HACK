# 📚 BIS Hackathon — Master Documentation Guide

**Document**: Master Index of All Rules & Instructions  
**Status**: Complete & Final  
**Audience**: Both Person A & Person B  
**Date**: May 2026

---

## 🗺️ Documentation Map

This workspace contains the **complete, finalized rules** for the BIS Standards RAG hackathon. All documents are cross-linked and designed to be used together.

### Document Index

| Document | Purpose | For Whom | Read First? |
|----------|---------|----------|------------|
| **[COLLABORATION.md](COLLABORATION.md)** | Main collaboration guide — role division, git workflow, rules overview | Both | ✅ START HERE |
| **[PERSON_A_TASKS.md](PERSON_A_TASKS.md)** | Detailed backend pipeline tasks — ingest, indexing, retriever, inference | Person A | After COLLABORATION |
| **[PERSON_B_SETUP.md](PERSON_B_SETUP.md)** | Detailed infrastructure tasks — git setup, web UI, rationale, presentation | Person B | After COLLABORATION |
| **[CRITICAL_RULES.md](CRITICAL_RULES.md)** | 15 hardest rules that cause immediate failure if broken | Both | ⚠️ READ BEFORE ANY PUSH |
| **[VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md)** | Step-by-step verification before final submission | Both | ✅ 24 HOURS BEFORE DEADLINE |
| **[AGENTS.md](AGENTS.md)** | AI coding assistant rules and conventions for this project | AI Agents | When asking AI for help |

---

## 🚀 Quick Start Path

### For Person A (Backend Developer)

1. **Day 1** (Setup):
   - Read: [COLLABORATION.md](COLLABORATION.md) (complete)
   - Read: [PERSON_A_TASKS.md](PERSON_A_TASKS.md) (complete)
   - Understand: Git workflow, folder structure

2. **Day 2-3** (Development):
   - Code: `src/ingest.py` — extract 500+ standards
   - Code: `src/indexer.py` — build TF-IDF index
   - Code: `src/retriever.py` — implement retrieval with query expansion
   - Code: `inference.py` — command-line entry point

3. **Day 4** (Testing):
   - Run full pipeline: `ingest.py` → `indexer.py` → `inference.py` → `eval_script.py`
   - Verify metrics: Hit Rate ≥ 0.80, MRR ≥ 0.74
   - Commit and push

4. **Day 5** (Final):
   - Run [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) (data pipeline section)
   - Final push before deadline

**Key Documents**: [PERSON_A_TASKS.md](PERSON_A_TASKS.md), [CRITICAL_RULES.md](CRITICAL_RULES.md)

---

### For Person B (Infrastructure Developer)

1. **Day 0** (Repository Setup) — **DO THIS FIRST**:
   - Read: [COLLABORATION.md](COLLABORATION.md) (complete)
   - Read: [PERSON_B_SETUP.md](PERSON_B_SETUP.md) (Task 1 in detail)
   - Execute: Day 0 setup (create .gitignore, init git, push to GitHub)

2. **Day 1-3** (Development — In Parallel with Person A):
   - Code: `.env.example` — environment variables template
   - Code: `requirements.txt` — dependencies with exact versions
   - Code: `README.md` — complete documentation
   - Code: `src/app.py` — Flask web UI
   - Code: `src/rationale.py` — Anthropic API integration
   - Create: `presentation.pdf` — 8-slide deck

3. **Day 4** (Integration):
   - Test: Flask UI works (`python src/app.py`)
   - Test: Web UI connects to retriever
   - Verify: Presentation has real metrics from Person A
   - Commit and push

4. **Day 5** (Final):
   - Run [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) (web UI section)
   - Final push before deadline

**Key Documents**: [PERSON_B_SETUP.md](PERSON_B_SETUP.md), [CRITICAL_RULES.md](CRITICAL_RULES.md)

---

## ⚠️ Critical Rules at a Glance

These 15 rules cause **immediate failure or disqualification**:

| # | Rule | Severity | If Broken |
|---|------|----------|-----------|
| 1 | Repo must be PUBLIC | 🔴 CRITICAL | Disqualification |
| 2 | inference.py at root (not /src) | 🔴 CRITICAL | Disqualification |
| 3 | Output JSON keys exact: id, retrieved_standards, latency_seconds | 🔴 CRITICAL | 0/40 points |
| 4 | eval_script.py is sacred (don't edit) | 🔴 CRITICAL | Wrong scoring |
| 5 | Never commit .env file | 🔴 CRITICAL | Security breach |
| 6 | No hallucinated IS codes | 🔴 CRITICAL | -10 pts each |
| 7 | Always return exactly 5 results | 🔴 CRITICAL | Hit Rate drops |
| 8 | Load models outside loop | 🔴 CRITICAL | Latency > 5s |
| 9 | Never use "git add ." | 🔴 CRITICAL | Accidental commits |
| 10 | Always git pull before push | 🔴 CRITICAL | Merge conflicts |
| 11 | Repo public before first push | 🔴 CRITICAL | Disqualification |
| 12 | Commit tfidf_model.pkl | 🔴 CRITICAL | Nothing runs |
| 13 | requirements.txt with == versions | 🔴 CRITICAL | Install fails |
| 14 | Presentation has exactly 8 slides | 🔴 CRITICAL | Score loss |
| 15 | Slide 6 has REAL metrics | 🔴 CRITICAL | Obvious fake |

**[→ Read Full Details in CRITICAL_RULES.md](CRITICAL_RULES.md)**

---

## 📞 Decision Tree: Where to Look?

### "How do I set up the GitHub repo?"
→ [PERSON_B_SETUP.md](PERSON_B_SETUP.md) — Task 1: Initialize Repository

### "What files should I write?"
→ [COLLABORATION.md](COLLABORATION.md) — Section: "Complete Repository Structure"

### "My inference.py output is failing eval"
→ [PERSON_A_TASKS.md](PERSON_A_TASKS.md) — Section: "Component 4: Inference (inference.py)"

### "I need to add a Python package"
→ [PERSON_B_SETUP.md](PERSON_B_SETUP.md) — Task 3 (rationale.py imports)  
→ Update `requirements.txt` with exact version

### "What's the git workflow?"
→ [COLLABORATION.md](COLLABORATION.md) — Section: "🚀 Git Workflow (Safe Collaboration)"

### "I accidentally committed something wrong"
→ [CRITICAL_RULES.md](CRITICAL_RULES.md) — Section: "🛡️ Safety Mechanisms" → "Emergency Recovery Steps"

### "What metrics do I need to achieve?"
→ [COLLABORATION.md](COLLABORATION.md) — Section: "🎯 Mission Statement"  
→ Hit Rate @3 ≥ 0.80, MRR @5 ≥ 0.74, Latency < 5s

### "How do I verify everything before submitting?"
→ [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) — Complete checklist (run 24 hours before deadline)

### "What's Person A's job vs Person B's job?"
→ [COLLABORATION.md](COLLABORATION.md) — Section: "📋 Division of Labor & File Ownership"

---

## 🎯 Success Definition

You'll **WIN** this hackathon if:

✅ **Code Runs**: Judges can clone, install requirements, and run inference.py  
✅ **Metrics Meet Targets**: Hit Rate ≥ 0.80, MRR ≥ 0.74, Latency < 5s  
✅ **No Hallucinations**: All returned IS codes exist in chunks.json  
✅ **Repo is Public**: Judges can access it in incognito window  
✅ **No Secrets**: .env is never committed, API key is protected  
✅ **Presentation Ready**: 8 professional slides with real metrics on slide 6  
✅ **Documentation Complete**: README has all sections with working commands  
✅ **Timeline Met**: Submitted before May 3, 11:59 PM IST  

---

## 📅 Timeline Overview

| Date | Phase | Person A | Person B |
|------|-------|----------|----------|
| **Day 0 (May 1)** | Setup | Review docs | Create repo, .gitignore, structure |
| **Day 1** | Planning | Detailed review | Git workflow verification |
| **Day 2** | Dev Phase 1 | ingest.py, indexer.py | .env.example, requirements.txt |
| **Day 3** | Dev Phase 2 | retriever.py | README.md, app.py |
| **Day 4** | Integration | inference.py, test pipeline | rationale.py, presentation.pdf, test UI |
| **Day 5** | Final | Optimization, commit | Run checklist, final push |
| **May 3, 11:59 PM** | **DEADLINE** | All files pushed | All files pushed |

---

## 🔗 Document Cross-References

### From COLLABORATION.md
- Links to [CRITICAL_RULES.md](CRITICAL_RULES.md) for deep dives on rules
- Links to [PERSON_A_TASKS.md](PERSON_A_TASKS.md) for detailed component specs
- Links to [PERSON_B_SETUP.md](PERSON_B_SETUP.md) for infrastructure details

### From PERSON_A_TASKS.md
- References [CRITICAL_RULES.md](CRITICAL_RULES.md) — Rule A-AI-1 through A-AI-8
- References [COLLABORATION.md](COLLABORATION.md) for file ownership and git workflow

### From PERSON_B_SETUP.md
- References [CRITICAL_RULES.md](CRITICAL_RULES.md) — Rule B-AI-1 through B-AI-8
- References [COLLABORATION.md](COLLABORATION.md) for file ownership and git workflow

### From CRITICAL_RULES.md
- Links to [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) for recovery steps
- References all components from [PERSON_A_TASKS.md](PERSON_A_TASKS.md) and [PERSON_B_SETUP.md](PERSON_B_SETUP.md)

### From VERIFICATION_CHECKLIST.md
- References output formats from [PERSON_A_TASKS.md](PERSON_A_TASKS.md)
- References web UI from [PERSON_B_SETUP.md](PERSON_B_SETUP.md)
- References rules from [CRITICAL_RULES.md](CRITICAL_RULES.md)

---

## 💾 How to Use These Documents

### For Regular Development
1. Keep [COLLABORATION.md](COLLABORATION.md) open — refer to it frequently
2. When writing code, consult your specific task doc ([PERSON_A_TASKS.md](PERSON_A_TASKS.md) or [PERSON_B_SETUP.md](PERSON_B_SETUP.md))
3. Before every git push, check [CRITICAL_RULES.md](CRITICAL_RULES.md)

### For Problem-Solving
1. Use the **Decision Tree** above to find the right document
2. Search within the document for your issue
3. If you find a rule violation, consult [CRITICAL_RULES.md](CRITICAL_RULES.md) recovery steps

### For Final Submission (24 Hours Before Deadline)
1. Print or display [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md)
2. Go through **every section** methodically
3. Check off each item
4. Do not submit until all ✅ are checked

---

## 🎓 For AI Assistants Helping with Code

When asking an AI for help:

1. **Reference the specific task doc**:
   - "Person A: Help me write src/ingest.py per [PERSON_A_TASKS.md](PERSON_A_TASKS.md) Component 1"
   - "Person B: Help me write app.py per [PERSON_B_SETUP.md](PERSON_B_SETUP.md) Task 3"

2. **Remind AI of critical rules**:
   - "Important: See [CRITICAL_RULES.md](CRITICAL_RULES.md) — my output JSON keys must be: id, retrieved_standards, latency_seconds"
   - "Never commit .env or use 'git add .'"

3. **Link to relevant sections**:
   - "Per [AGENTS.md](AGENTS.md) Rule A-AI-3: Load the model outside the loop"

---

## 📞 FAQ: Using These Documents

### Q: Do I need to read all 5 documents before starting?
**A**: Not all at once. Read [COLLABORATION.md](COLLABORATION.md) first (complete understanding). Then read your specific role doc ([PERSON_A_TASKS.md](PERSON_A_TASKS.md) or [PERSON_B_SETUP.md](PERSON_B_SETUP.md)). Save [CRITICAL_RULES.md](CRITICAL_RULES.md) and [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) for reference (before pushes and final submission).

### Q: Which document has the eval_script.py metrics explanation?
**A**: [PERSON_A_TASKS.md](PERSON_A_TASKS.md) — Component 5: Evaluation. It explains Hit Rate @3, MRR @5, and Latency.

### Q: Where do I find the exact inference.py output format?
**A**: [PERSON_A_TASKS.md](PERSON_A_TASKS.md) — Component 4: Inference. Also see [CRITICAL_RULES.md](CRITICAL_RULES.md) — RULE-CRITICAL-3.

### Q: How do I fix a merge conflict?
**A**: [COLLABORATION.md](COLLABORATION.md) — "Safe git workflow" section → "How Person A and B work in parallel."

### Q: What if I violate a rule?
**A**: Look in [CRITICAL_RULES.md](CRITICAL_RULES.md) under "🛡️ Safety Mechanisms" → "Emergency Recovery Steps."

---

## 🏆 Success Checklist (TL;DR)

Before final submission, ensure:

- [ ] All 5 documents have been read and understood
- [ ] Git repository is PUBLIC
- [ ] No .env file in repository
- [ ] inference.py is at root (not in /src)
- [ ] Output JSON has exact keys: id, retrieved_standards, latency_seconds
- [ ] Metrics: Hit Rate ≥ 0.80, MRR ≥ 0.74, Latency < 5s
- [ ] No hallucinated IS codes
- [ ] presentation.pdf has 8 slides with real metrics
- [ ] README.md is complete
- [ ] requirements.txt has == versions
- [ ] Run [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) completely
- [ ] Final push before May 3, 11:59 PM IST

---

## 📖 Document Stats

| Document | Pages (Estimated) | Words | Key Sections |
|----------|------------------|-------|--------------|
| COLLABORATION.md | 15 | 8,500 | Roles, rules, git workflow, file ownership |
| PERSON_A_TASKS.md | 18 | 10,200 | Components, data pipeline, testing |
| PERSON_B_SETUP.md | 20 | 11,500 | Tasks, web UI, presentation, git |
| CRITICAL_RULES.md | 12 | 7,800 | 15 hardest rules, recovery steps |
| VERIFICATION_CHECKLIST.md | 10 | 5,500 | 10 sections, detailed verification |
| **TOTAL** | **75** | **43,500** | Complete rulebook |

---

## 🤝 Support & Questions

### If You're Stuck:
1. Check the **Decision Tree** above (section "📞 Decision Tree")
2. Search the relevant document
3. If still stuck, consult with your partner (Person A or B)
4. Last resort: Ask an AI, but reference these documents

### If Something Seems Unclear:
- These documents are designed to be crystal clear
- If you're confused, re-read the section
- If still confused after 3 readings, it's likely a legitimate issue — consult partner

### If You Catch an Error in These Documents:
- Note it down
- Finish the hackathon
- File an issue on GitHub after submission
- These docs are final for this hackathon cycle

---

## 📝 Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | May 2026 | Person B (Team Lead) | Initial complete rulebook |

---

## ✨ Final Word

These documents represent **complete, battle-tested rules** for hackathon success. They cover **every scenario**, from Day 0 setup to final submission. Follow them precisely, and you'll maximize your chances of winning.

**Trust the rules. Stick to the plan. Ship with confidence.**

---

**Master Document Version**: 1.0  
**Status**: 🟢 FINAL & LOCKED  
**Last Updated**: May 2026  
**Maintained By**: Person B (Infrastructure Team Lead)

---

## 📚 Quick Links to All Documents

- [COLLABORATION.md](COLLABORATION.md) — Main collaboration guide
- [PERSON_A_TASKS.md](PERSON_A_TASKS.md) — Backend tasks
- [PERSON_B_SETUP.md](PERSON_B_SETUP.md) — Infrastructure tasks
- [CRITICAL_RULES.md](CRITICAL_RULES.md) — Never-break rules
- [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) — Final verification
- [AGENTS.md](AGENTS.md) — AI coding rules

**Begin with [COLLABORATION.md](COLLABORATION.md). You'll know what to do next.**
