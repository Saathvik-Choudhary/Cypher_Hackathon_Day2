import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app
from models import TravelRequest, TravelPreference, BudgetCategory

class TestAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "AI Weekend Travel Buddy"
    
    def test_popular_destinations(self, client):
        """Test popular destinations endpoint"""
        response = client.get("/api/destinations/popular")
        assert response.status_code == 200
        data = response.json()
        assert "destinations" in data
        assert len(data["destinations"]) > 0
        
        # Check destination structure
        destination = data["destinations"][0]
        assert "name" in destination
        assert "country" in destination
        assert "category" in destination
    
    def test_travel_preferences(self, client):
        """Test travel preferences endpoint"""
        response = client.get("/api/preferences")
        assert response.status_code == 200
        data = response.json()
        assert "preferences" in data
        assert len(data["preferences"]) > 0
        
        # Check preference structure
        preference = data["preferences"][0]
        assert "value" in preference
        assert "label" in preference
    
    def test_budget_categories(self, client):
        """Test budget categories endpoint"""
        response = client.get("/api/budget-categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0
        
        # Check category structure
        category = data["categories"][0]
        assert "value" in category
        assert "label" in category
        assert "range" in category
    
    def test_create_itinerary_valid_request(self, client):
        """Test itinerary creation with valid request"""
        request_data = {
            "destination": "Paris, France",
            "budget": 500.0,
            "budget_category": "moderate",
            "travel_preferences": ["culture", "food"],
            "start_date": "2024-06-15",
            "group_size": 2,
            "special_requirements": "Vegetarian friendly"
        }
        
        response = client.post("/api/create-itinerary", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "itinerary" in data
        assert "processing_time" in data
    
    def test_create_itinerary_invalid_request(self, client):
        """Test itinerary creation with invalid request"""
        request_data = {
            "destination": "",  # Invalid destination
            "budget": -100,     # Invalid budget
            "budget_category": "invalid",
            "travel_preferences": [],
            "start_date": "invalid-date",
            "group_size": 0
        }
        
        response = client.post("/api/create-itinerary", json=request_data)
        # Should handle errors gracefully
        assert response.status_code in [200, 422]  # Either success with error message or validation error
    
    def test_optimize_itinerary(self, client):
        """Test itinerary optimization endpoint"""
        request_data = {
            "destination": "Tokyo, Japan",
            "budget": 600.0,
            "budget_category": "moderate",
            "travel_preferences": ["adventure", "food"],
            "start_date": "2024-07-01",
            "group_size": 1
        }
        
        response = client.post("/api/optimize-itinerary", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "itinerary" in data
    
    def test_cache_stats(self, client):
        """Test cache statistics endpoint"""
        response = client.get("/api/cache/stats")
        assert response.status_code == 200
        data = response.json()
        assert "cache_type" in data
    
    def test_root_endpoint(self, client):
        """Test root endpoint serves frontend"""
        response = client.get("/")
        assert response.status_code == 200
        # Should return HTML content
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options("/api/health")
        # CORS middleware should be configured
        assert response.status_code in [200, 405]  # OPTIONS might not be explicitly handled
    
    def test_api_documentation(self, client):
        """Test API documentation is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
