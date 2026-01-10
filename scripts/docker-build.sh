#!/bin/bash
# UMIS Docker Build Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "========================================"
echo "  UMIS Docker Build"
echo "========================================"
echo ""

# Parse options
NO_CACHE=""
TAG="latest"

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --no-cache    Build without cache"
            echo "  --tag TAG     Docker image tag (default: latest)"
            echo "  -h, --help    Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check .env file and create from environment if needed
if [ ! -f ".env" ]; then
    echo "No .env file found, creating..."

    if [ -n "$OPENAI_API_KEY" ]; then
        # Create .env from current environment
        cat > .env << EOF
# Auto-generated from environment
OPENAI_API_KEY=${OPENAI_API_KEY}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
LLM_MODE=${LLM_MODE:-cursor}
NEO4J_PASSWORD=${NEO4J_PASSWORD:-***REMOVED***}
AUTO_BUILD_RAG=true
EOF
        echo "Created .env with OPENAI_API_KEY from environment"
    elif [ -f "env.template" ]; then
        cp env.template .env
        echo "Created .env from env.template"
        echo "Please set OPENAI_API_KEY: export OPENAI_API_KEY=sk-..."
    else
        echo "Error: env.template not found"
        exit 1
    fi
fi

# Export environment variables for docker-compose
if [ -n "$OPENAI_API_KEY" ]; then
    export OPENAI_API_KEY
fi

# Build
echo "Building Docker image: umis:$TAG"
echo ""
docker-compose build $NO_CACHE umis

echo ""
echo "========================================"
echo "  Build Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Set API key: export OPENAI_API_KEY=sk-..."
echo "  2. Run: ./scripts/docker-run.sh"
echo ""
