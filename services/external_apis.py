import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from config import Config

class ExternalAPIService:
    def __init__(self):
        self.session = None
        self.weather_cache = {}
        self.places_cache = {}
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_weather_forecast(self, destination: str, start_date: str) -> Dict[str, Any]:
        """Get weather forecast for the destination"""
        cache_key = f"{destination}_{start_date}"
        
        if cache_key in self.weather_cache:
            return self.weather_cache[cache_key]
        
        try:
            # Extract city and country from destination
            city, country = self._parse_destination(destination)
            
            # Use OpenWeatherMap API (free tier)
            api_key = Config.OPENWEATHER_API_KEY
            if not api_key:
                return self._get_mock_weather()
            
            url = f"http://api.openweathermap.org/data/2.5/forecast"
            params = {
                'q': f"{city},{country}",
                'appid': api_key,
                'units': 'metric'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    weather_info = self._process_weather_data(data, start_date)
                    self.weather_cache[cache_key] = weather_info
                    return weather_info
                else:
                    return self._get_mock_weather()
        
        except Exception as e:
            print(f"Weather API error: {e}")
            return self._get_mock_weather()
    
    async def get_places_info(self, destination: str, place_type: str = "tourist_attraction") -> List[Dict[str, Any]]:
        """Get places information using Google Places API"""
        cache_key = f"{destination}_{place_type}"
        
        if cache_key in self.places_cache:
            return self.places_cache[cache_key]
        
        try:
            api_key = Config.GOOGLE_PLACES_API_KEY
            if not api_key:
                return self._get_mock_places()
            
            # Get coordinates for the destination
            coords = await self._get_coordinates(destination)
            if not coords:
                return self._get_mock_places()
            
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{coords['lat']},{coords['lng']}",
                'radius': 5000,  # 5km radius
                'type': place_type,
                'key': api_key
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    places_info = self._process_places_data(data)
                    self.places_cache[cache_key] = places_info
                    return places_info
                else:
                    return self._get_mock_places()
        
        except Exception as e:
            print(f"Places API error: {e}")
            return self._get_mock_places()
    
    async def get_transportation_info(self, origin: str, destination: str) -> Dict[str, Any]:
        """Get transportation information between locations"""
        try:
            # Use Google Maps API for transportation info
            api_key = Config.GOOGLE_MAPS_API_KEY
            if not api_key:
                return self._get_mock_transportation()
            
            url = "https://maps.googleapis.com/maps/api/distancematrix/json"
            params = {
                'origins': origin,
                'destinations': destination,
                'mode': 'transit',
                'key': api_key
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_transportation_data(data)
                else:
                    return self._get_mock_transportation()
        
        except Exception as e:
            print(f"Transportation API error: {e}")
            return self._get_mock_transportation()
    
    def _parse_destination(self, destination: str) -> tuple:
        """Parse destination string to extract city and country"""
        parts = destination.split(',')
        if len(parts) >= 2:
            return parts[0].strip(), parts[1].strip()
        return destination.strip(), ""
    
    def _process_weather_data(self, data: Dict, start_date: str) -> Dict[str, Any]:
        """Process weather API response"""
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = start_dt + timedelta(days=2)
            
            forecasts = []
            for item in data.get('list', []):
                dt = datetime.fromtimestamp(item['dt'])
                if start_dt <= dt <= end_dt:
                    forecasts.append({
                        'date': dt.strftime('%Y-%m-%d'),
                        'time': dt.strftime('%H:%M'),
                        'temperature': item['main']['temp'],
                        'description': item['weather'][0]['description'],
                        'humidity': item['main']['humidity'],
                        'wind_speed': item['wind']['speed']
                    })
            
            return {
                'forecasts': forecasts,
                'recommendations': self._generate_weather_recommendations(forecasts)
            }
        except Exception:
            return self._get_mock_weather()
    
    def _process_places_data(self, data: Dict) -> List[Dict[str, Any]]:
        """Process places API response"""
        try:
            places = []
            for place in data.get('results', [])[:10]:  # Limit to top 10
                places.append({
                    'name': place.get('name', ''),
                    'rating': place.get('rating', 0),
                    'price_level': place.get('price_level', 0),
                    'types': place.get('types', []),
                    'vicinity': place.get('vicinity', ''),
                    'place_id': place.get('place_id', '')
                })
            return places
        except Exception:
            return self._get_mock_places()
    
    def _process_transportation_data(self, data: Dict) -> Dict[str, Any]:
        """Process transportation API response"""
        try:
            elements = data.get('rows', [{}])[0].get('elements', [{}])
            if elements:
                element = elements[0]
                return {
                    'duration': element.get('duration', {}).get('text', 'Unknown'),
                    'distance': element.get('distance', {}).get('text', 'Unknown'),
                    'status': element.get('status', 'Unknown')
                }
            return self._get_mock_transportation()
        except Exception:
            return self._get_mock_transportation()
    
    def _generate_weather_recommendations(self, forecasts: List[Dict]) -> List[str]:
        """Generate weather-based recommendations"""
        recommendations = []
        
        if not forecasts:
            return ["Check local weather before your trip"]
        
        # Analyze weather patterns
        temperatures = [f['temperature'] for f in forecasts]
        descriptions = [f['description'] for f in forecasts]
        
        avg_temp = sum(temperatures) / len(temperatures)
        
        if avg_temp < 10:
            recommendations.append("🌡️ Cold weather expected - pack warm clothing and layers")
        elif avg_temp > 25:
            recommendations.append("☀️ Warm weather expected - pack light clothing and sunscreen")
        
        if any('rain' in desc.lower() for desc in descriptions):
            recommendations.append("🌧️ Rain expected - pack rain gear and consider indoor activities")
        
        if any('snow' in desc.lower() for desc in descriptions):
            recommendations.append("❄️ Snow expected - pack winter gear and check road conditions")
        
        return recommendations
    
    async def _get_coordinates(self, destination: str) -> Optional[Dict[str, float]]:
        """Get coordinates for a destination using geocoding"""
        try:
            api_key = Config.GOOGLE_MAPS_API_KEY
            if not api_key:
                return None
            
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': destination,
                'key': api_key
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('results'):
                        location = data['results'][0]['geometry']['location']
                        return {'lat': location['lat'], 'lng': location['lng']}
            return None
        except Exception:
            return None
    
    def _get_mock_weather(self) -> Dict[str, Any]:
        """Return mock weather data for demo purposes"""
        return {
            'forecasts': [
                {
                    'date': '2024-06-15',
                    'time': '09:00',
                    'temperature': 22,
                    'description': 'partly cloudy',
                    'humidity': 65,
                    'wind_speed': 3.2
                },
                {
                    'date': '2024-06-16',
                    'time': '09:00',
                    'temperature': 24,
                    'description': 'sunny',
                    'humidity': 60,
                    'wind_speed': 2.8
                }
            ],
            'recommendations': [
                "☀️ Pleasant weather expected - perfect for outdoor activities",
                "👕 Pack light layers for temperature variations"
            ]
        }
    
    def _get_mock_places(self) -> List[Dict[str, Any]]:
        """Return mock places data for demo purposes"""
        return [
            {
                'name': 'City Center',
                'rating': 4.5,
                'price_level': 2,
                'types': ['tourist_attraction', 'point_of_interest'],
                'vicinity': 'Downtown',
                'place_id': 'mock_place_1'
            }
        ]
    
    def _get_mock_transportation(self) -> Dict[str, Any]:
        """Return mock transportation data for demo purposes"""
        return {
            'duration': '15 minutes',
            'distance': '2.5 km',
            'status': 'OK'
        }
