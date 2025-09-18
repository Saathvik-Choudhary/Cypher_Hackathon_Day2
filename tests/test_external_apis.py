import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from services.external_apis import ExternalAPIService

class TestExternalAPIs:
    @pytest.fixture
    def api_service(self):
        return ExternalAPIService()
    
    @pytest.mark.asyncio
    async def test_weather_forecast_mock(self, api_service):
        """Test weather forecast with mock data"""
        # Test with mock response
        weather_data = await api_service.get_weather_forecast("Paris, France", "2024-06-15")
        
        assert "forecasts" in weather_data
        assert "recommendations" in weather_data
        assert len(weather_data["forecasts"]) > 0
        
        # Check forecast structure
        forecast = weather_data["forecasts"][0]
        required_fields = ["date", "time", "temperature", "description", "humidity", "wind_speed"]
        for field in required_fields:
            assert field in forecast
    
    @pytest.mark.asyncio
    async def test_places_info_mock(self, api_service):
        """Test places info with mock data"""
        places_data = await api_service.get_places_info("Paris, France", "tourist_attraction")
        
        assert isinstance(places_data, list)
        if len(places_data) > 0:
            place = places_data[0]
            required_fields = ["name", "rating", "price_level", "types", "vicinity", "place_id"]
            for field in required_fields:
                assert field in place
    
    @pytest.mark.asyncio
    async def test_transportation_info_mock(self, api_service):
        """Test transportation info with mock data"""
        transport_data = await api_service.get_transportation_info("Paris", "Eiffel Tower")
        
        assert "duration" in transport_data
        assert "distance" in transport_data
        assert "status" in transport_data
    
    def test_parse_destination(self, api_service):
        """Test destination parsing"""
        # Test with city, country format
        city, country = api_service._parse_destination("Paris, France")
        assert city == "Paris"
        assert country == "France"
        
        # Test with single location
        city, country = api_service._parse_destination("Tokyo")
        assert city == "Tokyo"
        assert country == ""
    
    def test_generate_weather_recommendations(self, api_service):
        """Test weather recommendation generation"""
        forecasts = [
            {"temperature": 5, "description": "cold and rainy"},
            {"temperature": 30, "description": "hot and sunny"},
            {"temperature": 15, "description": "snowy weather"}
        ]
        
        recommendations = api_service._generate_weather_recommendations(forecasts)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Should have cold weather recommendation
        cold_recs = [rec for rec in recommendations if "cold" in rec.lower() or "warm" in rec.lower()]
        assert len(cold_recs) > 0
    
    def test_mock_weather_data(self, api_service):
        """Test mock weather data structure"""
        mock_weather = api_service._get_mock_weather()
        
        assert "forecasts" in mock_weather
        assert "recommendations" in mock_weather
        assert len(mock_weather["forecasts"]) > 0
        
        forecast = mock_weather["forecasts"][0]
        required_fields = ["date", "time", "temperature", "description", "humidity", "wind_speed"]
        for field in required_fields:
            assert field in forecast
    
    def test_mock_places_data(self, api_service):
        """Test mock places data structure"""
        mock_places = api_service._get_mock_places()
        
        assert isinstance(mock_places, list)
        assert len(mock_places) > 0
        
        place = mock_places[0]
        required_fields = ["name", "rating", "price_level", "types", "vicinity", "place_id"]
        for field in required_fields:
            assert field in place
    
    def test_mock_transportation_data(self, api_service):
        """Test mock transportation data structure"""
        mock_transport = api_service._get_mock_transportation()
        
        assert "duration" in mock_transport
        assert "distance" in mock_transport
        assert "status" in mock_transport
    
    @pytest.mark.asyncio
    async def test_api_service_context_manager(self):
        """Test API service as context manager"""
        async with ExternalAPIService() as service:
            assert service is not None
            # Should be able to make calls
            weather = await service.get_weather_forecast("Test", "2024-01-01")
            assert weather is not None
    
    @pytest.mark.asyncio
    async def test_error_handling(self, api_service):
        """Test error handling in API calls"""
        # Test with invalid destination
        weather = await api_service.get_weather_forecast("", "invalid-date")
        assert weather is not None  # Should return mock data on error
        
        places = await api_service.get_places_info("", "invalid_type")
        assert isinstance(places, list)  # Should return mock data on error
        
        transport = await api_service.get_transportation_info("", "")
        assert transport is not None  # Should return mock data on error
    
    def test_cache_functionality(self, api_service):
        """Test caching functionality"""
        # Test cache key generation
        data = {"destination": "Paris", "date": "2024-06-15"}
        key = api_service._generate_cache_key(data)
        assert isinstance(key, str)
        assert len(key) > 0
        
        # Test cache storage
        api_service.weather_cache["test_key"] = {"test": "data"}
        assert "test_key" in api_service.weather_cache
        assert api_service.weather_cache["test_key"]["test"] == "data"
