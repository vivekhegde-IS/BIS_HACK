#!/usr/bin/env python3
"""
Component: Flask Web UI (PERSON B)
Web interface for BIS Standards RAG

Usage:
    python src/app.py
    # Open: http://localhost:5000
"""

from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    """Serve web UI."""
    pass


@app.route('/api/search', methods=['POST'])
def api_search():
    """API endpoint for search."""
    pass


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
