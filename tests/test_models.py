import pytest
from datetime import datetime
from models import (
    TravelPreference, BudgetCategory, Attraction, Restaurant, 
    DayPlan, BudgetBreakdown, TravelRequest, TravelItinerary, AgentResponse
)

class TestModels:
    def test_travel_preference_enum(self):
        """Test TravelPreference enum values"""
        assert TravelPreference.ADVENTURE == "adventure"
        assert TravelPreference.CULTURE == "culture"
        assert TravelPreference.RELAXATION == "relaxation"
        assert TravelPreference.FOOD == "food"
        assert TravelPreference.NIGHTLIFE == "nightlife"
        assert TravelPreference.FAMILY == "family"
    
    def test_budget_category_enum(self):
        """Test BudgetCategory enum values"""
        assert BudgetCategory.BUDGET == "budget"
        assert BudgetCategory.MODERATE == "moderate"
        assert BudgetCategory.LUXURY == "luxury"
    
    def test_attraction_model(self):
        """Test Attraction model creation and validation"""
        attraction = Attraction(
            name="Eiffel Tower",
            description="Iconic iron tower in Paris",
            location="Champ de Mars, 7th arrondissement, Paris",
            opening_hours="9:30 AM - 11:45 PM",
            entry_fee=25.0,
            estimated_duration=120,
            popularity_score=9.5,
            uniqueness_score=8.0,
            category="landmark"
        )
        
        assert attraction.name == "Eiffel Tower"
        assert attraction.entry_fee == 25.0
        assert attraction.estimated_duration == 120
        assert attraction.popularity_score == 9.5
        assert attraction.uniqueness_score == 8.0
        assert attraction.category == "landmark"
    
    def test_attraction_validation(self):
        """Test Attraction model validation"""
        # Test popularity score bounds
        with pytest.raises(ValueError):
            Attraction(
                name="Test",
                description="Test",
                location="Test",
                estimated_duration=60,
                popularity_score=15.0,  # Invalid: > 10
                uniqueness_score=5.0,
                category="test"
            )
        
        # Test uniqueness score bounds
        with pytest.raises(ValueError):
            Attraction(
                name="Test",
                description="Test",
                location="Test",
                estimated_duration=60,
                popularity_score=5.0,
                uniqueness_score=-1.0,  # Invalid: < 0
                category="test"
            )
    
    def test_restaurant_model(self):
        """Test Restaurant model creation and validation"""
        restaurant = Restaurant(
            name="Le Comptoir du Relais",
            cuisine_type="French Bistro",
            price_range="$$",
            rating=4.5,
            location="9 Carrefour de l'Odéon, 75006 Paris",
            specialties=["Coq au Vin", "Bouillabaisse", "Tarte Tatin"],
            opening_hours="12:00 PM - 2:30 PM, 7:00 PM - 11:00 PM",
            estimated_cost_per_person=45.0,
            must_try_dishes=["Coq au Vin", "Crème Brûlée"],
            fun_tips=["Reservations recommended", "Try the wine selection"]
        )
        
        assert restaurant.name == "Le Comptoir du Relais"
        assert restaurant.cuisine_type == "French Bistro"
        assert restaurant.price_range == "$$"
        assert restaurant.rating == 4.5
        assert len(restaurant.specialties) == 3
        assert restaurant.estimated_cost_per_person == 45.0
    
    def test_restaurant_validation(self):
        """Test Restaurant model validation"""
        # Test rating bounds
        with pytest.raises(ValueError):
            Restaurant(
                name="Test",
                cuisine_type="Test",
                price_range="$",
                rating=6.0,  # Invalid: > 5
                location="Test",
                specialties=["Test"],
                estimated_cost_per_person=20.0,
                must_try_dishes=["Test"],
                fun_tips=["Test"]
            )
    
    def test_budget_breakdown_model(self):
        """Test BudgetBreakdown model"""
        budget = BudgetBreakdown(
            total_budget=500.0,
            accommodation=200.0,
            transportation=50.0,
            food=150.0,
            activities=100.0,
            miscellaneous=0.0,
            remaining_budget=0.0
        )
        
        assert budget.total_budget == 500.0
        assert budget.accommodation == 200.0
        assert budget.transportation == 50.0
        assert budget.food == 150.0
        assert budget.activities == 100.0
    
    def test_travel_request_model(self):
        """Test TravelRequest model"""
        request = TravelRequest(
            destination="Paris, France",
            budget=500.0,
            budget_category=BudgetCategory.MODERATE,
            travel_preferences=[TravelPreference.CULTURE, TravelPreference.FOOD],
            start_date="2024-06-15",
            group_size=2,
            special_requirements="Vegetarian friendly"
        )
        
        assert request.destination == "Paris, France"
        assert request.budget == 500.0
        assert request.budget_category == BudgetCategory.MODERATE
        assert len(request.travel_preferences) == 2
        assert request.start_date == "2024-06-15"
        assert request.group_size == 2
        assert request.special_requirements == "Vegetarian friendly"
    
    def test_travel_request_validation(self):
        """Test TravelRequest model validation"""
        # Test group size bounds
        with pytest.raises(ValueError):
            TravelRequest(
                destination="Paris, France",
                budget=500.0,
                budget_category=BudgetCategory.MODERATE,
                travel_preferences=[TravelPreference.CULTURE],
                start_date="2024-06-15",
                group_size=0  # Invalid: < 1
            )
        
        with pytest.raises(ValueError):
            TravelRequest(
                destination="Paris, France",
                budget=500.0,
                budget_category=BudgetCategory.MODERATE,
                travel_preferences=[TravelPreference.CULTURE],
                start_date="2024-06-15",
                group_size=15  # Invalid: > 10
            )
    
    def test_day_plan_model(self):
        """Test DayPlan model"""
        attraction = Attraction(
            name="Test Attraction",
            description="Test",
            location="Test",
            estimated_duration=60,
            popularity_score=5.0,
            uniqueness_score=5.0,
            category="test"
        )
        
        restaurant = Restaurant(
            name="Test Restaurant",
            cuisine_type="Test",
            price_range="$",
            rating=4.0,
            location="Test",
            specialties=["Test"],
            estimated_cost_per_person=20.0,
            must_try_dishes=["Test"],
            fun_tips=["Test"]
        )
        
        day_plan = DayPlan(
            day=1,
            date="2024-06-15",
            morning_activities=[attraction],
            lunch=restaurant,
            afternoon_activities=[],
            dinner=None,
            evening_activities=[],
            total_estimated_cost=50.0
        )
        
        assert day_plan.day == 1
        assert day_plan.date == "2024-06-15"
        assert len(day_plan.morning_activities) == 1
        assert day_plan.lunch is not None
        assert day_plan.total_estimated_cost == 50.0
    
    def test_travel_itinerary_model(self):
        """Test TravelItinerary model"""
        budget = BudgetBreakdown(
            total_budget=500.0,
            accommodation=200.0,
            transportation=50.0,
            food=150.0,
            activities=100.0,
            miscellaneous=0.0,
            remaining_budget=0.0
        )
        
        day_plan = DayPlan(
            day=1,
            date="2024-06-15",
            morning_activities=[],
            lunch=None,
            afternoon_activities=[],
            dinner=None,
            evening_activities=[],
            total_estimated_cost=50.0
        )
        
        itinerary = TravelItinerary(
            destination="Paris, France",
            total_budget=500.0,
            budget_breakdown=budget,
            day_plans=[day_plan],
            total_estimated_cost=100.0,
            budget_utilization_percentage=20.0,
            recommendations=["Test recommendation"],
            emergency_contacts=["Emergency: 911"],
            weather_forecast=[{"date": "2024-06-15", "temperature": 22}],
            external_data={"test": "data"}
        )
        
        assert itinerary.destination == "Paris, France"
        assert itinerary.total_budget == 500.0
        assert len(itinerary.day_plans) == 1
        assert itinerary.total_estimated_cost == 100.0
        assert itinerary.budget_utilization_percentage == 20.0
        assert len(itinerary.recommendations) == 1
        assert len(itinerary.emergency_contacts) == 1
        assert len(itinerary.weather_forecast) == 1
        assert "test" in itinerary.external_data
    
    def test_agent_response_model(self):
        """Test AgentResponse model"""
        response = AgentResponse(
            agent_name="Test Agent",
            success=True,
            data={"test": "data"},
            error_message=None,
            processing_time=1.5
        )
        
        assert response.agent_name == "Test Agent"
        assert response.success is True
        assert response.data == {"test": "data"}
        assert response.error_message is None
        assert response.processing_time == 1.5
    
    def test_model_serialization(self):
        """Test model serialization to dict"""
        attraction = Attraction(
            name="Test Attraction",
            description="Test",
            location="Test",
            estimated_duration=60,
            popularity_score=5.0,
            uniqueness_score=5.0,
            category="test"
        )
        
        # Test dict conversion
        attraction_dict = attraction.dict()
        assert isinstance(attraction_dict, dict)
        assert attraction_dict["name"] == "Test Attraction"
        assert attraction_dict["popularity_score"] == 5.0
        
        # Test JSON serialization
        import json
        json_str = attraction.json()
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["name"] == "Test Attraction"
