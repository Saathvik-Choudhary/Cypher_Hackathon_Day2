import time
from typing import Dict, Any, List
from .base_agent import BaseAgent
from models import TravelRequest, BudgetBreakdown, BudgetCategory
from config import Config

class BudgetAgent(BaseAgent):
    def __init__(self):
        super().__init__("Budget Agent")
    
    async def process(self, request: TravelRequest, context: Dict[str, Any] = None) -> 'AgentResponse':
        start_time = time.time()
        
        try:
            # Create budget breakdown
            budget_breakdown = await self._create_budget_breakdown(request)
            
            # Estimate costs for activities if provided in context
            activity_costs = {}
            if context and "attractions" in context:
                activity_costs = await self._estimate_activity_costs(context["attractions"], request)
            
            # Generate budget recommendations
            recommendations = await self._generate_budget_recommendations(budget_breakdown, request)
            
            return self._create_agent_response(
                success=True,
                data={
                    "budget_breakdown": budget_breakdown.dict(),
                    "activity_costs": activity_costs,
                    "recommendations": recommendations,
                    "budget_utilization": self._calculate_budget_utilization(budget_breakdown)
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
    
    async def _create_budget_breakdown(self, request: TravelRequest) -> BudgetBreakdown:
        """Create a detailed budget breakdown based on the request"""
        
        total_budget = request.budget
        budget_category = request.budget_category.value
        
        # Get budget allocation percentages from config
        allocation = Config.BUDGET_CATEGORIES.get(budget_category, Config.BUDGET_CATEGORIES["moderate"])
        
        # Calculate allocations
        accommodation = total_budget * allocation["accommodation"]
        food = total_budget * allocation["food"]
        activities = total_budget * allocation["activities"]
        transportation = total_budget * allocation["transportation"]
        
        # Calculate miscellaneous (remaining budget)
        allocated = accommodation + food + activities + transportation
        miscellaneous = total_budget - allocated
        
        return BudgetBreakdown(
            total_budget=total_budget,
            accommodation=accommodation,
            transportation=transportation,
            food=food,
            activities=activities,
            miscellaneous=miscellaneous,
            remaining_budget=total_budget
        )
    
    async def _estimate_activity_costs(self, attractions: List[Dict], request: TravelRequest) -> Dict[str, float]:
        """Estimate costs for activities/attractions"""
        
        activity_costs = {}
        total_activity_cost = 0.0
        
        for attraction in attractions:
            name = attraction.get("name", "Unknown")
            entry_fee = attraction.get("entry_fee", 0.0)
            
            # Adjust cost based on group size
            cost_per_person = entry_fee
            total_cost = cost_per_person * request.group_size
            
            activity_costs[name] = total_cost
            total_activity_cost += total_cost
        
        # Add transportation estimates
        if request.budget_category.value == "budget":
            activity_costs["Local Transportation"] = 20.0 * request.group_size
        elif request.budget_category.value == "moderate":
            activity_costs["Local Transportation"] = 40.0 * request.group_size
        else:  # luxury
            activity_costs["Local Transportation"] = 80.0 * request.group_size
        
        activity_costs["Total Activities"] = total_activity_cost + activity_costs["Local Transportation"]
        
        return activity_costs
    
    async def _generate_budget_recommendations(self, budget_breakdown: BudgetBreakdown, request: TravelRequest) -> List[str]:
        """Generate sophisticated budget-specific recommendations"""
        
        recommendations = []
        
        # Budget category specific recommendations
        if request.budget_category.value == "budget":
            recommendations.extend([
                "🏨 Accommodation: Consider hostels, budget hotels, or Airbnb to maximize your accommodation budget",
                "🎫 Activities: Look for free walking tours, free museum days, and city passes for multiple attractions",
                "🍽️ Food: Eat at local markets, street food, and casual restaurants for authentic and affordable meals",
                "🚌 Transportation: Use public transportation, walking, or bike rentals between attractions",
                "💰 Money-saving tips: Book activities in advance for discounts, look for student/senior discounts",
                "📱 Apps: Use local apps for deals on food and activities",
                "🕐 Timing: Visit popular attractions during off-peak hours to avoid crowds and higher prices"
            ])
        elif request.budget_category.value == "moderate":
            recommendations.extend([
                "🏨 Accommodation: Mix of mid-range hotels, boutique accommodations, and unique stays",
                "🍽️ Food: Balance between restaurants and local food experiences, try local specialties",
                "🎫 Activities: Consider combo tickets for multiple attractions, book guided tours for key sites",
                "🚌 Transportation: Use a mix of public transport and occasional taxis/rideshare",
                "💳 Payment: Use credit cards with travel rewards, consider travel insurance",
                "📅 Planning: Book popular restaurants and activities in advance",
                "🎯 Focus: Prioritize must-see attractions and unique local experiences"
            ])
        else:  # luxury
            recommendations.extend([
                "🏨 Accommodation: Stay at premium hotels, luxury resorts, or unique boutique accommodations",
                "🍽️ Food: Dine at top-rated restaurants, try local specialties at fine dining establishments",
                "🎫 Activities: Book private tours, premium experiences, and exclusive access",
                "🚌 Transportation: Use private transportation, premium car services, or chauffeur services",
                "💎 Experiences: Consider wine tastings, spa treatments, and exclusive cultural experiences",
                "📞 Concierge: Use hotel concierge services for reservations and recommendations",
                "🎭 Entertainment: Book tickets for shows, concerts, or cultural performances"
            ])
        
        # Advanced budget optimization recommendations
        budget_utilization = (budget_breakdown.activities + budget_breakdown.food + budget_breakdown.accommodation) / budget_breakdown.total_budget
        
        if budget_utilization > 0.9:
            recommendations.append("⚠️ Your budget is highly utilized - consider adding a 10-15% buffer for unexpected expenses")
        elif budget_utilization < 0.7:
            recommendations.append("💡 You have room in your budget - consider upgrading some experiences or adding more activities")
        
        # Category-specific optimization
        if budget_breakdown.activities > budget_breakdown.total_budget * 0.4:
            recommendations.append("🎯 Consider reducing activity costs to balance your budget across all categories")
        
        if budget_breakdown.food < budget_breakdown.total_budget * 0.15:
            recommendations.append("🍽️ You might want to allocate more budget for food experiences - local cuisine is a key part of travel")
        
        if budget_breakdown.accommodation > budget_breakdown.total_budget * 0.6:
            recommendations.append("🏨 Consider reducing accommodation costs to free up budget for activities and dining")
        
        # Group size specific recommendations
        if request.group_size > 4:
            recommendations.extend([
                "👥 Group discounts: Look for group rates on accommodations, activities, and transportation",
                "🍽️ Dining: Consider family-style dining or sharing dishes to try more variety",
                "🚌 Transportation: Consider group transportation options for better value"
            ])
        
        # Destination-specific recommendations
        if "culture" in [pref.value for pref in request.travel_preferences]:
            recommendations.append("🏛️ Cultural sites often have free or discounted entry on certain days - check local schedules")
        
        if "food" in [pref.value for pref in request.travel_preferences]:
            recommendations.append("🍴 Food tours and cooking classes offer great value for experiencing local cuisine")
        
        return recommendations
    
    def _calculate_budget_utilization(self, budget_breakdown: BudgetBreakdown) -> Dict[str, float]:
        """Calculate budget utilization percentages"""
        
        total = budget_breakdown.total_budget
        
        return {
            "accommodation_percentage": (budget_breakdown.accommodation / total) * 100,
            "food_percentage": (budget_breakdown.food / total) * 100,
            "activities_percentage": (budget_breakdown.activities / total) * 100,
            "transportation_percentage": (budget_breakdown.transportation / total) * 100,
            "miscellaneous_percentage": (budget_breakdown.miscellaneous / total) * 100
        }
