#!/bin/bash
# UMIS Docker Run Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "========================================"
echo "  UMIS Docker Run"
echo "========================================"
echo ""

# Parse options
DETACH="-d"
REBUILD=""
LOGS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --foreground|-f)
            DETACH=""
            shift
            ;;
        --build)
            REBUILD="--build"
            shift
            ;;
        --logs)
            LOGS="true"
            shift
            ;;
        --down)
            echo "Stopping containers..."
            docker-compose down
            echo "Done."
            exit 0
            ;;
        --status)
            docker-compose ps
            exit 0
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -f, --foreground  Run in foreground (show logs)"
            echo "  --build           Rebuild before running"
            echo "  --logs            Show logs after starting"
            echo "  --down            Stop all containers"
            echo "  --status          Show container status"
            echo "  -h, --help        Show this help"
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
    echo "No .env file found, creating from environment..."

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
        echo "Created .env from template"
        echo "Warning: OPENAI_API_KEY not set in environment"
        echo "Please set it: export OPENAI_API_KEY=sk-..."
    else
        echo "Error: No .env, no environment variable, no template"
        exit 1
    fi
fi

# Export environment variables for docker-compose
if [ -n "$OPENAI_API_KEY" ]; then
    export OPENAI_API_KEY
    echo "Using OPENAI_API_KEY from environment"
fi

# Check OPENAI_API_KEY availability
if [ -z "$OPENAI_API_KEY" ] && ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    echo "Warning: OPENAI_API_KEY not configured"
    echo "RAG index build will be skipped without API key"
    echo ""
fi

# Start containers
echo "Starting UMIS containers..."
docker-compose up $DETACH $REBUILD

if [ -n "$DETACH" ]; then
    echo ""
    echo "========================================"
    echo "  UMIS Running!"
    echo "========================================"
    echo ""
    echo "Commands:"
    echo "  docker-compose logs -f umis      # View logs"
    echo "  docker-compose exec umis bash    # Enter container"
    echo "  docker-compose ps                # Check status"
    echo "  docker-compose down              # Stop all"
    echo ""
    echo "RAG Query:"
    echo "  docker-compose exec umis python scripts/query_rag.py \"query\""
    echo ""
    echo "Neo4j Browser:"
    echo "  http://localhost:7474"
    echo ""

    if [ "$LOGS" = "true" ]; then
        echo "Following logs..."
        docker-compose logs -f umis
    fi
fi
