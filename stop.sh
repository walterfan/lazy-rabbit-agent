#!/bin/bash

###############################################################################
# Stop Script for Backend Service
###############################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
  echo -e "${GREEN}✓${NC} $1"
}

print_error() {
  echo -e "${RED}✗${NC} $1"
}

print_info() {
  echo -e "${YELLOW}ℹ${NC} $1"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

cd "$BACKEND_DIR" || exit 1

echo "Stopping Backend Service..."

# Stop backend
if [ -f "logs/backend.pid" ]; then
  BACKEND_PID=$(cat logs/backend.pid)
  if ps -p $BACKEND_PID > /dev/null 2>&1; then
    kill $BACKEND_PID
    print_success "Backend stopped (PID: $BACKEND_PID)"
  else
    print_info "Backend not running"
  fi
  rm logs/backend.pid
else
  print_info "No backend PID file found"
  
  # Try to find and kill by name
  if pkill -f "uvicorn app.main:app" > /dev/null 2>&1; then
    print_success "Stopped backend by process name"
  else
    print_info "No backend process found"
  fi
fi

print_success "All services stopped"
