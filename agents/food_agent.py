import time
from typing import Dict, Any, List
from .base_agent import BaseAgent
from models import TravelRequest, Restaurant, BudgetCategory

class FoodAgent(BaseAgent):
    def __init__(self):
        super().__init__("Food Agent")
    
    async def process(self, request: TravelRequest, context: Dict[str, Any] = None) -> 'AgentResponse':
        start_time = time.time()
        
        try:
            # Find restaurants and food recommendations
            restaurants = await self._find_restaurants(request, context)
            
            # Generate food recommendations
            food_recommendations = await self._generate_food_recommendations(restaurants, request)
            
            # Create meal suggestions
            meal_suggestions = await self._create_meal_suggestions(restaurants, request)
            
            return self._create_agent_response(
                success=True,
                data={
                    "restaurants": [restaurant.dict() for restaurant in restaurants],
                    "food_recommendations": food_recommendations,
                    "meal_suggestions": meal_suggestions,
                    "total_restaurants": len(restaurants)
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
    
    async def _find_restaurants(self, request: TravelRequest, context: Dict[str, Any] = None) -> List[Restaurant]:
        """Find restaurants and food spots for the destination"""
        
        preferences_text = ", ".join([pref.value for pref in request.travel_preferences])
        
        prompt = f"""
        You are an expert food and dining guide. Find the best restaurants, cafes, and food spots for a 2-day weekend trip to {request.destination}.
        
        Travel Preferences: {preferences_text}
        Budget Category: {request.budget_category.value}
        Group Size: {request.group_size}
        
        For each restaurant/food spot, provide:
        1. Name and cuisine type
        2. Price range ($, $$, $$$, $$$$)
        3. Rating (0-5 stars)
        4. Location/address
        5. Specialties (3-5 signature dishes)
        6. Opening hours
        7. Estimated cost per person in USD
        8. Must-try dishes (2-3 dishes)
        9. Fun food tips or local insights
        
        Return a JSON array with 8-12 restaurants that would be suitable for a 2-day trip.
        Include a mix of:
        - Breakfast/brunch spots
        - Lunch restaurants
        - Dinner restaurants
        - Street food or local markets
        - Cafes or dessert places
        
        Format:
        [
            {{
                "name": "Restaurant Name",
                "cuisine_type": "Italian, Local, etc.",
                "price_range": "$$",
                "rating": 4.5,
                "location": "Address or area",
                "specialties": ["Dish 1", "Dish 2", "Dish 3"],
                "opening_hours": "Hours of operation",
                "estimated_cost_per_person": 35.0,
                "must_try_dishes": ["Signature dish 1", "Signature dish 2"],
                "fun_tips": ["Local tip 1", "Local tip 2"]
            }}
        ]
        """
        
        messages = [{"role": "user", "content": prompt}]
        response = await self._call_openai(messages)
        data = self._extract_json_from_response(response)
        
        restaurants = []
        if isinstance(data, list):
            for item in data:
                try:
                    restaurant = Restaurant(**item)
                    restaurants.append(restaurant)
                except Exception as e:
                    print(f"Error creating restaurant: {e}")
                    continue
        
        return restaurants
    
    async def _generate_food_recommendations(self, restaurants: List[Restaurant], request: TravelRequest) -> List[str]:
        """Generate food-specific recommendations"""
        
        recommendations = []
        
        # Budget-specific recommendations
        if request.budget_category.value == "budget":
            budget_restaurants = [r for r in restaurants if r.price_range in ["$", "$$"]]
            if budget_restaurants:
                recommendations.append(f"Focus on {len(budget_restaurants)} budget-friendly restaurants to maximize your food budget")
            
            recommendations.extend([
                "Try local street food and markets for authentic flavors at great prices",
                "Look for lunch specials and early bird dinner deals",
                "Consider sharing dishes to try more variety"
            ])
        
        elif request.budget_category.value == "luxury":
            luxury_restaurants = [r for r in restaurants if r.price_range in ["$$$", "$$$$"]]
            if luxury_restaurants:
                recommendations.append(f"Indulge in {len(luxury_restaurants)} premium dining experiences")
            
            recommendations.extend([
                "Make reservations at top-rated restaurants in advance",
                "Try local specialties at fine dining establishments",
                "Consider wine pairings and tasting menus"
            ])
        
        else:  # moderate
            recommendations.extend([
                "Mix of casual and upscale dining experiences",
                "Try local specialties at mid-range restaurants",
                "Balance between restaurants and local food markets"
            ])
        
        # Cuisine diversity
        cuisines = set(r.cuisine_type for r in restaurants)
        if len(cuisines) > 3:
            recommendations.append(f"Experience diverse cuisines: {', '.join(list(cuisines)[:3])}")
        
        # Local specialties
        local_restaurants = [r for r in restaurants if "local" in r.cuisine_type.lower() or "traditional" in r.cuisine_type.lower()]
        if local_restaurants:
            recommendations.append("Don't miss the local traditional restaurants for authentic experiences")
        
        return recommendations
    
    async def _create_meal_suggestions(self, restaurants: List[Restaurant], request: TravelRequest) -> Dict[str, List[Dict]]:
        """Create meal suggestions for each day"""
        
        # Categorize restaurants by meal type
        breakfast_spots = []
        lunch_spots = []
        dinner_spots = []
        cafes = []
        
        for restaurant in restaurants:
            name_lower = restaurant.name.lower()
            cuisine_lower = restaurant.cuisine_type.lower()
            
            if any(word in name_lower for word in ["cafe", "coffee", "breakfast", "brunch"]):
                breakfast_spots.append(restaurant)
            elif any(word in name_lower for word in ["lunch", "bistro", "deli"]):
                lunch_spots.append(restaurant)
            elif any(word in name_lower for word in ["dinner", "restaurant", "fine"]):
                dinner_spots.append(restaurant)
            else:
                # Default categorization based on price range
                if restaurant.price_range in ["$", "$$"]:
                    lunch_spots.append(restaurant)
                else:
                    dinner_spots.append(restaurant)
        
        # Create meal suggestions for 2 days
        meal_suggestions = {
            "day_1": {
                "breakfast": breakfast_spots[:2] if breakfast_spots else restaurants[:1],
                "lunch": lunch_spots[:2] if lunch_spots else restaurants[1:3] if len(restaurants) > 1 else restaurants[:1],
                "dinner": dinner_spots[:2] if dinner_spots else restaurants[2:4] if len(restaurants) > 2 else restaurants[:1]
            },
            "day_2": {
                "breakfast": breakfast_spots[2:4] if len(breakfast_spots) > 2 else breakfast_spots[:1] if breakfast_spots else restaurants[4:5] if len(restaurants) > 4 else restaurants[:1],
                "lunch": lunch_spots[2:4] if len(lunch_spots) > 2 else lunch_spots[:1] if lunch_spots else restaurants[5:7] if len(restaurants) > 5 else restaurants[:1],
                "dinner": dinner_spots[2:4] if len(dinner_spots) > 2 else dinner_spots[:1] if dinner_spots else restaurants[7:9] if len(restaurants) > 7 else restaurants[:1]
            }
        }
        
        # Convert to dict format for JSON serialization
        result = {}
        for day, meals in meal_suggestions.items():
            result[day] = {}
            for meal, restaurant_list in meals.items():
                result[day][meal] = [r.dict() for r in restaurant_list]
        
        return result
