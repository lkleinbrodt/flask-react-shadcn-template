#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${BLUE}==>${NC} $1"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print error messages and exit
print_error() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

# Function to execute commands and handle errors
execute_command() {
    print_status "$1"
    if ! eval "$2"; then
        print_error "Failed to execute: $2"
    fi
    print_success "Completed: $1"
}

echo -e "\n${BLUE}🚀 Starting setup process...${NC}\n"

# Backend setup
print_status "Setting up Python backend environment..."
execute_command "Creating Python virtual environment" "python3 -m venv backend/venv"
execute_command "Activating virtual environment" "source backend/venv/bin/activate"
execute_command "Installing Python dependencies" "pip install -r backend/requirements.txt"

# Frontend setup
print_status "Setting up Node.js frontend environment..."
execute_command "Installing Node.js dependencies" "cd frontend && npm install"
execute_command "Updating Node.js packages" "npm update && cd .."


# Database setup
print_status "Initializing database..."
execute_command "Creating database migrations" "flask db init --directory backend/migrations"
execute_command "Generating initial migration" "flask db migrate -m 'Initial Migration'"
execute_command "Applying database migrations" "flask db upgrade"

echo -e "\n${GREEN}✨ Setup completed successfully!${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo "1. Start the backend server: cd backend && flask run"
echo "2. Start the frontend development server: cd frontend && npm run dev"
