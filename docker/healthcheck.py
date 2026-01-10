#!/usr/bin/env python3
"""
UMIS Docker Healthcheck Script
"""

import sys
import os


def check_health():
    """Check UMIS container health status."""
    errors = []
    warnings = []

    # 1. Module import test
    try:
        import umis_rag
        version = getattr(umis_rag, '__version__', 'unknown')
        print(f"[OK] umis_rag module loaded (v{version})")
    except ImportError as e:
        errors.append(f"[FAIL] Cannot import umis_rag: {e}")

    # 2. ChromaDB connection test
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_PERSIST_DIR", "/app/data/chroma")

        if os.path.exists(chroma_path):
            client = chromadb.PersistentClient(path=chroma_path)
            collections = client.list_collections()
            print(f"[OK] ChromaDB: {len(collections)} collection(s)")
        else:
            warnings.append(f"[WARN] ChromaDB path not found: {chroma_path}")
    except Exception as e:
        errors.append(f"[FAIL] ChromaDB error: {e}")

    # 3. Environment variables check
    if os.getenv("OPENAI_API_KEY"):
        print("[OK] OPENAI_API_KEY configured")
    else:
        warnings.append("[WARN] OPENAI_API_KEY not set")

    # 4. Data directories check
    data_dirs = ["/app/data/chroma", "/app/data/chunks", "/app/logs"]
    for d in data_dirs:
        if os.path.isdir(d):
            print(f"[OK] Directory exists: {d}")
        else:
            warnings.append(f"[WARN] Directory missing: {d}")

    # Print warnings
    for w in warnings:
        print(w)

    # Print errors and exit
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    print("[OK] UMIS is healthy")
    return 0


if __name__ == "__main__":
    sys.exit(check_health())
