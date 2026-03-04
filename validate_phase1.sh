#!/bin/bash

################################################################################
# FleetOS Phase 1: Validation & Testing Script
#
# This script validates that Phase 1 setup is complete and working.
# Run this after running setup.sh and pulling the Ollama model.
#
# Usage: bash validate_phase1.sh
#
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║      FleetOS Phase 1: Validation & Health Check            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Array to track results
declare -a CHECKS
TOTAL=0
PASSED=0

# Helper function
check_item() {
    local name=$1
    local cmd=$2

    echo -n "Checking $name... "
    TOTAL=$((TOTAL + 1))

    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        PASSED=$((PASSED + 1))
        CHECKS+=("✓ $name")
    else
        echo -e "${RED}✗ FAIL${NC}"
        CHECKS+=("✗ $name")
    fi
}

echo ""
echo -e "${YELLOW}Running validation checks...${NC}"
echo ""

# Check 1: Virtual environment
check_item "Virtual environment activated" "[ -n '\$VIRTUAL_ENV' ]"

# Check 2: Python version
check_item "Python 3.10+" "python --version | grep -qE '3\.(10|11|12)'"

# Check 3: Dependencies
check_item "langgraph installed" "pip show langgraph > /dev/null"
check_item "streamlit installed" "pip show streamlit > /dev/null"
check_item "chromadb installed" "pip show chromadb > /dev/null"
check_item "pydantic installed" "pip show pydantic > /dev/null"

# Check 4: Docker services
check_item "Docker running" "docker ps > /dev/null"
check_item "Docker Compose" "docker-compose version > /dev/null"

# Check 5: Services running
check_item "Ollama service running" "docker-compose ps | grep ollama | grep -q Up"
check_item "Redis service running" "docker-compose ps | grep redis | grep -q Up"
check_item "Chroma service running" "docker-compose ps | grep chroma | grep -q Up"

# Check 6: Ollama connectivity
check_item "Ollama endpoint accessible" "curl -s http://localhost:11434/api/tags > /dev/null"

# Check 7: Ollama model downloaded
check_item "Ollama model downloaded" "ollama list | grep -qE 'llama|dolphin'"

# Check 8: Python modules
check_item "fleetos.core.planner module" "python -c 'from fleetos.core.planner import Planner' 2>/dev/null"
check_item "fleetos.core.orchestrator module" "python -c 'from fleetos.core.orchestrator import Orchestrator' 2>/dev/null"
check_item "fleetos.core.memory module" "python -c 'from fleetos.core.memory import MemoryManager' 2>/dev/null"
check_item "fleetos.core.verifier module" "python -c 'from fleetos.core.verifier import Verifier' 2>/dev/null"

# Check 9: CLI
check_item "CLI accessible" "python -m fleetos.cli --help > /dev/null 2>&1"

# Check 10: Environment file
check_item ".env file exists" "[ -f .env ]"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}VALIDATION RESULTS: $PASSED/$TOTAL passed${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Print detailed results
for check in "${CHECKS[@]}"; do
    echo "$check"
done

echo ""

if [ $PASSED -eq $TOTAL ]; then
    echo -e "${GREEN}🎉 ALL CHECKS PASSED - PHASE 1 IS READY!${NC}"
    echo ""
    echo "You can now:"
    echo "  1. Test CLI: ${YELLOW}python -m fleetos.cli status${NC}"
    echo "  2. Run a command: ${YELLOW}python -m fleetos.cli run \"test\"${NC}"
    echo "  3. Search memory: ${YELLOW}python -m fleetos.cli search \"test\"${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}⚠️  Some checks failed. See details above.${NC}"
    echo ""
    echo "Troubleshooting steps:"
    echo "  1. Check Docker is running: ${YELLOW}docker ps${NC}"
    echo "  2. Check service status: ${YELLOW}docker-compose ps${NC}"
    echo "  3. View logs: ${YELLOW}docker-compose logs ollama${NC}"
    echo "  4. Verify virtual env: ${YELLOW}source venv/bin/activate${NC}"
    echo ""
    exit 1
fi
