# Person B — Infrastructure & UI Setup Tasks

**Role**: AI-Assisted Infrastructure & UI Developer  
**Primary Focus**: Git Setup → Flask Web UI → Deployment → Presentation  
**Partner**: Person A (Backend Pipeline)

---

## 🎯 Your Mission

Set up the Git repository, build a Flask web interface for live searching, integrate the Anthropic API for explanations, create comprehensive documentation, and prepare a professional presentation deck.

**Success = Repo is Public + UI Works + No Secrets Exposed + 8-Slide Presentation**

---

## 📋 Task 1: Initialize Repository (DAY 0 — DO THIS FIRST)

### Phase 1.1: Create Local Structure

This must happen **BEFORE any code is written**.

```bash
# Step 1: Create directory
mkdir bis-standards-rag
cd bis-standards-rag

# Step 2: Create .gitignore file IMMEDIATELY (BEFORE git init)
cat > .gitignore << 'EOF'
# Environment variables (CRITICAL - never commit)
.env

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Virtual environments
.venv/
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Large files (source only, not outputs)
BIS_SP_21.pdf
BIS_SP_21.txt
EOF

# Step 3: Create folder structure
mkdir -p src data
touch .gitignore
touch inference.py eval_script.py requirements.txt README.md presentation.pdf
touch src/ingest.py src/indexer.py src/retriever.py src/rationale.py src/app.py
echo "" > data/.gitkeep

# Step 4: Initialize git
git init

# Step 5: FIRST commit MUST be .gitignore
git add .gitignore
git commit -m "Add gitignore (security first)"

# Step 6: Add folder structure
git add .
git commit -m "Initial folder structure for BIS Standards RAG"

# Step 7: Create empty license file
touch LICENSE
echo "MIT License - See organizers for full text" > LICENSE
git add LICENSE
git commit -m "Add license"
```

### Phase 1.2: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `bis-standards-rag`
3. Description: `BIS Standards Retrieval-Augmented Generation System`
4. **Visibility: PUBLIC** (CRITICAL — judges must see it)
5. Click "Create repository"

### Phase 1.3: Connect Local to GitHub

```bash
# Replace YOUR_USERNAME with your actual GitHub username
git remote add origin https://github.com/YOUR_USERNAME/bis-standards-rag.git
git branch -M main
git push -u origin main

# Verify it worked
git remote -v  # Should show origin URL twice
```

### Phase 1.4: Verify Repository is Public

```bash
# Open in incognito window (different browser, or Ctrl+Shift+N in Chrome)
# Navigate to: https://github.com/YOUR_USERNAME/bis-standards-rag
#
# If you can see files WITHOUT logging in, it's public ✓
# If it says "404" or prompts to log in, it's private ✗
```

### Success Criteria for Task 1
- [ ] .gitignore is first commit (before any code)
- [ ] Folder structure exists locally: src/, data/
- [ ] GitHub repo is created and set to PUBLIC
- [ ] Repo is accessible in incognito window
- [ ] Git remote is configured: `git remote -v` shows origin

---

## 🔐 Task 2: Create Infrastructure Files

### Task 2.1: .env.example (Committed to Repo)

This file shows what environment variables are needed, WITHOUT exposing real values.

```bash
# File: .env.example
# Location: Repository root
# Status: COMMIT this file ✓

cat > .env.example << 'EOF'
# Anthropic API Configuration
# Get your API key from: https://console.anthropic.com/
ANTHROPIC_API_KEY=your_anthropic_key_here
EOF

git add .env.example
git commit -m "Add environment variables example"
```

### Task 2.2: .env (Local Only — NEVER Commit)

This file contains YOUR REAL API KEY and lives on your machine only.

```bash
# File: .env
# Location: Repository root (but .gitignore blocks it)
# Status: DO NOT COMMIT ✗

# Create locally (on your machine only)
cp .env.example .env

# Edit .env with your real API key
# nano .env
# OR
# code .env (in VS Code)

# Replace: your_anthropic_key_here
# With: sk-ant-XXXXXXXXXXXXXXXXXXXX (your real key)

# Verify .env is BLOCKED by .gitignore
git status  # Should NOT show .env
```

### Task 2.3: requirements.txt (Committed)

All Python dependencies with exact versions.

