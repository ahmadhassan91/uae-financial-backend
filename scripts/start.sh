#!/bin/bash

# Quick Start Script - UAE Financial Health Check Backend
# For developers who already have the environment set up

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  UAE Financial Health Check - Quick Start${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Navigate to backend directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$BACKEND_DIR"

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo -e "${BLUE}⚠️  Virtual environment not found. Running full setup...${NC}"
    bash scripts/setup_backend.sh
    exit 0
fi

echo -e "${GREEN}✅ Activating virtual environment...${NC}"
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${BLUE}⚠️  .env file not found. Please create it from .env.example${NC}"
    echo "  cp .env.example .env"
    echo "  # Then edit .env with your configuration"
    exit 1
fi

# Start the server
echo ""
echo -e "${GREEN}🚀 Starting FastAPI server...${NC}"
echo ""
echo -e "${BLUE}  API:  http://localhost:8000${NC}"
echo -e "${BLUE}  Docs: http://localhost:8000/docs${NC}"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
