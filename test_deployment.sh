#!/bin/bash

# AI Weekend Travel Buddy - Deployment Test Script
# This script tests the deployed application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost:8000"
TIMEOUT=30

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

# Function to test HTTP endpoint
test_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3
    
    print_status "Testing $description..."
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$BASE_URL$endpoint")
    
    if [ "$response" = "$expected_status" ]; then
        print_success "$description - Status: $response"
        return 0
    else
        print_error "$description - Expected: $expected_status, Got: $response"
        return 1
    fi
}

# Function to test API endpoint with JSON
test_api_endpoint() {
    local endpoint=$1
    local method=$2
    local data=$3
    local description=$4
    
    print_status "Testing $description..."
    
    if [ "$method" = "POST" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" \
            --max-time $TIMEOUT \
            -X POST \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BASE_URL$endpoint")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" \
            --max-time $TIMEOUT \
            "$BASE_URL$endpoint")
    fi
    
    if [ "$response" = "200" ] || [ "$response" = "201" ]; then
        print_success "$description - Status: $response"
        return 0
    else
        print_error "$description - Status: $response"
        return 1
    fi
}

# Main test function
main() {
    echo "🧪 AI Weekend Travel Buddy - Deployment Test"
    echo "============================================="
    
    # Test basic connectivity
    print_status "Testing basic connectivity..."
    if ! curl -s --max-time 5 "$BASE_URL" > /dev/null; then
        print_error "Cannot connect to $BASE_URL. Is the application running?"
        exit 1
    fi
    print_success "Basic connectivity OK"
    
    # Test endpoints
    local failed_tests=0
    
    # Test main page
    test_endpoint "/" "200" "Main page" || ((failed_tests++))
    
    # Test health check
    test_endpoint "/api/health" "200" "Health check" || ((failed_tests++))
    
    # Test API endpoints
    test_endpoint "/api/destinations/popular" "200" "Popular destinations" || ((failed_tests++))
    test_endpoint "/api/preferences" "200" "Travel preferences" || ((failed_tests++))
    test_endpoint "/api/budget-categories" "200" "Budget categories" || ((failed_tests++))
    
    # Test itinerary creation (this might take longer)
    print_status "Testing itinerary creation (this may take 30+ seconds)..."
    test_data='{
        "destination": "Paris, France",
        "budget": 500,
        "budget_category": "moderate",
        "travel_preferences": ["culture", "food"],
        "start_date": "2024-06-15",
        "group_size": 1
    }'
    
    test_api_endpoint "/api/create-itinerary" "POST" "$test_data" "Itinerary creation" || ((failed_tests++))
    
    # Summary
    echo ""
    if [ $failed_tests -eq 0 ]; then
        print_success "🎉 All tests passed! The application is working correctly."
        echo ""
        echo "You can now access the application at: $BASE_URL"
        echo "API documentation is available at: $BASE_URL/docs"
    else
        print_error "❌ $failed_tests test(s) failed. Please check the application logs."
        exit 1
    fi
}

# Run main function
main "$@"
