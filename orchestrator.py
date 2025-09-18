import asyncio
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
from models import TravelRequest, TravelItinerary, DayPlan, BudgetBreakdown
from agents import ExplorerAgent, BudgetAgent, FoodAgent
from services.external_apis import ExternalAPIService

class TravelBuddyOrchestrator:
    def __init__(self):
        self.explorer_agent = ExplorerAgent()
        self.budget_agent = BudgetAgent()
        self.food_agent = FoodAgent()
    
    async def create_itinerary(self, request: TravelRequest) -> TravelItinerary:
        """Create a complete 2-day travel itinerary using multi-agent collaboration"""
        
        start_time = time.time()
        print(f"🚀 Starting itinerary creation for {request.destination}")
        
        # Phase 0: Gather real-time data
        print("🌐 Phase 0: Gathering real-time data...")
        external_data = await self._gather_external_data(request)
        
        # Phase 1: Parallel agent processing with external data
        print("📋 Phase 1: Gathering information from all agents...")
        agent_results = await self._run_agents_parallel(request, external_data)
        
        # Phase 2: Integrate results and create optimized day plans
        print("🗓️ Phase 2: Creating optimized day plans...")
        day_plans = await self._create_day_plans(agent_results, request, external_data)
        
        # Phase 3: Final budget reconciliation
        print("💰 Phase 3: Finalizing budget and recommendations...")
        final_budget = await self._reconcile_budget(agent_results, day_plans, request)
        
        # Phase 4: Create final itinerary with enhanced data
        print("✨ Phase 4: Assembling final itinerary...")
        itinerary = await self._assemble_itinerary(
            request, agent_results, day_plans, final_budget, external_data
        )
        
        total_time = time.time() - start_time
        print(f"✅ Itinerary created successfully in {total_time:.2f} seconds")
        
        return itinerary
    
    async def _gather_external_data(self, request: TravelRequest) -> Dict[str, Any]:
        """Gather real-time data from external APIs"""
        external_data = {}
        
        try:
            async with ExternalAPIService() as api_service:
                # Gather weather, places, and transportation data in parallel
                tasks = [
                    api_service.get_weather_forecast(request.destination, request.start_date),
                    api_service.get_places_info(request.destination, "tourist_attraction"),
                    api_service.get_places_info(request.destination, "restaurant")
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                external_data['weather'] = results[0] if not isinstance(results[0], Exception) else {}
                external_data['attractions'] = results[1] if not isinstance(results[1], Exception) else []
                external_data['restaurants'] = results[2] if not isinstance(results[2], Exception) else []
                
        except Exception as e:
            print(f"External API error: {e}")
            external_data = {
                'weather': {},
                'attractions': [],
                'restaurants': []
            }
        
        return external_data
    
    async def _run_agents_parallel(self, request: TravelRequest, external_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run all agents in parallel for maximum efficiency"""
        
        # Start all agents simultaneously
        tasks = [
            self.explorer_agent.process(request),
            self.budget_agent.process(request),
            self.food_agent.process(request)
        ]
        
        # Wait for all agents to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        agent_results = {}
        agent_names = ["explorer", "budget", "food"]
        
        for i, result in enumerate(results):
            agent_name = agent_names[i]
            
            if isinstance(result, Exception):
                print(f"❌ {agent_name} agent failed: {result}")
                agent_results[agent_name] = {
                    "success": False,
                    "error": str(result),
                    "data": {}
                }
            else:
                agent_results[agent_name] = result.dict()
                print(f"✅ {agent_name} agent completed in {result.processing_time:.2f}s")
        
        return agent_results
    
    async def _create_day_plans(self, agent_results: Dict[str, Any], request: TravelRequest, external_data: Dict[str, Any] = None) -> List[DayPlan]:
        """Create optimized day plans from agent results"""
        
        day_plans = []
        
        # Get attractions from explorer agent
        attractions = []
        if agent_results["explorer"]["success"]:
            attractions = agent_results["explorer"]["data"].get("attractions", [])
        
        # Get restaurants from food agent
        restaurants = []
        if agent_results["food"]["success"]:
            restaurants = agent_results["food"]["data"].get("restaurants", [])
            meal_suggestions = agent_results["food"]["data"].get("meal_suggestions", {})
        
        # Create Day 1 plan
        day1_plan = await self._create_single_day_plan(
            day=1,
            attractions=attractions[:len(attractions)//2] if attractions else [],
            restaurants=restaurants,
            meal_suggestions=meal_suggestions.get("day_1", {}),
            request=request
        )
        day_plans.append(day1_plan)
        
        # Create Day 2 plan
        day2_plan = await self._create_single_day_plan(
            day=2,
            attractions=attractions[len(attractions)//2:] if attractions else [],
            restaurants=restaurants,
            meal_suggestions=meal_suggestions.get("day_2", {}),
            request=request
        )
        day_plans.append(day2_plan)
        
        return day_plans
    
    async def _create_single_day_plan(self, day: int, attractions: List[Dict], 
                                    restaurants: List[Dict], meal_suggestions: Dict,
                                    request: TravelRequest) -> DayPlan:
        """Create a plan for a single day"""
        
        # Calculate date
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        current_date = start_date + timedelta(days=day-1)
        
        # Organize attractions by time of day
        morning_activities = attractions[:2] if len(attractions) >= 2 else attractions[:1]
        afternoon_activities = attractions[2:4] if len(attractions) >= 4 else attractions[1:3] if len(attractions) > 1 else []
        evening_activities = attractions[4:6] if len(attractions) >= 6 else attractions[2:4] if len(attractions) > 2 else []
        
        # Get meal suggestions
        lunch_restaurant = None
        dinner_restaurant = None
        
        if meal_suggestions:
            lunch_options = meal_suggestions.get("lunch", [])
            dinner_options = meal_suggestions.get("dinner", [])
            
            if lunch_options:
                lunch_restaurant = lunch_options[0]
            if dinner_options:
                dinner_restaurant = dinner_options[0]
        
        # Calculate estimated costs
        total_cost = 0.0
        
        # Add attraction costs
        for activity in morning_activities + afternoon_activities + evening_activities:
            if activity.get("entry_fee"):
                total_cost += activity["entry_fee"] * request.group_size
        
        # Add meal costs
        if lunch_restaurant and lunch_restaurant.get("estimated_cost_per_person"):
            total_cost += lunch_restaurant["estimated_cost_per_person"] * request.group_size
        
        if dinner_restaurant and dinner_restaurant.get("estimated_cost_per_person"):
            total_cost += dinner_restaurant["estimated_cost_per_person"] * request.group_size
        
        return DayPlan(
            day=day,
            date=current_date.strftime("%Y-%m-%d"),
            morning_activities=morning_activities,
            lunch=lunch_restaurant,
            afternoon_activities=afternoon_activities,
            dinner=dinner_restaurant,
            evening_activities=evening_activities,
            total_estimated_cost=total_cost
        )
    
    async def _reconcile_budget(self, agent_results: Dict[str, Any], 
                              day_plans: List[DayPlan], request: TravelRequest) -> BudgetBreakdown:
        """Reconcile budget based on actual planned activities"""
        
        # Get initial budget breakdown
        budget_breakdown = None
        if agent_results["budget"]["success"]:
            budget_data = agent_results["budget"]["data"].get("budget_breakdown", {})
            budget_breakdown = BudgetBreakdown(**budget_data)
        
        if not budget_breakdown:
            # Create default budget breakdown
            budget_breakdown = BudgetBreakdown(
                total_budget=request.budget,
                accommodation=request.budget * 0.4,
                transportation=request.budget * 0.1,
                food=request.budget * 0.3,
                activities=request.budget * 0.2
            )
        
        # Calculate actual costs from day plans
        total_activity_cost = sum(plan.total_estimated_cost for plan in day_plans)
        
        # Adjust budget based on actual costs
        if total_activity_cost > budget_breakdown.activities:
            # If activities cost more than budgeted, adjust other categories
            excess = total_activity_cost - budget_breakdown.activities
            budget_breakdown.activities = total_activity_cost
            budget_breakdown.miscellaneous = max(0, budget_breakdown.miscellaneous - excess)
        
        # Calculate remaining budget
        total_allocated = (budget_breakdown.accommodation + budget_breakdown.transportation + 
                          budget_breakdown.food + budget_breakdown.activities + 
                          budget_breakdown.miscellaneous)
        budget_breakdown.remaining_budget = budget_breakdown.total_budget - total_allocated
        
        return budget_breakdown
    
    async def _assemble_itinerary(self, request: TravelRequest, agent_results: Dict[str, Any],
                                day_plans: List[DayPlan], budget_breakdown: BudgetBreakdown, external_data: Dict[str, Any] = None) -> TravelItinerary:
        """Assemble the final travel itinerary"""
        
        # Calculate total estimated cost
        total_estimated_cost = sum(plan.total_estimated_cost for plan in day_plans)
        total_estimated_cost += budget_breakdown.accommodation + budget_breakdown.transportation
        
        # Calculate budget utilization
        budget_utilization = (total_estimated_cost / request.budget) * 100 if request.budget > 0 else 0
        
        # Collect recommendations from all agents
        all_recommendations = []
        
        if agent_results["explorer"]["success"]:
            explorer_recs = agent_results["explorer"]["data"].get("recommendations", [])
            all_recommendations.extend(explorer_recs)
        
        if agent_results["budget"]["success"]:
            budget_recs = agent_results["budget"]["data"].get("recommendations", [])
            all_recommendations.extend(budget_recs)
        
        if agent_results["food"]["success"]:
            food_recs = agent_results["food"]["data"].get("food_recommendations", [])
            all_recommendations.extend(food_recs)
        
        # Add weather-based recommendations
        if external_data and external_data.get('weather'):
            weather_recs = external_data['weather'].get('recommendations', [])
            all_recommendations.extend(weather_recs)
        
        # Add emergency contacts
        emergency_contacts = [
            "Local Emergency: 911 (or local emergency number)",
            "Tourist Information Center",
            "Your accommodation front desk",
            "Local embassy/consulate (if international travel)"
        ]
        
        # Add weather information to the itinerary
        weather_info = external_data.get('weather', {}) if external_data else {}
        
        return TravelItinerary(
            destination=request.destination,
            total_budget=request.budget,
            budget_breakdown=budget_breakdown,
            day_plans=day_plans,
            total_estimated_cost=total_estimated_cost,
            budget_utilization_percentage=budget_utilization,
            recommendations=all_recommendations,
            emergency_contacts=emergency_contacts,
            weather_forecast=weather_info.get('forecasts', []),
            external_data=external_data or {}
        )
