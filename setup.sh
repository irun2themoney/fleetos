#!/bin/bash

################################################################################
# FleetOS Phase 1: Automated Setup Script
#
# This script automates the entire Phase 1 setup process.
# Run this once after cloning the repository.
#
# Usage: bash setup.sh
#
# Requirements:
#   - Python 3.10+
#   - Docker & Docker Compose
#   - 8GB+ RAM
#   - 20GB+ disk space
#
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║     FleetOS Phase 1: Automated Setup & Configuration      ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check prerequisites
echo -e "${YELLOW}[1/6] Checking prerequisites...${NC}"

if ! command -v python3.10 &> /dev/null; then
    echo -e "${RED}❌ Python 3.10 not found${NC}"
    echo "Please install Python 3.10 from https://python.org"
    exit 1
fi
echo -e "${GREEN}✓ Python 3.10 found${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found${NC}"
    echo "Please install Docker from https://docker.com"
    exit 1
fi
echo -e "${GREEN}✓ Docker found${NC}"

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found${NC}"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose found${NC}"

# Create virtual environment
echo -e "${YELLOW}[2/6] Creating Python virtual environment...${NC}"

if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping creation"
else
    python3.10 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Install dependencies
echo -e "${YELLOW}[3/6] Installing Python dependencies...${NC}"

pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Setup environment
echo -e "${YELLOW}[4/6] Setting up environment configuration...${NC}"

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file from template${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env file to add your settings:${NC}"
    echo "   nano .env  (or your preferred editor)"
    echo ""
else
    echo "✓ .env file already exists"
fi

# Start Docker services
echo -e "${YELLOW}[5/6] Starting Docker services (Ollama, Redis, Chroma, etc.)...${NC}"

docker-compose down > /dev/null 2>&1 || true
docker-compose up -d

echo -e "${GREEN}✓ Docker services started${NC}"

# Wait for services to be ready
echo -e "${YELLOW}[6/6] Waiting for services to be healthy...${NC}"

sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Services are running${NC}"
else
    echo -e "${YELLOW}⚠️  Some services may not be healthy yet${NC}"
    echo "   Wait a moment and check again: docker-compose ps"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ PHASE 1 SETUP COMPLETE!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

echo "NEXT STEPS:"
echo ""
echo "1. PULL OLLAMA MODEL (this takes 5-10 minutes for the 70B model):"
echo "   ${YELLOW}ollama pull llama3.1:70b${NC}"
echo ""
echo "   Or if you have limited disk space, use the smaller model:"
echo "   ${YELLOW}ollama pull llama3.1:13b${NC}"
echo "   Then update .env: OLLAMA_MODEL=llama3.1:13b"
echo ""
echo "2. TEST THE SETUP:"
echo "   ${YELLOW}python -m fleetos.cli --help${NC}"
echo "   ${YELLOW}python -m fleetos.cli status${NC}"
echo "   ${YELLOW}python -m fleetos.cli run \"Tell me about yourself\"${NC}"
echo ""
echo "3. VERIFY DOCKER SERVICES:"
echo "   ${YELLOW}docker-compose ps${NC}"
echo ""
echo "4. VIEW LOGS (if troubleshooting):"
echo "   ${YELLOW}docker-compose logs -f ollama${NC}"
echo "   ${YELLOW}docker-compose logs -f fleetos${NC}"
echo ""
echo "IMPORTANT:"
echo "  • Keep Docker running: ${YELLOW}docker-compose up -d${NC}"
echo "  • Activate venv each session: ${YELLOW}source venv/bin/activate${NC}"
echo "  • Virtual environment is in: ${YELLOW}./venv${NC}"
echo ""
echo -e "${GREEN}Ready to test? Try: python -m fleetos.cli status${NC}"
echo ""
