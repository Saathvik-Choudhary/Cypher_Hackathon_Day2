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
        """Generate budget-specific recommendations"""
        
        recommendations = []
        
        # Budget category specific recommendations
        if request.budget_category.value == "budget":
            recommendations.extend([
                "Consider staying in hostels or budget hotels to maximize your accommodation budget",
                "Look for free walking tours and free museum days",
                "Eat at local markets and street food for authentic and affordable meals",
                "Use public transportation or walk between attractions"
            ])
        elif request.budget_category.value == "moderate":
            recommendations.extend([
                "Mix of mid-range hotels and unique accommodations",
                "Balance between restaurants and local food experiences",
                "Consider combo tickets for multiple attractions",
                "Use a mix of public transport and occasional taxis"
            ])
        else:  # luxury
            recommendations.extend([
                "Stay at premium hotels or unique boutique accommodations",
                "Dine at top-rated restaurants and try local specialties",
                "Book private tours and premium experiences",
                "Use private transportation or premium car services"
            ])
        
        # General recommendations
        if budget_breakdown.activities > budget_breakdown.total_budget * 0.3:
            recommendations.append("Consider reducing activity costs to balance your budget")
        
        if budget_breakdown.food < budget_breakdown.total_budget * 0.2:
            recommendations.append("You might want to allocate more budget for food experiences")
        
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
