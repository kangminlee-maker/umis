#!/bin/bash
# UMIS Docker Entrypoint Script
set -e

echo "========================================"
echo "  UMIS Container Starting..."
echo "  Version: $(cat /app/VERSION.txt 2>/dev/null || echo 'unknown')"
echo "========================================"

# ============================================
# 1. Environment Variable Check
# ============================================
check_env() {
    echo ""
    echo "[1/3] Checking environment variables..."

    if [ -z "$OPENAI_API_KEY" ]; then
        echo "  Warning: OPENAI_API_KEY not set"
        echo "  RAG index build will be skipped"
        export HAS_API_KEY="false"
    else
        echo "  OPENAI_API_KEY: configured"
        export HAS_API_KEY="true"
    fi

    echo "  LLM_MODE: ${LLM_MODE:-cursor}"
    echo "  CHROMA_PERSIST_DIR: ${CHROMA_PERSIST_DIR:-/app/data/chroma}"
    echo "  AUTO_BUILD_RAG: ${AUTO_BUILD_RAG:-true}"
}

# ============================================
# 2. Wait for Neo4j (if configured)
# ============================================
wait_for_neo4j() {
    if [ "$WAIT_FOR_NEO4J" = "true" ] && [ -n "$NEO4J_URI" ]; then
        echo ""
        echo "[2/3] Waiting for Neo4j..."

        MAX_RETRIES=30
        RETRY_COUNT=0

        while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
            if python -c "
from neo4j import GraphDatabase
try:
    driver = GraphDatabase.driver('$NEO4J_URI', auth=('${NEO4J_USER:-neo4j}', '${NEO4J_PASSWORD:-***REMOVED***}'))
    driver.verify_connectivity()
    driver.close()
    print('OK')
except Exception as e:
    exit(1)
" 2>/dev/null; then
                echo "  Neo4j connected successfully"
                return 0
            fi

            RETRY_COUNT=$((RETRY_COUNT + 1))
            echo "  Waiting for Neo4j... ($RETRY_COUNT/$MAX_RETRIES)"
            sleep 2
        done

        echo "  Warning: Neo4j not available (continuing without it)"
    else
        echo ""
        echo "[2/3] Skipping Neo4j wait (WAIT_FOR_NEO4J=${WAIT_FOR_NEO4J:-false})"
    fi
}

# ============================================
# 3. Build RAG Index (first run only)
# ============================================
build_rag_index() {
    echo ""
    echo "[3/3] Checking RAG index..."

    CHROMA_DB="${CHROMA_PERSIST_DIR:-/app/data/chroma}/chroma.sqlite3"

    if [ -f "$CHROMA_DB" ]; then
        echo "  RAG index already exists"
        return 0
    fi

    if [ "$AUTO_BUILD_RAG" != "true" ]; then
        echo "  AUTO_BUILD_RAG=false, skipping build"
        return 0
    fi

    if [ "$HAS_API_KEY" != "true" ]; then
        echo "  No API key, skipping RAG build"
        return 0
    fi

    echo "  Building RAG index (first run)..."
    echo "  This may take 1-2 minutes..."

    # Step 1: YAML to JSONL conversion
    echo ""
    echo "  [Step 1/2] Converting YAML to JSONL..."
    python /app/scripts/01_convert_yaml.py

    # Step 2: Build vector index
    echo ""
    echo "  [Step 2/2] Building vector index..."
    python /app/scripts/02_build_index.py --agent explorer

    echo ""
    echo "  RAG index built successfully!"
}

# ============================================
# Main
# ============================================
check_env
wait_for_neo4j
build_rag_index

echo ""
echo "========================================"
echo "  UMIS Ready!"
echo "========================================"
echo ""
echo "Usage:"
echo "  docker-compose exec umis python scripts/query_rag.py \"query\""
echo ""

# Execute passed command
exec "$@"
