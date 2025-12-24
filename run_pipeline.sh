#!/usr/bin/env bash
# AI Job Market - Notebook Pipeline Executor
# Bash script for Linux/Mac to run the notebook orchestration pipeline

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}======================================================================${NC}"
echo -e "${CYAN}  AI JOB MARKET - NOTEBOOK PIPELINE${NC}"
echo -e "${CYAN}======================================================================${NC}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found. Please install Python first.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ Python found: ${PYTHON_VERSION}${NC}"
echo ""

# Change to script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}📂 Working directory: ${SCRIPT_DIR}${NC}"
echo ""

# Show pipeline stages
echo -e "${CYAN}📋 Pipeline Stages:${NC}"
echo "  1. cleaning.ipynb (Data Cleaning & Enrichment)"
echo "  2. exploration.ipynb (Exploratory Data Analysis)"
echo "  3. salary_intelligence_analysis.ipynb (Salary Analysis)"
echo ""

# Confirmation
read -p "Execute full pipeline? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Pipeline execution cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}🚀 Starting pipeline execution...${NC}"
echo ""

# Run pipeline
if python3 run_pipeline.py; then
    echo ""
    echo -e "${GREEN}✅ Pipeline completed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}📊 Check output/logs/ for execution reports${NC}"
    echo -e "${YELLOW}📓 Executed notebooks saved to output/executed_notebooks/${NC}"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}❌ Pipeline failed with errors.${NC}"
    echo ""
    exit 1
fi
