#!/bin/bash

# AI Weekend Travel Buddy - Build Script
# This script builds both the React frontend and prepares the Docker container

set -e  # Exit on any error

echo "🚀 Building AI Weekend Travel Buddy..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "All requirements are met!"
}

# Build React frontend
build_frontend() {
    print_status "Building React frontend..."
    
    if [ ! -d "frontend" ]; then
        print_error "Frontend directory not found!"
        exit 1
    fi
    
    cd frontend
    
    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        print_error "package.json not found in frontend directory!"
        exit 1
    fi
    
    # Install dependencies
    print_status "Installing frontend dependencies..."
    npm install
    
    # Build the React app
    print_status "Building React app for production..."
    npm run build
    
    if [ ! -d "build" ]; then
        print_error "React build failed - build directory not created!"
        exit 1
    fi
    
    print_success "Frontend built successfully!"
    cd ..
}

# Build Docker image
build_docker() {
    print_status "Building Docker image..."
    
    # Build the Docker image
    docker build -t travel-buddy:latest .
    
    if [ $? -eq 0 ]; then
        print_success "Docker image built successfully!"
    else
        print_error "Docker build failed!"
        exit 1
    fi
}

# Check environment file
check_env() {
    print_status "Checking environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            print_warning ".env file not found. Copying from env.example..."
            cp env.example .env
            print_warning "Please edit .env file and add your OpenAI API key!"
        else
            print_error "No .env file found and no env.example to copy from!"
            exit 1
        fi
    else
        print_success "Environment file found!"
    fi
}

# Main build process
main() {
    echo "🎯 AI Weekend Travel Buddy Build Script"
    echo "========================================"
    
    check_requirements
    check_env
    build_frontend
    build_docker
    
    echo ""
    print_success "🎉 Build completed successfully!"
    echo ""
    echo "To run the application:"
    echo "  docker-compose up"
    echo ""
    echo "Or run directly with Docker:"
    echo "  docker run -p 8000:8000 --env-file .env travel-buddy:latest"
    echo ""
    echo "The application will be available at: http://localhost:8000"
}

# Run main function
main "$@"
