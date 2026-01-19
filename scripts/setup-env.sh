#!/bin/bash

# Script to generate .env file from .env.example with secure SECRET_KEY
# Usage: ./scripts/setup-env.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔧 Environment Setup Script"
echo "============================"
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file already exists!${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled."
        exit 0
    fi
fi

# Check if .env.example exists
if [ ! -f .env.example ]; then
    echo -e "${RED}❌ Error: .env.example file not found!${NC}"
    exit 1
fi

# Check if Python is available for generating SECRET_KEY
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Error: Python not found. Please install Python to generate secure SECRET_KEY.${NC}"
    exit 1
fi

# Generate secure SECRET_KEY
echo "🔐 Generating secure SECRET_KEY..."
SECRET_KEY=$($PYTHON_CMD -c "import secrets; print(secrets.token_urlsafe(32))")

if [ -z "$SECRET_KEY" ]; then
    echo -e "${RED}❌ Error: Failed to generate SECRET_KEY${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Generated SECRET_KEY: ${SECRET_KEY:0:10}...${NC}"

# Copy .env.example to .env and replace SECRET_KEY
echo "📝 Creating .env file..."
cp .env.example .env

# Replace the SECRET_KEY placeholder
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/SECRET_KEY=your-secret-key-change-this-in-production-min-32-chars/SECRET_KEY=$SECRET_KEY/" .env
else
    # Linux
    sed -i "s/SECRET_KEY=your-secret-key-change-this-in-production-min-32-chars/SECRET_KEY=$SECRET_KEY/" .env
fi

echo -e "${GREEN}✓ .env file created successfully!${NC}"
echo ""
echo "📋 Summary:"
echo "  - SECRET_KEY: Generated (32 bytes, URL-safe)"
echo "  - Database: SQLite (./app.db)"
echo "  - CORS Origins: localhost:5173, localhost:3000"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo "  1. Review .env file and adjust settings if needed"
echo "  2. Never commit .env file to version control"
echo "  3. For production, update CORS origins and database URL"
echo ""
echo -e "${GREEN}✅ Environment setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  make install    # Install dependencies"
echo "  make migrate    # Run database migrations"
echo "  make run        # Start servers"

