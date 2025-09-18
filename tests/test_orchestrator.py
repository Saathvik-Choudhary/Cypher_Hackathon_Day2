import pytest
import asyncio
from datetime import datetime
from models import TravelRequest, TravelPreference, BudgetCategory
from orchestrator import TravelBuddyOrchestrator

class TestOrchestrator:
    @pytest.fixture
    def sample_request(self):
        return TravelRequest(
            destination="Tokyo, Japan",
            budget=600.0,
            budget_category=BudgetCategory.MODERATE,
            travel_preferences=[TravelPreference.ADVENTURE, TravelPreference.FOOD],
            start_date="2024-07-01",
            group_size=1,
            special_requirements="English speaking staff preferred"
        )
    
    @pytest.fixture
    def orchestrator(self):
        return TravelBuddyOrchestrator()
    
    @pytest.mark.asyncio
    async def test_create_itinerary(self, orchestrator, sample_request):
        """Test complete itinerary creation"""
        itinerary = await orchestrator.create_itinerary(sample_request)
        
        # Test basic structure
        assert itinerary.destination == "Tokyo, Japan"
        assert itinerary.total_budget == 600.0
        assert len(itinerary.day_plans) == 2
        assert itinerary.budget_breakdown is not None
        assert len(itinerary.recommendations) > 0
        assert len(itinerary.emergency_contacts) > 0
    
    @pytest.mark.asyncio
    async def test_day_plans_structure(self, orchestrator, sample_request):
        """Test day plans structure"""
        itinerary = await orchestrator.create_itinerary(sample_request)
        
        for i, day_plan in enumerate(itinerary.day_plans):
            assert day_plan.day == i + 1
            assert day_plan.date is not None
            assert day_plan.total_estimated_cost >= 0
            # Should have some activities
            assert len(day_plan.morning_activities) > 0 or len(day_plan.afternoon_activities) > 0
    
    @pytest.mark.asyncio
    async def test_budget_breakdown(self, orchestrator, sample_request):
        """Test budget breakdown accuracy"""
        itinerary = await orchestrator.create_itinerary(sample_request)
        
        budget = itinerary.budget_breakdown
        assert budget.total_budget == 600.0
        assert budget.accommodation > 0
        assert budget.food > 0
        assert budget.activities > 0
        assert budget.transportation > 0
        
        # Total allocated should not exceed total budget
        total_allocated = (budget.accommodation + budget.food + 
                          budget.activities + budget.transportation + 
                          budget.miscellaneous)
        assert total_allocated <= budget.total_budget
    
    @pytest.mark.asyncio
    async def test_budget_utilization(self, orchestrator, sample_request):
        """Test budget utilization calculation"""
        itinerary = await orchestrator.create_itinerary(sample_request)
        
        assert itinerary.budget_utilization_percentage >= 0
        assert itinerary.budget_utilization_percentage <= 100
        
        # Should be reasonable utilization
        assert itinerary.budget_utilization_percentage > 50  # At least 50% utilized
    
    @pytest.mark.asyncio
    async def test_different_destinations(self, orchestrator):
        """Test with different destinations"""
        destinations = ["New York, USA", "London, UK", "Sydney, Australia"]
        
        for destination in destinations:
            request = TravelRequest(
                destination=destination,
                budget=400.0,
                budget_category=BudgetCategory.BUDGET,
                travel_preferences=[TravelPreference.CULTURE],
                start_date="2024-08-01",
                group_size=1
            )
            
            itinerary = await orchestrator.create_itinerary(request)
            assert itinerary.destination == destination
            assert len(itinerary.day_plans) == 2
    
    @pytest.mark.asyncio
    async def test_different_budget_categories(self, orchestrator):
        """Test with different budget categories"""
        categories = [BudgetCategory.BUDGET, BudgetCategory.MODERATE, BudgetCategory.LUXURY]
        
        for category in categories:
            request = TravelRequest(
                destination="Paris, France",
                budget=300.0 if category == BudgetCategory.BUDGET else 
                       600.0 if category == BudgetCategory.MODERATE else 1200.0,
                budget_category=category,
                travel_preferences=[TravelPreference.FOOD],
                start_date="2024-09-01",
                group_size=2
            )
            
            itinerary = await orchestrator.create_itinerary(request)
            assert itinerary.budget_breakdown.total_budget > 0
    
    @pytest.mark.asyncio
    async def test_group_size_handling(self, orchestrator):
        """Test different group sizes"""
        group_sizes = [1, 2, 4, 6]
        
        for group_size in group_sizes:
            request = TravelRequest(
                destination="Barcelona, Spain",
                budget=500.0,
                budget_category=BudgetCategory.MODERATE,
                travel_preferences=[TravelPreference.ADVENTURE],
                start_date="2024-10-01",
                group_size=group_size
            )
            
            itinerary = await orchestrator.create_itinerary(request)
            # Should handle different group sizes without errors
            assert itinerary is not None
    
    @pytest.mark.asyncio
    async def test_special_requirements(self, orchestrator):
        """Test special requirements handling"""
        request = TravelRequest(
            destination="Rome, Italy",
            budget=400.0,
            budget_category=BudgetCategory.MODERATE,
            travel_preferences=[TravelPreference.CULTURE],
            start_date="2024-11-01",
            group_size=1,
            special_requirements="Wheelchair accessible venues only"
        )
        
        itinerary = await orchestrator.create_itinerary(request)
        assert itinerary is not None
        # Should include accessibility considerations in recommendations
        assert len(itinerary.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_processing_time(self, orchestrator, sample_request):
        """Test that itinerary creation completes within reasonable time"""
        start_time = datetime.now()
        
        itinerary = await orchestrator.create_itinerary(sample_request)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        assert processing_time < 60  # Should complete within 60 seconds
        assert itinerary is not None
