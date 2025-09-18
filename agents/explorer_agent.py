import json
from typing import Dict, Any, List
from .base_agent import BaseAgent
from models import TravelRequest, Attraction, TravelPreference

class ExplorerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Explorer Agent")
    
    async def process(self, request: TravelRequest, context: Dict[str, Any] = None) -> 'AgentResponse':
        start_time = time.time()
        
        try:
            # Get attractions for the destination
            attractions = await self._find_attractions(request)
            
            # Rank and optimize attractions
            optimized_attractions = await self._optimize_attractions(attractions, request)
            
            return self._create_agent_response(
                success=True,
                data={
                    "attractions": [attraction.dict() for attraction in optimized_attractions],
                    "total_attractions": len(optimized_attractions),
                    "recommendations": self._generate_recommendations(optimized_attractions, request)
                },
                start_time=start_time
            )
            
        except Exception as e:
            return self._create_agent_response(
                success=False,
                data={},
                error_message=str(e),
                start_time=start_time
            )
    
    async def _find_attractions(self, request: TravelRequest) -> List[Attraction]:
        """Find top attractions for the destination"""
        
        preferences_text = ", ".join([pref.value for pref in request.travel_preferences])
        
        prompt = f"""
        You are an expert travel explorer. Find the top attractions and activities for a 2-day weekend trip to {request.destination}.
        
        Travel Preferences: {preferences_text}
        Budget Category: {request.budget_category.value}
        Group Size: {request.group_size}
        
        For each attraction, provide:
        1. Name and description
        2. Location/address
        3. Opening hours (if applicable)
        4. Entry fee in USD (estimate if unknown)
        5. Estimated duration in minutes
        6. Popularity score (0-10)
        7. Uniqueness score (0-10)
        8. Category (museum, park, landmark, activity, etc.)
        
        Return a JSON array with at least 8-12 attractions that would be suitable for a 2-day trip.
        Focus on attractions that match the travel preferences and are appropriate for the budget category.
        
        Format:
        [
            {{
                "name": "Attraction Name",
                "description": "Brief description of what makes this attraction special",
                "location": "Address or area",
                "opening_hours": "Hours of operation",
                "entry_fee": 25.0,
                "estimated_duration": 120,
                "popularity_score": 8.5,
                "uniqueness_score": 7.0,
                "category": "museum"
            }}
        ]
        """
        
        messages = [{"role": "user", "content": prompt}]
        response = await self._call_openai(messages)
        data = self._extract_json_from_response(response)
        
        attractions = []
        if isinstance(data, list):
            for item in data:
                try:
                    attraction = Attraction(**item)
                    attractions.append(attraction)
                except Exception as e:
                    print(f"Error creating attraction: {e}")
                    continue
        
        return attractions
    
    async def _optimize_attractions(self, attractions: List[Attraction], request: TravelRequest) -> List[Attraction]:
        """Optimize attractions based on preferences and constraints"""
        
        # Sort by combined score (popularity + uniqueness)
        scored_attractions = []
        for attraction in attractions:
            combined_score = (attraction.popularity_score + attraction.uniqueness_score) / 2
            
            # Adjust score based on preferences
            if any(pref.value in attraction.category.lower() for pref in request.travel_preferences):
                combined_score += 1.0
            
            # Adjust score based on budget
            if request.budget_category.value == "budget" and attraction.entry_fee and attraction.entry_fee > 50:
                combined_score -= 1.0
            elif request.budget_category.value == "luxury" and attraction.entry_fee and attraction.entry_fee < 20:
                combined_score -= 0.5
            
            scored_attractions.append((attraction, combined_score))
        
        # Sort by score and take top attractions
        scored_attractions.sort(key=lambda x: x[1], reverse=True)
        
        # Take top attractions (limit to reasonable number for 2 days)
        max_attractions = min(len(scored_attractions), 12)
        optimized_attractions = [attraction for attraction, score in scored_attractions[:max_attractions]]
        
        return optimized_attractions
    
    def _generate_recommendations(self, attractions: List[Attraction], request: TravelRequest) -> List[str]:
        """Generate travel recommendations based on attractions"""
        recommendations = []
        
        # Group attractions by category
        categories = {}
        for attraction in attractions:
            if attraction.category not in categories:
                categories[attraction.category] = []
            categories[attraction.category].append(attraction)
        
        # Generate category-specific recommendations
        for category, attrs in categories.items():
            if len(attrs) > 1:
                recommendations.append(f"Visit multiple {category}s to get a comprehensive experience")
        
        # Budget-specific recommendations
        if request.budget_category.value == "budget":
            free_attractions = [a for a in attractions if not a.entry_fee or a.entry_fee == 0]
            if free_attractions:
                recommendations.append(f"Consider visiting {len(free_attractions)} free attractions to save money")
        
        # Duration recommendations
        total_duration = sum(a.estimated_duration for a in attractions)
        if total_duration > 960:  # More than 16 hours
            recommendations.append("Your itinerary is packed - consider prioritizing must-see attractions")
        
        return recommendations

import time
