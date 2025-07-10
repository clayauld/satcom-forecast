#!/bin/bash

# 🔧 SatCom Forecast Pre-commit Setup Script
# This script automates the setup of pre-commit hooks for code quality

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 SatCom Forecast Pre-commit Setup${NC}"
echo "=================================="

# Check if we're in the right directory
if [ ! -f ".pre-commit-config.yaml" ]; then
    echo -e "${RED}❌ Error: .pre-commit-config.yaml not found${NC}"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Check Python version
echo -e "${YELLOW}🔍 Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}🔄 Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}📈 Upgrading pip...${NC}"
pip install --upgrade pip

# Install pre-commit
echo -e "${YELLOW}📥 Installing pre-commit...${NC}"
pip install pre-commit

# Install project dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}📥 Installing project dependencies...${NC}"
    pip install -r requirements.txt
else
    echo -e "${YELLOW}⚠️  No requirements.txt found, installing basic dependencies...${NC}"
    pip install black isort flake8 mypy bandit pytest pytest-cov
fi

# Install additional type stubs for mypy
echo -e "${YELLOW}📥 Installing type stubs...${NC}"
pip install types-aiofiles types-requests || echo -e "${YELLOW}⚠️  Some type stubs may not be available${NC}"

# Install pre-commit hooks
echo -e "${YELLOW}🪝 Installing pre-commit hooks...${NC}"
pre-commit install

# Optionally install pre-push hooks
read -p "Do you want to install pre-push hooks? (y/N): " install_prepush
if [[ $install_prepush =~ ^[Yy]$ ]]; then
    pre-commit install --hook-type pre-push
    echo -e "${GREEN}✅ Pre-push hooks installed${NC}"
fi

# Update hooks to latest versions
echo -e "${YELLOW}🔄 Updating hooks to latest versions...${NC}"
pre-commit autoupdate

# Test the setup
echo -e "${YELLOW}🧪 Testing pre-commit setup...${NC}"
echo "Running pre-commit on all files (this may take a few minutes)..."

if pre-commit run --all-files; then
    echo -e "${GREEN}✅ All pre-commit checks passed!${NC}"
else
    echo -e "${YELLOW}⚠️  Some pre-commit checks failed. This is normal for the first run.${NC}"
    echo "Pre-commit has likely auto-fixed some formatting issues."
    echo "Review the changes and commit them if they look good."
fi

# Display summary
echo -e "\n${BLUE}📋 Setup Summary${NC}"
echo "=================="
echo -e "${GREEN}✅ Virtual environment: venv${NC}"
echo -e "${GREEN}✅ Pre-commit installed and configured${NC}"
echo -e "${GREEN}✅ Git hooks installed${NC}"
echo -e "${GREEN}✅ Dependencies installed${NC}"

echo -e "\n${BLUE}🎯 Next Steps${NC}"
echo "=============="
echo "1. Review any changes made by pre-commit"
echo "2. Stage and commit the auto-fixed files:"
echo -e "   ${YELLOW}git add .${NC}"
echo -e "   ${YELLOW}git commit -m \"Apply pre-commit formatting\"${NC}"
echo "3. Start developing! Pre-commit will now run automatically on each commit."

echo -e "\n${BLUE}📚 Useful Commands${NC}"
echo "=================="
echo -e "${YELLOW}# Run pre-commit manually${NC}"
echo "pre-commit run --all-files"
echo ""
echo -e "${YELLOW}# Run specific hooks${NC}"
echo "pre-commit run black"
echo "pre-commit run flake8"
echo ""
echo -e "${YELLOW}# Skip hooks for emergency commits${NC}"
echo "git commit --no-verify -m \"Emergency fix\""
echo ""
echo -e "${YELLOW}# Update hooks${NC}"
echo "pre-commit autoupdate"

echo -e "\n${GREEN}🎉 Pre-commit setup complete!${NC}"
echo -e "See ${YELLOW}PRE_COMMIT_SETUP.md${NC} for detailed documentation."