#!/bin/bash

# Migration Diagnostics Script
# Helps identify why 'make migrate' might be failing

set -e

echo "🔍 Migration Diagnostics"
echo "======================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "1. Checking project structure..."
if [ -f "Makefile" ]; then
    check_pass "Makefile found (in project root)"
else
    check_fail "Makefile not found - are you in project root?"
    echo "   Current directory: $(pwd)"
    exit 1
fi

if [ -d "backend" ]; then
    check_pass "backend/ directory exists"
else
    check_fail "backend/ directory not found"
    exit 1
fi

echo ""
echo "2. Checking Poetry installation..."
if command -v poetry &> /dev/null; then
    POETRY_VERSION=$(poetry --version 2>&1 || echo "error")
    if [[ "$POETRY_VERSION" == *"error"* ]] || [[ "$POETRY_VERSION" == *"Permission"* ]]; then
        check_warn "Poetry found but has issues: $POETRY_VERSION"
    else
        check_pass "Poetry installed: $POETRY_VERSION"
    fi
else
    check_fail "Poetry not installed"
    echo "   Install: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

echo ""
echo "3. Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    check_pass "Python installed: $PYTHON_VERSION"
    
    # Extract version number
    PY_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
    PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
    
    if [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 11 ]; then
        check_pass "Python version >= 3.11 ✓"
    else
        check_warn "Python version < 3.11 (recommended: 3.11+)"
    fi
else
    check_fail "Python3 not found"
    exit 1
fi

echo ""
echo "4. Checking environment configuration..."
if [ -f ".env" ]; then
    check_pass ".env file exists"
    
    if grep -q "SECRET_KEY=" .env && ! grep -q "SECRET_KEY=your-secret" .env; then
        check_pass "SECRET_KEY is set"
    else
        check_warn "SECRET_KEY not set or using default"
        echo "   Run: make setup"
    fi
else
    check_fail ".env file not found"
    echo "   Run: make setup"
fi

if [ -f ".env.example" ]; then
    check_pass ".env.example exists"
else
    check_warn ".env.example not found"
fi

echo ""
echo "5. Checking backend structure..."
if [ -f "backend/pyproject.toml" ]; then
    check_pass "backend/pyproject.toml exists"
else
    check_fail "backend/pyproject.toml not found"
    exit 1
fi

if [ -f "backend/alembic.ini" ]; then
    check_pass "backend/alembic.ini exists"
else
    check_fail "backend/alembic.ini not found"
    exit 1
fi

if [ -d "backend/alembic/versions" ]; then
    check_pass "backend/alembic/versions/ directory exists"
    
    MIGRATION_COUNT=$(ls -1 backend/alembic/versions/*.py 2>/dev/null | wc -l | tr -d ' ')
    if [ "$MIGRATION_COUNT" -gt 0 ]; then
        check_pass "Found $MIGRATION_COUNT migration file(s)"
    else
        check_warn "No migration files found"
    fi
else
    check_fail "backend/alembic/versions/ not found"
fi

echo ""
echo "6. Checking dependencies installation..."
if [ -f "backend/poetry.lock" ]; then
    check_pass "poetry.lock exists"
else
    check_fail "poetry.lock not found - dependencies not installed"
    echo "   Run: cd backend && poetry install"
    exit 1
fi

cd backend
if poetry run python -c "import alembic" 2>/dev/null; then
    check_pass "alembic package is installed"
else
    check_fail "alembic package not found"
    echo "   Run: cd backend && poetry install"
    cd ..
    exit 1
fi

if poetry run python -c "from app.db.base import Base" 2>/dev/null; then
    check_pass "app.db.base imports successfully"
else
    check_fail "Cannot import app.db.base"
    echo "   Check __init__.py files exist in app/ directories"
fi

if poetry run python -c "from app.models.user import User" 2>/dev/null; then
    check_pass "app.models.user imports successfully"
else
    check_fail "Cannot import app.models.user"
fi

cd ..

echo ""
echo "7. Checking database status..."
if [ -f "backend/app.db" ]; then
    DB_SIZE=$(ls -lh backend/app.db | awk '{print $5}')
    check_pass "Database exists (size: $DB_SIZE)"
    
    # Check if it's locked
    if lsof backend/app.db 2>/dev/null | grep -q app.db; then
        check_warn "Database is currently in use"
    fi
else
    check_warn "Database doesn't exist yet (will be created on first migration)"
fi

echo ""
echo "8. Running migration check..."
cd backend
ALEMBIC_STATUS=$(poetry run alembic current 2>&1 || echo "error")
cd ..

if [[ "$ALEMBIC_STATUS" == *"error"* ]] || [[ "$ALEMBIC_STATUS" == *"Error"* ]]; then
    check_fail "Alembic status check failed"
    echo "   Error: $ALEMBIC_STATUS"
else
    check_pass "Alembic can connect"
    echo "   Current version: $ALEMBIC_STATUS"
fi

echo ""
echo "=== Summary ==="
echo ""
echo "If all checks passed, try running:"
echo "  make migrate"
echo ""
echo "If you see errors above, refer to:"
echo "  docs/MIGRATION_TROUBLESHOOTING.md"
echo ""
echo "Common fixes:"
echo "  - Dependencies not installed:  make install-backend"
echo "  - No .env file:               make setup"
echo "  - Database locked:            rm backend/app.db && make migrate"
echo "  - Import errors:              Check __init__.py files"
echo ""

