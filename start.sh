#!/bin/bash

###############################################################################
# Simple Start Script for Backend Service
# 
# This script starts the FastAPI backend service.
# For scheduled emails, configure a cronjob to call the API endpoint.
#
# Usage:
#   ./start.sh [--port PORT]
#
# Options:
#   --port PORT    Port number for backend (default: 8000)
#   --help         Show this help message
#
###############################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
PORT=8000

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --port)
      PORT="$2"
      shift 2
      ;;
    --help)
      head -n 17 "$0" | tail -n 12
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Helper functions
print_header() {
  echo -e "\n${BLUE}========================================${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
  echo -e "${GREEN}✓${NC} $1"
}

print_error() {
  echo -e "${RED}✗${NC} $1"
}

print_info() {
  echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

# Change to backend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

if [ ! -d "$BACKEND_DIR" ]; then
  print_error "Backend directory not found: $BACKEND_DIR"
  exit 1
fi

cd "$BACKEND_DIR" || exit 1

print_header "Starting Backend Service"

###############################################################################
# Check Prerequisites
###############################################################################

print_info "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
  print_error "Python 3 is not installed"
  exit 1
fi
print_success "Python 3 found: $(python3 --version)"

# Check Poetry
if ! command -v poetry &> /dev/null; then
  print_error "Poetry is not installed"
  print_info "Install Poetry: curl -sSL https://install.python-poetry.org | python3 -"
  exit 1
fi
print_success "Poetry found: $(poetry --version)"

###############################################################################
# Check Environment File
###############################################################################

print_info "Checking for .env file..."

# Function to find .env file
find_env_file() {
  local search_paths=(
    "$BACKEND_DIR/.env"
    "$SCRIPT_DIR/.env"
  )
  
  for env_path in "${search_paths[@]}"; do
    if [ -f "$env_path" ]; then
      echo "$env_path"
      return 0
    fi
  done
  
  return 1
}

ENV_FILE=$(find_env_file)
if [ -n "$ENV_FILE" ]; then
  print_success "Found .env file: $ENV_FILE"
else
  print_warning ".env file not found"
  print_info "Create .env file from .env.example:"
  print_info "  cp backend/.env.example backend/.env"
  print_info "  # Edit backend/.env with your configuration"
fi

###############################################################################
# Create Logs Directory
###############################################################################

if [ ! -d "logs" ]; then
  mkdir -p logs
  print_success "Created logs directory"
fi

###############################################################################
# Check if Backend is Already Running
###############################################################################

if [ -f "logs/backend.pid" ]; then
  OLD_PID=$(cat logs/backend.pid)
  if ps -p $OLD_PID > /dev/null 2>&1; then
    print_warning "Backend is already running (PID: $OLD_PID)"
    print_info "Stop it first: ./stop.sh"
    exit 1
  else
    print_info "Removing stale PID file"
    rm logs/backend.pid
  fi
fi

###############################################################################
# Start Backend
###############################################################################

print_header "Starting Backend API"

print_info "Starting FastAPI server on port $PORT..."
nohup poetry run uvicorn app.main:app \
  --host 0.0.0.0 \
  --port $PORT \
  --reload \
  > logs/backend.log 2>&1 &

BACKEND_PID=$!
echo $BACKEND_PID > logs/backend.pid

# Wait for backend to start
sleep 3

if ps -p $BACKEND_PID > /dev/null; then
  print_success "Backend started (PID: $BACKEND_PID)"
  print_info "Logs: $BACKEND_DIR/logs/backend.log"
else
  print_error "Backend failed to start"
  print_info "Check logs: $BACKEND_DIR/logs/backend.log"
  exit 1
fi

###############################################################################
# Health Check
###############################################################################

print_header "Health Check"

sleep 2
if curl -s http://localhost:$PORT/api/health > /dev/null 2>&1; then
  print_success "Backend API is healthy"
else
  print_error "Backend API health check failed"
  print_info "Check logs: $BACKEND_DIR/logs/backend.log"
fi

###############################################################################
# Success Summary
###############################################################################

print_header "Service Started Successfully! 🎉"

echo -e "${GREEN}Backend service is running:${NC}\n"

echo "📊 Service Status:"
echo "  • Backend API:   Running (PID: $BACKEND_PID, port $PORT)"

echo -e "\n📡 Access Points:"
echo "  • Frontend:     http://localhost:$PORT"
echo "  • API:          http://localhost:$PORT/api/v1"
echo "  • API Docs:     http://localhost:$PORT/docs"
echo "  • Health:       http://localhost:$PORT/api/health"

echo -e "\n📁 Logs:"
echo "  • Backend:      $BACKEND_DIR/logs/backend.log"

echo -e "\n⏰ Scheduled Emails:"
echo "  Configure cronjob to call:"
echo "  curl -X POST http://localhost:$PORT/api/v1/scheduled/send-scheduled-emails"

echo -e "\n🛑 To stop the service:"
echo "  ./stop.sh"
echo "  or manually:"
echo "  kill $BACKEND_PID"

echo -e "\n${GREEN}Ready to use! 🚀${NC}\n"

