#!/usr/bin/env python3
"""
Component 2: Indexer (PERSON A)
Build TF-IDF index from chunks.json → tfidf_model.pkl

Usage:
    python src/indexer.py

Input:  chunks.json
Output: tfidf_model.pkl
"""

import json
import pickle
import os
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from dotenv import load_dotenv

load_dotenv()

CHUNKS_PATH = os.getenv('CHUNKS_PATH', './chunks.json')
MODEL_PATH = os.getenv('MODEL_PATH', './tfidf_model.pkl')


def build_tfidf_index(chunks):
    """
    Build TF-IDF matrix from chunk texts.

    Returns:
        vectorizer: Fitted TfidfVectorizer
        tfidf_matrix: Sparse matrix (n_chunks x vocab_size)
    """
    corpus = [chunk['text'] for chunk in chunks]

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),       # unigrams + bigrams for better phrase matching
        sublinear_tf=True,        # log(1+tf) to reduce dominance of frequent terms
        max_features=100000,      # large vocab for domain coverage
        min_df=1,                 # keep rare IS-specific terms
        analyzer='word',
        token_pattern=r'(?u)\b[A-Za-z0-9][A-Za-z0-9\-\.]+\b',
    )

    tfidf_matrix = vectorizer.fit_transform(corpus)

    print(f"  Vocabulary size : {len(vectorizer.vocabulary_)}")
    print(f"  Matrix shape    : {tfidf_matrix.shape}")
    print(f"  Matrix density  : {tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1]):.4f}")

    return vectorizer, tfidf_matrix


def main():
    """Main indexing pipeline."""
    # Validate input
    if not os.path.exists(CHUNKS_PATH):
        print(f"ERROR: chunks.json not found at '{CHUNKS_PATH}'")
        print("Run first: python src/ingest.py")
        sys.exit(1)

    print(f"Step 1: Loading chunks from {CHUNKS_PATH} ...")
    with open(CHUNKS_PATH, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    print(f"  Loaded {len(chunks)} chunks")

    print("Step 2: Building TF-IDF index ...")
    vectorizer, tfidf_matrix = build_tfidf_index(chunks)

    print(f"Step 3: Saving model to {MODEL_PATH} ...")
    model_data = {
        'vectorizer': vectorizer,
        'tfidf_matrix': tfidf_matrix,
        'chunks': chunks           # Store chunks inside model for easy loading
    }
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model_data, f, protocol=pickle.HIGHEST_PROTOCOL)

    size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
    print(f"\nDone! Model saved to {MODEL_PATH} ({size_mb:.1f} MB)")
    print("Next step: python inference.py --input public_test_set.json --output results.json")


if __name__ == "__main__":
    main()
