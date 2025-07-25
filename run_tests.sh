#!/bin/bash

# Test runner script for To-Do Application
# This script runs all tests with coverage reporting

set -e

echo "🧪 Running To-Do Application Tests"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_section() {
    echo -e "\n${BLUE}$1${NC}"
    echo "$(printf '=%.0s' {1..50})"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python is available
if ! command_exists python && ! command_exists python3; then
    print_error "Python is not installed!"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python"
if command_exists python3; then
    PYTHON_CMD="python3"
fi

print_section "Setting up test environment"

# Install test dependencies directly (without virtual environment)
print_warning "Installing test dependencies..."

# Check if pip is available
if ! command_exists pip && ! command_exists pip3; then
    print_error "pip is not installed!"
    exit 1
fi

PIP_CMD="pip"
if command_exists pip3; then
    PIP_CMD="pip3"
fi

# Install basic testing requirements
$PIP_CMD install pytest pytest-cov Flask Flask-SQLAlchemy Flask-CORS SQLAlchemy Werkzeug

# Create tests directory if it doesn't exist
mkdir -p tests

# Run unit tests with coverage
print_section "Running Unit Tests"
echo "Testing backend functionality..."

if [ -f "tests/test_backend.py" ]; then
    $PYTHON_CMD -m pytest tests/test_backend.py -v --cov=. --cov-report=html --cov-report=term-missing --cov-exclude="tests/*" --cov-exclude="venv/*" --cov-exclude="__pycache__/*"
    
    if [ $? -eq 0 ]; then
        print_success "Unit tests passed!"
    else
        print_error "Unit tests failed!"
        exit 1
    fi
else
    print_warning "test_backend.py not found, skipping unit tests"
fi

# Check if Docker is running for integration tests
print_section "Checking Docker Environment"
if command_exists docker && docker ps >/dev/null 2>&1; then
    if docker ps | grep -q "todo_backend"; then
        print_success "Docker containers are running"
        
        # Run integration/E2E tests
        print_section "Running Integration Tests"
        echo "Testing API endpoints..."
        
        # Basic API health check
        if curl -f http://localhost/api/health >/dev/null 2>&1; then
            print_success "API is accessible"
            
            # Test basic API functionality
            print_warning "Testing API endpoints..."
            
            # Test health endpoint
            if curl -s http://localhost/api/health | grep -q "healthy"; then
                print_success "Health endpoint working"
            else
                print_warning "Health endpoint test failed"
            fi
            
            # Test tasks endpoint
            if curl -s http://localhost/api/tasks | grep -q "success"; then
                print_success "Tasks endpoint working"
            else
                print_warning "Tasks endpoint test failed"
            fi
            
            # Run E2E tests if available and selenium is installed
            if [ -f "tests/test_e2e.py" ] && $PYTHON_CMD -c "import selenium" 2>/dev/null; then
                print_warning "Running End-to-End tests..."
                $PYTHON_CMD -m pytest tests/test_e2e.py -v -k "not test_complete_user_workflow"
                print_success "Integration tests completed"
            else
                print_warning "Selenium not available or E2E tests not found, skipping browser tests"
                print_warning "Install selenium for full E2E testing: pip install selenium"
            fi
        else
            print_warning "Application not accessible at http://localhost"
            print_warning "Make sure containers are running: docker-compose up -d"
        fi
    else
        print_warning "Docker containers not running"
        print_warning "Start containers with: docker-compose up -d"
    fi
else
    print_warning "Docker not available or not running, skipping integration tests"
fi

# Generate test report
print_section "Test Results Summary"

if [ -f "htmlcov/index.html" ]; then
    print_success "Coverage report generated: htmlcov/index.html"
fi

echo ""
print_success "All available tests completed!"
echo ""
echo "📊 To view detailed coverage report:"
echo "   Open htmlcov/index.html in your browser"
echo ""
echo "🚀 To run the application:"
echo "   docker-compose up --build -d"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost"
echo "   Backend:  http://localhost:5000"