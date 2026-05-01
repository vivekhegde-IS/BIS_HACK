# PERSON A: BACKEND DEVELOPER - CRITICAL RULES

**You are the Backend Pipeline Developer. These are the RULES you MUST NEVER BREAK.**

---

## 🔴 TIER 1 (AUTOMATIC DISQUALIFICATION)

### Rule A-1: inference.py Must Be at Root
```
✅ CORRECT:   ./inference.py
❌ WRONG:     ./src/inference.py
```
**Why**: Judges expect entry point at root directory  
**Penalty**: Disqualification

### Rule A-2: Output JSON Keys Must Be Exact
```json
{
  "id": "query_id",
  "retrieved_standards": ["IS 1875", "IS 2062", "IS 3975", "IS 1677", "IS 1687"],
  "latency_seconds": 0.245
}
```
**Why**: eval_script.py expects exact keys  
**Penalty**: 0/40 points (automatic failure)

### Rule A-3: Always Load Models Outside Loop
```python
# ✅ CORRECT
vectorizer, tfidf_matrix = load_model()
for query in queries:
    results = vectorizer.transform([query])

# ❌ WRONG
for query in queries:
    vectorizer, tfidf_matrix = load_model()  # SLOW!
    results = vectorizer.transform([query])
```
**Why**: Loading inside loop causes Latency > 5 seconds  
**Penalty**: Hit Rate/MRR calculations fail

### Rule A-4: Always Return Exactly 5 Results
```python
# ✅ CORRECT
retrieved_standards = get_top_5_results(query)  # Always 5

# ❌ WRONG
retrieved_standards = get_top_3_results(query)  # Wrong count!
```
**Why**: eval_script.py expects exactly 5 for MRR @5 calculation  
**Penalty**: Hit Rate and MRR metrics fail

### Rule A-5: Never Commit eval_script.py Modifications
```bash
# ✅ CORRECT
git diff eval_script.py  # Shows: no changes

# ❌ WRONG
# You edited eval_script.py
git add eval_script.py
```
**Why**: Judges use original eval_script.py for scoring  
**Penalty**: Wrong scoring / Disqualification

### Rule A-6: All IS Codes Must Be Real (No Hallucinations)
```python
# ✅ CORRECT
retrieved_standards = ["IS 1875", "IS 2062"]  # Real codes

# ❌ WRONG
retrieved_standards = ["IS 9999999", "IS 1234"]  # Made up!
```
**Why**: eval_script.py checks against ground truth  
**Penalty**: -10 points per hallucinated code

---

## 🟡 TIER 2 (SEVERE POINT LOSS)

### Rule A-7: Commit tfidf_model.pkl
```bash
git add tfidf_model.pkl
git commit -m "Add trained model"
```
**Why**: inference.py needs the model  
**Penalty**: -5 points (if missing, inference fails entirely)

### Rule A-8: Don't Use git add .
```bash
# ✅ CORRECT
git add src/ingest.py src/indexer.py src/retriever.py

# ❌ WRONG
git add .  # Might add .env, __pycache__, etc.
```
**Why**: Prevents accidental secret commits  
**Penalty**: -10 points (if .env exposed)

---

## 📊 PERSON A CHECKLIST (Before Any Push)

- [ ] inference.py is at root (./inference.py), NOT in src/
- [ ] Output JSON has exact keys: id, retrieved_standards, latency_seconds
- [ ] Always return exactly 5 results per query
- [ ] All IS codes are real (no made-up codes)
- [ ] Model loads ONCE at startup (outside loop)
- [ ] eval_script.py is NOT modified
- [ ] tfidf_model.pkl is committed
- [ ] No changes to eval_script.py in git log
- [ ] Using git add with specific files (not "git add .")
- [ ] Test with: python inference.py --input public_test_set.json --output test.json

---

## 🧪 TESTING COMMANDS (Person A)

```bash
# Test 1: Check inference.py location
test -f ./inference.py && echo "✓ inference.py at root" || echo "✗ ERROR: Wrong location"

# Test 2: Run inference
python inference.py --input public_test_set.json --output test_results.json

# Test 3: Check output format
python -c "import json; d=json.load(open('test_results.json')); print('Keys:', list(d['results'][0].keys()))"
# Should print: Keys: ['id', 'retrieved_standards', 'latency_seconds']

# Test 4: Check result count
python -c "import json; d=json.load(open('test_results.json')); print('Results per query:', len(d['results'][0]['retrieved_standards']))"
# Should print: Results per query: 5

# Test 5: Run evaluation
python eval_script.py

# Test 6: Check model is committed
git log --oneline | grep -i "model\|pkl"
```

---

## ⚠️ EMERGENCY RECOVERY

### If inference.py is in wrong location:
```bash
git mv src/inference.py inference.py
git commit -m "Move inference to root"
git push origin main
```

### If output format is wrong:
1. Open inference.py
2. Find the result formatting section
3. Ensure JSON has exactly: id, retrieved_standards, latency_seconds
4. Re-run: python inference.py --input public_test_set.json --output test.json
5. Verify with: python -c "import json; print(json.load(open('test.json')))"

### If returning wrong number of results:
1. Open inference.py
2. Find retrieve_standards() function
3. Ensure it always returns top_k=5
4. Add while loop to pad with default IS codes if needed

---

## 📞 CONTACT PERSON B IF:

- You need git help
- Repo structure changed
- Need to push to GitHub
- Not sure about file location
- Need Person B to verify checklist

---

**Status**: 🟢 FINAL & LOCKED  
**Version**: 1.0  
**Remember**: These rules are non-negotiable. Break even one and you lose points or get disqualified.