```bash
# File: requirements.txt
# Location: Repository root
# Status: COMMIT this file ✓

cat > requirements.txt << 'EOF'
scikit-learn==1.2.2
numpy==1.24.3
Flask==2.2.5
python-dotenv==1.0.0
anthropic==0.25.0
EOF

git add requirements.txt
git commit -m "Add Python dependencies"
```

### Success Criteria for Task 2
- [ ] .env.example exists with placeholder values
- [ ] .env.example is committed to repo
- [ ] .env exists locally with real API key
- [ ] .env is NOT in git status (blocked by .gitignore)
- [ ] requirements.txt lists all packages with == versions
- [ ] requirements.txt is committed

---

## 🌐 Task 3: Build Flask Web UI (src/app.py)

### Purpose
Create a web interface where users can type queries and see results with explanations (from Anthropic API).

### Key Rules
- ✅ Single Python file with inline HTML/CSS/JS (no separate files)
- ✅ Load index at app startup (NOT per-request)
- ✅ `/` route returns search interface
- ✅ `/search` POST route processes queries
- ✅ Never hardcode API key

### Implementation

```python
# File: src/app.py
# Owner: Person B
# Status: COMMIT ✓

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, request, jsonify, render_template_string
from src.retriever import load_index, retrieve
from src.rationale import get_rationale

# Initialize Flask app
app = Flask(__name__)

# CRITICAL: Load index at app startup (not per-request)
try:
    INDEX = load_index("data/tfidf_model.pkl")
    print("[✓] TF-IDF index loaded successfully")
except FileNotFoundError:
    print("[✗] Error: data/tfidf_model.pkl not found. Run 'python src/indexer.py' first.")
    INDEX = None

# HTML template (inline, no separate files)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BIS Standards Search</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            max-width: 700px;
            width: 100%;
        }
        h1 {
            font-size: 28px;
            color: #333;
            margin-bottom: 10px;
            text-align: center;
        }
        .subtitle {
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-bottom: 30px;
        }
        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px 16px;
            font-size: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            transition: border-color 0.3s;
            font-family: inherit;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            padding: 12px 28px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #5568d3;
        }
        button:active {
            transform: scale(0.98);
        }
        .results {
            margin-top: 20px;
        }
        .result-item {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 16px;
            margin-bottom: 12px;
            border-radius: 6px;
            animation: slideIn 0.3s ease-out;
        }
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .result-header {
            font-weight: 600;
            color: #333;
            margin-bottom: 6px;
            font-size: 16px;
        }
        .result-number {
            color: #667eea;
            font-weight: 700;
            margin-right: 6px;
        }
        .result-text {
            color: #666;
            font-size: 14px;
            line-height: 1.5;
        }
        .loading {
            text-align: center;
            color: #667eea;
            font-size: 15px;
            padding: 20px;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            margin: 10px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .error {
            background: #fee;
            border-left-color: #f00;
            color: #c00;
        }
        .latency {
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 BIS Standards Search</h1>
        <div class="subtitle">Find relevant Indian Standards for your product</div>
        
        <div class="search-box">
            <input 
                type="text" 
                id="query" 
                placeholder="e.g., Portland cement, coarse aggregate, ceramic tiles..."
                onkeypress="if(event.key==='Enter') search()"
            >
            <button onclick="search()">Search</button>
        </div>
        
        <div id="results"></div>
    </div>
    
    <script>
        async function search() {
            const query = document.getElementById('query').value.trim();
            if (!query) {
                alert('Please enter a search query');
                return;
            }
            
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Searching...</div>';
            
            try {
                const response = await fetch('/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="result-item error"><div class="result-header">Error</div><div class="result-text">${data.error}</div></div>`;
                } else {
                    let html = '<div class="results">';
                    data.results.forEach((item, idx) => {
                        html += `
                            <div class="result-item">
                                <div class="result-header">
                                    <span class="result-number">#${idx + 1}</span>${item.id}
                                </div>
                                <div class="result-text">${item.rationale}</div>
                            </div>
                        `;
                    });
                    html += '</div>';
                    html += `<div class="latency">⏱️ Response time: ${data.latency}s</div>`;
                    resultsDiv.innerHTML = html;
                }
            } catch (error) {
                resultsDiv.innerHTML = `<div class="result-item error"><div class="result-header">Error</div><div class="result-text">Failed to fetch results: ${error.message}</div></div>`;
            }
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    """Serve the search interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route("/search", methods=["POST"])
def search():
    """Process search query and return ranked results."""
    if INDEX is None:
        return jsonify({"error": "Index not loaded. Please run src/indexer.py first."}), 500
    
    try:
        data = request.json or {}
        query = data.get("query", "").strip()
        
        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400
        
        # Retrieve standards
        t0 = time.time()
        retrieved_ids = retrieve(query, INDEX, top_k=5)
        latency = round(time.time() - t0, 4)
        
        # Get rationale for each result
        results = []
        for std_id in retrieved_ids:
            rationale = get_rationale(query, std_id)
            results.append({
                "id": std_id,
                "rationale": rationale
            })
        
        return jsonify({
            "results": results,
            "latency": latency
        })
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    # Run Flask server
    print("[*] Starting BIS Standards Search Server...")
    print("[*] Open http://localhost:5000 in your browser")
    print("[*] Press Ctrl+C to stop the server")
    
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000,
        use_reloader=False  # Disable reloader to avoid loading index twice
    )
```

### Success Criteria for Task 3
- [ ] src/app.py loads INDEX at startup (not per-request)
- [ ] `/` route returns HTML search interface
- [ ] `/search` POST route accepts JSON with `query` key
- [ ] Returns JSON with `results` array and `latency` float
- [ ] No separate CSS/JS files created
- [ ] No hardcoded API key
- [ ] Flask runs without errors on `python src/app.py`

### Testing app.py

```bash
# 1. Ensure index exists
python src/indexer.py

# 2. Start Flask server
python src/app.py
# Output should show: "Running on http://127.0.0.1:5000"

# 3. In browser, go to: http://localhost:5000
# 4. Type a query: "cement"
# 5. Click Search
# 6. Verify results appear with explanations

# 7. Stop server: Ctrl+C
```

---

## 🧠 Task 4: Write Rationale Generator (src/rationale.py)

### Purpose
Call Anthropic's Claude API to generate one-sentence explanations of why each retrieved standard is relevant to the user's query.

### Key Rules
- ✅ Use `os.getenv("ANTHROPIC_API_KEY")` — never hardcode
- ✅ Graceful error handling
- ✅ Return placeholder if API fails
- ✅ Keep response short (< 120 tokens)

### Implementation

```python
# File: src/rationale.py
# Owner: Person B
# Status: COMMIT ✓

import os
import anthropic
from dotenv import load_dotenv

# Load .env file (reads ANTHROPIC_API_KEY from local .env)
load_dotenv()

def get_rationale(query: str, standard_id: str) -> str:
    """
    Generate a brief explanation of why a standard is relevant to the query.
    
    Args:
        query: User's search query (e.g., "Portland cement requirements")
        standard_id: BIS standard ID (e.g., "IS 269: 1989")
    
    Returns:
        One-sentence explanation (e.g., "This standard specifies requirements...")
    """
    try:
        # Get API key from environment
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return "(Anthropic API key not configured)"
        
        # Create Anthropic client
        client = anthropic.Anthropic(api_key=api_key)
        
        # Call Claude to generate rationale
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=120,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"User searched: \"{query}\"\n"
                        f"Retrieved standard: {standard_id}\n"
                        f"\n"
                        f"In ONE sentence, explain why this BIS Indian Standard is relevant to the user's search. "
                        f"Be specific and concise (max 20 words)."
                    )
                }
            ]
        )
        
        # Extract response text
        rationale = message.content[0].text.strip()
        return rationale
    
    except anthropic.APIError as e:
        # API errors (network, rate limit, etc.)
        print(f"[!] Anthropic API error: {e}")
        return "(Unable to generate explanation — API unavailable)"
    
    except KeyError as e:
        # Missing required fields in response
        print(f"[!] Response parsing error: {e}")
        return "(Unable to generate explanation — parsing failed)"
    
    except Exception as e:
        # Catch-all for unexpected errors
        print(f"[!] Unexpected error: {e}")
        return "(Unable to generate explanation)"

if __name__ == "__main__":
    # Quick test (requires valid API key in .env)
    test_query = "Portland cement"
    test_standard = "IS 269: 1989"
    
    result = get_rationale(test_query, test_standard)
    print(f"Query: {test_query}")
    print(f"Standard: {test_standard}")
    print(f"Rationale: {result}")
```

### Success Criteria for Task 4
- [ ] Uses `os.getenv("ANTHROPIC_API_KEY")` — no hardcoded key
- [ ] Returns string explanation for valid query + standard
- [ ] Handles API errors gracefully (returns placeholder)
- [ ] Loads dotenv on import
- [ ] Returns response in < 120 characters

### Testing rationale.py

```bash
# Create .env with real API key first
cp .env.example .env
# Edit .env and add your real Anthropic API key

# Run test
python -c "
from src.rationale import get_rationale
result = get_rationale('Portland cement', 'IS 269: 1989')
print(f'Result: {result}')
"
```

---

## 📖 Task 5: Write README.md

### Purpose
Complete documentation for judges and other users to set up and run the project.

### Implementation

```markdown
# BIS Standards Retrieval System

A Retrieval-Augmented Generation (RAG) pipeline that retrieves the top-5 most relevant Bureau of Indian Standards (BIS) specifications based on natural language queries.

## 🎯 Overview

This system indexes all ~600 BIS standards from BIS SP 21 (929-page handbook) and enables fast semantic search. Users query in natural language (e.g., "What standard covers Portland cement?") and receive ranked results with AI-generated explanations.

**Performance**: Hit Rate @3 ≥ 80%, MRR @5 ≥ 0.74, Latency < 5s per query.

## 📦 Requirements

- Python 3.9+
- No GPU required
- Tested on: Ubuntu 22.04, macOS 13, Windows 11

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/bis-standards-rag.git
cd bis-standards-rag
```

### 2. Set Up Python Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Build the Index (Run Once)

**Prerequisites**: Convert the PDF to text:
```bash
# macOS
brew install xpdf
pdftotext BIS_SP_21.pdf BIS_SP_21.txt

# Ubuntu/Debian
sudo apt-get install xpdf
pdftotext BIS_SP_21.pdf BIS_SP_21.txt

# Windows
# Download from: https://www.xpdfreader.com/
# Then run: pdftotext.exe BIS_SP_21.pdf BIS_SP_21.txt
```

**Build index**:
```bash
python src/ingest.py        # Extract 600+ standards from text
python src/indexer.py       # Build TF-IDF search index
```

### 4. Run Inference (Judges Use This)
```bash
python inference.py \
  --input data/public_test_set.json \
  --output data/public_results.json
```

### 5. Evaluate Results
```bash
python eval_script.py --results data/public_results.json
```

### 6. Run Web UI (Demo)
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key (optional for UI only)

python src/app.py
# Open http://localhost:5000 in your browser
```

## 📁 Project Structure

```
bis-standards-rag/
├── inference.py               # Entry point (judges run this)
├── eval_script.py             # Evaluation script (provided)
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── presentation.pdf           # 8-slide deck
├── .env.example               # Environment variables template
├── .env                       # Local only (NEVER commit)
│
├── src/
│   ├── ingest.py              # Parse PDF → chunks.json
│   ├── indexer.py             # Build TF-IDF index
│   ├── retriever.py           # Retrieve top-5 standards
│   ├── app.py                 # Flask web UI
│   └── rationale.py           # Anthropic API integration
│
└── data/
    ├── chunks.json            # Extracted standards (600+)
    ├── tfidf_model.pkl        # Serialized TF-IDF index
    ├── public_test_set.json   # Test queries (provided)
    └── public_results.json    # Inference results
```

## 🔍 Architecture

### Pipeline

1. **Ingestion** (`src/ingest.py`):
   - Parse BIS_SP_21.txt
   - Extract 600+ IS standard entries
   - Save to `data/chunks.json`

2. **Indexing** (`src/indexer.py`):
   - Build TF-IDF vectorizer (scikit-learn)
   - Create sparse matrix from chunks
   - Serialize to `data/tfidf_model.pkl`

3. **Retrieval** (`src/retriever.py`):
   - Expand queries with synonym dictionary
   - Compute cosine similarity
   - Return top-5 ranked standards

4. **Inference** (`inference.py`):
   - Load index once
   - Process all queries
   - Measure latency per query
   - Output JSON results

5. **Evaluation** (`eval_script.py`):
   - Compute Hit Rate @3
   - Compute MRR @5
   - Measure average latency

### Web UI (Optional Demo)

- Flask server (`src/app.py`)
- RESTful endpoint `/search` accepts queries
- Calls `src/rationale.py` for explanations
- No API calls needed for core inference

## 🔐 Configuration

### Environment Variables

Create `.env` file (never commit):

```
ANTHROPIC_API_KEY=sk-ant-XXXXXXXXXXXXXXXXXXXX
```

Get your key from: https://console.anthropic.com/account/keys

### Dependencies

All packages use exact pinned versions (see `requirements.txt`):
- scikit-learn: TF-IDF vectorization
- numpy: Numerical operations
- Flask: Web framework
- python-dotenv: Load .env variables
- anthropic: Claude API client

## 📊 Evaluation Metrics

Judges run `eval_script.py` which computes:

| Metric | Formula | Target |
|--------|---------|--------|
| **Hit Rate @3** | % queries with ≥1 match in top-3 | ≥ 0.80 |
| **MRR @5** | Mean reciprocal rank (top-5) | ≥ 0.74 |
| **Latency** | Avg seconds per query | < 5.0 |

## 🎬 Demo

See `presentation.pdf` (8 slides) for full demo walkthrough.

Or run the web UI:
```bash
python src/app.py
# Open http://localhost:5000
# Type a query like: "cement requirements"
# See results with AI-generated explanations
```

## 🤝 External APIs

- **Anthropic Claude API** (`claude-sonnet-4-20250514`):
  - Used in web UI only (`src/rationale.py`)
  - NOT used in core inference pipeline
  - Optional for demo
  - Required API key: https://console.anthropic.com/

- **Inference pipeline is completely offline** — no API calls needed.

## 📝 Attribution & Licensing

- **Dataset**: BIS SP 21 (Bureau of Indian Standards Handbook)
- **Standards**: ~600 IS specifications from BIS SP 21
- **License**: See LICENSE file

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'scikit_learn'"
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### "FileNotFoundError: BIS_SP_21.txt not found"
```bash
# Convert PDF first
pdftotext BIS_SP_21.pdf BIS_SP_21.txt
python src/ingest.py
python src/indexer.py
```

### "Error reading .env"
```bash
cp .env.example .env
# Only needed if running Flask app with explanations
# Not needed for core inference
```

### Low evaluation scores
- Check: Are 600+ standards extracted? (`python src/ingest.py`)
- Check: Is index built? (`python src/indexer.py`)
- Check: Are results valid JSON? (open `data/public_results.json`)
- Optimize: Tune `ngram_range` or `min_df` in `src/indexer.py`

## 👥 Team

- **Person A**: Backend pipeline (ingest → indexing → retrieval)
- **Person B**: Infrastructure & UI (setup → Flask → deployment)

## 📅 Timeline

- **Day 1**: Repository setup, git workflow
- **Day 2-3**: Core development (pipeline + UI in parallel)
- **Day 4**: Integration, testing, optimization
- **Day 5**: Final submission

---

**Last Updated**: May 2026  
**Status**: Production Ready  
**Contact**: See GitHub Issues for questions
```

### Success Criteria for Task 5
- [ ] README has all 8 sections
- [ ] Setup instructions are clear and complete
- [ ] Commands are copy-pasteable (not pseudocode)
- [ ] Project structure diagram matches actual files
- [ ] Troubleshooting section covers common issues

---

## 🎤 Task 6: Create Presentation (presentation.pdf)

### Slide Structure (Exactly 8 slides)

**Slide 1: Problem**
- What problem are we solving?
- Why does it matter?
- Example: "Manufacturers spend hours finding the right BIS standard"

**Slide 2: Solution**
- What's our approach?
- Key features
- High-level overview

**Slide 3: Architecture**
- System diagram with components
- Data flow: PDF → Index → Query → Results
- Technology stack

**Slide 4: Chunking Strategy**
- How we extract standards from PDF
- Data representation
- Sample chunks

**Slide 5: Demo**
- Live screenshot of web UI
- OR demo video walkthrough
- Show search → results → explanations

**Slide 6: Evaluation Results** ⭐ MUST BE REAL NUMBERS
- Hit Rate @3: _____ (get from eval_script.py)
- MRR @5: _____ (get from eval_script.py)
- Avg Latency: _____ (get from eval_script.py)
- Comparison: target vs achieved

**Slide 7: Impact**
- Use cases
- Business value
- Future enhancements

**Slide 8: Team**
- Person A: Name, Role, Contact
- Person B: Name, Role, Contact
- Acknowledgments

### Tools to Create Presentation
- **Google Slides**: Free, collaborative, easy to export as PDF
- **Canva**: Designer-friendly, templates available
- **PowerPoint**: Professional, local
- **Keynote**: Mac-friendly

### Export as PDF
- Google Slides: File → Download → PDF Document
- Canva: Click "Download" → PDF
- PowerPoint: File → Export → PDF
- Keynote: File → Export to → PDF

### Success Criteria for Task 6
- [ ] Exactly 8 slides
- [ ] Slides in correct order (Problem → Team)
- [ ] Slide 6 has REAL metrics (not placeholders)
- [ ] Professional appearance (consistent fonts, colors)
- [ ] Saved as `presentation.pdf` in repo root
- [ ] File is < 10 MB

### Committing Presentation

```bash
# Ensure presentation.pdf exists in repo root
git add presentation.pdf
git commit -m "Add 8-slide presentation deck"
git push origin main
```

---

## ✅ Pre-Submission Checklist (Person B)

Before final push, verify:

### Infrastructure
- [ ] Repository is PUBLIC (verified in incognito window)
- [ ] `.gitignore` is first commit
- [ ] `.env` is NOT in `git ls-files` output
- [ ] `.env.example` exists and is committed
- [ ] No __pycache__, *.pyc, or PDFs in repo

### Files
- [ ] requirements.txt with exact versions
- [ ] README.md complete (all sections)
- [ ] presentation.pdf has 8 slides
- [ ] src/app.py works locally
- [ ] src/rationale.py calls API correctly

### Web UI
- [ ] `python src/app.py` runs without errors
- [ ] Open http://localhost:5000 in browser
- [ ] Search interface appears
- [ ] Type a test query
- [ ] Results display with explanations
- [ ] Latency appears at bottom

### Git
- [ ] `git status` shows clean working tree
- [ ] `git log --oneline` shows 5+ commits
- [ ] All files are tracked: `git ls-files | wc -l`
- [ ] No uncommitted changes

### Collaboration
- [ ] Person A's files are present and working
- [ ] Person A's metrics meet targets
- [ ] No merge conflicts
- [ ] Both persons' names in presentation

---

## 🔄 Git Workflow for Person B

### Initial Setup (Day 0)

```bash
# Local setup
mkdir bis-standards-rag && cd bis-standards-rag
cat > .gitignore << 'EOF'
.env
__pycache__/
*.pyc
.venv/
venv/
BIS_SP_21.pdf
BIS_SP_21.txt
EOF

mkdir src data
git init
git add .gitignore
git commit -m "Add gitignore (security first)"

# ... create files ...

git add .
git commit -m "Initial structure"

# GitHub: Create public repo

git remote add origin https://github.com/USERNAME/bis-standards-rag.git
git branch -M main
git push -u origin main
```

### For Each Change

```bash
# 1. Make changes to your files
# 2. Check what changed
git status
git diff HEAD

# 3. Stage your files (by name, not ".")
git add requirements.txt src/app.py README.md

# 4. Commit
git diff --cached  # Review before committing
git commit -m "Add Flask UI and README"

# 5. Get Person A's changes
git pull origin main

# 6. Push
git push origin main
```

### Files You Own (Person B)

Always commit these after changes:
- src/app.py
- src/rationale.py
- README.md
- requirements.txt
- presentation.pdf
- .env.example
- .gitignore (created once, don't edit after)

---

## 📊 Final Verification Commands

Run these before final submission:

```bash
# 1. Full pipeline
python src/ingest.py
python src/indexer.py
python inference.py --input data/public_test_set.json --output data/public_results.json
python eval_script.py --results data/public_results.json

# 2. Web UI test
python src/app.py

# 3. Files check
git ls-files | sort

# 4. Repo check
git log --oneline | head -5
git status
```

---

**Last Updated**: May 2026  
**Status**: Active Development  
**Role**: Person B (Infrastructure & UI)
