#!/bin/bash
# Galani Protocol - Complete Setup & GitHub Push Script
# This script reorganizes the repository and pushes to GitHub

set -e  # Exit on error

echo "============================================"
echo "Galani Protocol v2.0 - Setup & Deployment"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is not installed${NC}"
    exit 1
fi

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo -e "${RED}Error: Not a git repository. Please run 'git init' first${NC}"
    exit 1
fi

echo -e "${GREEN}Step 1: Creating new directory structure...${NC}"

# Create new structure
mkdir -p src/galani/{core,domains,governance,api,utils}
mkdir -p tests/{unit,integration,load,benchmarks}
mkdir -p docs/{architecture,api,guides}
mkdir -p examples/{fintech,medtech,retail,govtech}
mkdir -p deployments/{kubernetes,docker,terraform}
mkdir -p scripts/{setup,migration,monitoring}
mkdir -p .github/workflows

echo -e "${GREEN}Step 2: Organizing existing files...${NC}"

# Move demo files to examples
if ls *_demo.py 1> /dev/null 2>&1; then
    mv fintech*demo*.py examples/fintech/ 2>/dev/null || true
    mv medtech*demo*.py examples/medtech/ 2>/dev/null || true
    mv ecommerce*demo*.py examples/retail/ 2>/dev/null || true
    mv d2c*demo*.py examples/retail/ 2>/dev/null || true
    mv govtech*demo*.py examples/govtech/ 2>/dev/null || true
    mv banking*demo*.py examples/fintech/ 2>/dev/null || true
    mv insurtech*demo*.py examples/fintech/ 2>/dev/null || true
    mv legaltech*demo*.py examples/govtech/ 2>/dev/null || true
    mv energy*demo*.py examples/govtech/ 2>/dev/null || true
fi

# Move core engine files
if ls *engine*.py 1> /dev/null 2>&1; then
    mv *engine*.py src/galani/core/ 2>/dev/null || true
fi

# Move governance files
if ls *policy*.py 1> /dev/null 2>&1; then
    mv *policy*.py src/galani/governance/ 2>/dev/null || true
fi

# Move audit files
if ls audit*.py 1> /dev/null 2>&1; then
    mv audit*.py src/galani/core/ 2>/dev/null || true
fi

# Move API files
if ls app.py 1> /dev/null 2>&1; then
    mv app.py src/galani/api/ 2>/dev/null || true
fi

# Move test files
if ls test*.py 1> /dev/null 2>&1; then
    mv test*.py tests/ 2>/dev/null || true
fi

# Move router files
if [ -d routers ]; then
    mv routers/* src/galani/api/ 2>/dev/null || true
    rmdir routers 2>/dev/null || true
fi

echo -e "${GREEN}Step 3: Creating configuration files...${NC}"

# Create .gitignore
cat > .gitignore << 'EOF'
# Secrets
api_keys.json
*.env
.env.*
dump.rdb
*.pem
*.key

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/
*.egg-info/
dist/
build/
.eggs/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
coverage.xml
*.cover

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Logs
*.log
logs/
audit.log

# Database
*.db
*.sqlite
*.rdb

# Temporary
*.tmp
*.bak
.cache/

# Node modules (if any JS tools used)
node_modules/

# Terraform
.terraform/
*.tfstate
*.tfstate.backup
