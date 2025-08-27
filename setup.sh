#!/bin/bash
set -e

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to clean up background processes when script is terminated
cleanup() {
    echo -e "\n${BLUE}Shutting down servers...${NC}"
    # Kill all child processes
    pkill -P $$ || true
    exit 0
}

# Set up trap to catch termination signals
trap cleanup SIGINT SIGTERM EXIT

echo -e "${BLUE}Setting up Chewbacca project...${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "\033[0;33mWarning: .env file not found. Please create one with required environment variables.${NC}"
    echo -e "\033[0;33mSee README.md for required environment variables.${NC}"
    echo ""
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "\033[0;31mError: Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
if [ "$(printf '%s\n' "3.8" "$python_version" | sort -V | head -n1)" != "3.8" ]; then
    echo -e "\033[0;31mError: Python 3.8+ is required. Found version: $python_version${NC}"
    exit 1
fi
echo -e "${GREEN}Python version check passed: $python_version${NC}"

# Check if Node.js is installed
if ! command -v npm &> /dev/null; then
    echo -e "\033[0;31mError: Node.js is not installed. Please install Node.js and try again.${NC}"
    exit 1
fi

# Check Node.js version
node_version=$(node --version 2>&1 | grep -oE 'v[0-9]+')
if [ "$(printf '%s\n' "v18" "$node_version" | sort -V | head -n1)" != "v18" ]; then
    echo -e "\033[0;31mError: Node.js 18+ is required. Found version: $node_version${NC}"
    exit 1
fi
echo -e "${GREEN}Node.js version check passed: $node_version${NC}"

# 1. Create and activate Python virtual environment
echo -e "${GREEN}Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    if ! python3 -m venv venv; then
        echo -e "\033[0;31mError: Failed to create virtual environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}Virtual environment created successfully${NC}"
fi

# Source the virtual environment (different for Windows vs Unix-based systems)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    if ! source venv/Scripts/activate; then
        echo -e "\033[0;31mError: Failed to activate virtual environment on Windows${NC}"
        exit 1
    fi
else
    # Unix-based (macOS, Linux)
    if ! source venv/bin/activate; then
        echo -e "\033[0;31mError: Failed to activate virtual environment on Unix${NC}"
        exit 1
    fi
fi

# Verify virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "\033[0;31mError: Virtual environment was not activated properly${NC}"
    exit 1
fi
echo -e "${GREEN}Virtual environment activated: $VIRTUAL_ENV${NC}"

# 2. Install Python dependencies
echo -e "${GREEN}Installing Python dependencies...${NC}"
# Check if pip is available
if ! python -m pip --version &> /dev/null; then
    echo "Error: pip is not available. Trying to install pip..."
    if ! python -m ensurepip --upgrade; then
        echo -e "\033[0;31mError: Failed to install pip${NC}"
        exit 1
    fi
fi

if ! python -m pip install -r backend/requirements.txt; then
    echo -e "\033[0;31mError: Failed to install Python dependencies${NC}"
    exit 1
fi
echo -e "${GREEN}Python dependencies installed successfully${NC}"

# 3. Initialize and upgrade database schema
echo -e "${GREEN}Setting up database...${NC}"

# Check if migrations directory exists and has content
if [ ! -d "backend/migrations" ] || [ -z "$(ls -A backend/migrations 2>/dev/null)" ]; then
    echo "Initializing database migrations..."
    if ! flask db init --directory backend/migrations; then
        echo -e "\033[0;31mError: Failed to initialize database migrations${NC}"
        exit 1
    fi
    
    if ! flask db migrate --directory backend/migrations -m "Initial migration"; then
        echo -e "\033[0;31mError: Failed to create initial migration${NC}"
        exit 1
    fi
    echo -e "${GREEN}Database migrations initialized successfully${NC}"
else
    echo "Migrations directory already exists, skipping initialization"
fi

echo -e "${GREEN}Upgrading database schema...${NC}"
if ! flask db upgrade --directory backend/migrations; then
    echo -e "\033[0;31mError: Failed to upgrade database schema${NC}"
    exit 1
fi
echo -e "${GREEN}Database schema upgraded successfully${NC}"

# 4. Install frontend dependencies
echo -e "${GREEN}Installing frontend dependencies...${NC}"
cd frontend
if ! npm install; then
    echo -e "\033[0;31mError: Failed to install frontend dependencies${NC}"
    exit 1
fi
cd ..
echo -e "${GREEN}Frontend dependencies installed successfully${NC}"

# 5. Start both servers
echo -e "${GREEN}Starting servers...${NC}"
echo -e "${BLUE}Starting Flask backend server on http://localhost:5002${NC}"
echo -e "${BLUE}Starting React frontend server on http://localhost:5173${NC}"
echo -e "${BLUE}Press Ctrl+C to stop all servers${NC}"

# Start servers as background processes in the current terminal
echo -e "${BLUE}Starting frontend server...${NC}"
(cd frontend && npm run dev) &
FRONTEND_PID=$!

# Give the frontend a moment to start up and check if it's running
sleep 3
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "\033[0;31mError: Frontend server failed to start${NC}"
    exit 1
fi
echo -e "${GREEN}Frontend server started successfully${NC}"

# Start the backend server in the foreground
echo -e "${BLUE}Starting backend server...${NC}"
if ! flask run --host=0.0.0.0 --port=5000; then
    echo -e "\033[0;31mError: Backend server failed to start or crashed${NC}"
    exit 1
fi

# Note: We won't reach here under normal circumstances
# The script will be terminated by the user with Ctrl+C, which will trigger the cleanup function 