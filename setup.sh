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

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v npm &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js and try again."
    exit 1
fi

# 1. Create and activate Python virtual environment
echo -e "${GREEN}Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Source the virtual environment (different for Windows vs Unix-based systems)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Unix-based (macOS, Linux)
    source venv/bin/activate
fi

# Verify virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Error: Virtual environment was not activated properly"
    exit 1
fi
echo -e "${GREEN}Virtual environment activated: $VIRTUAL_ENV${NC}"

# 2. Install Python dependencies
echo -e "${GREEN}Installing Python dependencies...${NC}"
# Check if pip is available
if ! python -m pip --version &> /dev/null; then
    echo "Error: pip is not available. Trying to install pip..."
    python -m ensurepip --upgrade
fi
python -m pip install -r backend/requirements.txt

# 3. Initialize and upgrade database schema
echo -e "${GREEN}Setting up database...${NC}"
# Only initialize if migrations directory doesn't exist or is empty
if [ ! -d "backend/migrations" ] || [ -z "$(ls -A backend/migrations 2>/dev/null)" ]; then
    flask db init --directory backend/migrations
else
    echo "Migrations directory already exists, skipping initialization"
fi
echo -e "${GREEN}Upgrading database schema...${NC}"
flask db upgrade --directory backend/migrations

# 4. Install frontend dependencies
echo -e "${GREEN}Installing frontend dependencies...${NC}"
cd frontend
npm install
cd ..

# 5. Start both servers
echo -e "${GREEN}Starting servers...${NC}"
echo -e "${BLUE}Starting Flask backend server on http://localhost:5002${NC}"
echo -e "${BLUE}Starting React frontend server on http://localhost:5173${NC}"
echo -e "${BLUE}Press Ctrl+C to stop all servers${NC}"

# Start servers as background processes in the current terminal
(cd frontend && npm run dev) &
FRONTEND_PID=$!

# Give the frontend a moment to start up
sleep 2

# Start the backend server in the foreground
flask run --host=0.0.0.0 --port=5002

# Note: We won't reach here under normal circumstances
# The script will be terminated by the user with Ctrl+C, which will trigger the cleanup function 