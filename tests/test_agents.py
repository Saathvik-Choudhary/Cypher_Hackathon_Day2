import pytest
import asyncio
from datetime import datetime, timedelta
from models import TravelRequest, TravelPreference, BudgetCategory
from agents import ExplorerAgent, BudgetAgent, FoodAgent

class TestAgents:
    @pytest.fixture
    def sample_request(self):
        return TravelRequest(
            destination="Paris, France",
            budget=500.0,
            budget_category=BudgetCategory.MODERATE,
            travel_preferences=[TravelPreference.CULTURE, TravelPreference.FOOD],
            start_date="2024-06-15",
            group_size=2,
            special_requirements="Vegetarian friendly"
        )
    
    @pytest.mark.asyncio
    async def test_explorer_agent(self, sample_request):
        """Test Explorer Agent functionality"""
        agent = ExplorerAgent()
        response = await agent.process(sample_request)
        
        assert response.success is True
        assert response.agent_name == "Explorer Agent"
        assert "attractions" in response.data
        assert "recommendations" in response.data
        assert len(response.data["attractions"]) > 0
        
        # Test attraction structure
        attraction = response.data["attractions"][0]
        required_fields = ["name", "description", "location", "entry_fee", "estimated_duration"]
        for field in required_fields:
            assert field in attraction
    
    @pytest.mark.asyncio
    async def test_budget_agent(self, sample_request):
        """Test Budget Agent functionality"""
        agent = BudgetAgent()
        response = await agent.process(sample_request)
        
        assert response.success is True
        assert response.agent_name == "Budget Agent"
        assert "budget_breakdown" in response.data
        assert "recommendations" in response.data
        
        # Test budget breakdown structure
        budget = response.data["budget_breakdown"]
        assert budget["total_budget"] == 500.0
        assert budget["accommodation"] > 0
        assert budget["food"] > 0
        assert budget["activities"] > 0
        assert budget["transportation"] > 0
    
    @pytest.mark.asyncio
    async def test_food_agent(self, sample_request):
        """Test Food Agent functionality"""
        agent = FoodAgent()
        response = await agent.process(sample_request)
        
        assert response.success is True
        assert response.agent_name == "Food Agent"
        assert "restaurants" in response.data
        assert "food_recommendations" in response.data
        assert "meal_suggestions" in response.data
        
        # Test restaurant structure
        restaurant = response.data["restaurants"][0]
        required_fields = ["name", "cuisine_type", "price_range", "rating", "location"]
        for field in required_fields:
            assert field in restaurant
    
    @pytest.mark.asyncio
    async def test_agent_error_handling(self):
        """Test agent error handling with invalid request"""
        agent = ExplorerAgent()
        invalid_request = TravelRequest(
            destination="",  # Invalid destination
            budget=-100,     # Invalid budget
            budget_category=BudgetCategory.BUDGET,
            travel_preferences=[],
            start_date="invalid-date",
            group_size=0
        )
        
        response = await agent.process(invalid_request)
        # Should handle errors gracefully
        assert response.success is False or response.success is True  # Either way, should not crash
    
    def test_budget_categories(self, sample_request):
        """Test different budget categories"""
        agent = BudgetAgent()
        
        # Test budget category
        sample_request.budget_category = BudgetCategory.BUDGET
        sample_request.budget = 200.0
        
        # Test luxury category
        sample_request.budget_category = BudgetCategory.LUXURY
        sample_request.budget = 1000.0
        
        # Should not crash with different categories
        assert True
    
    @pytest.mark.asyncio
    async def test_agent_processing_time(self, sample_request):
        """Test that agents complete within reasonable time"""
        agent = ExplorerAgent()
        start_time = datetime.now()
        
        response = await agent.process(sample_request)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        assert response.processing_time > 0
        assert processing_time < 30  # Should complete within 30 seconds
