from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, time
from enum import Enum

class TravelPreference(str, Enum):
    ADVENTURE = "adventure"
    CULTURE = "culture"
    RELAXATION = "relaxation"
    FOOD = "food"
    NIGHTLIFE = "nightlife"
    FAMILY = "family"

class BudgetCategory(str, Enum):
    BUDGET = "budget"  # $0-100
    MODERATE = "moderate"  # $100-300
    LUXURY = "luxury"  # $300+

class Attraction(BaseModel):
    name: str
    description: str
    location: str
    opening_hours: Optional[str] = None
    entry_fee: Optional[float] = None
    estimated_duration: int = Field(description="Duration in minutes")
    travel_time_from_previous: Optional[int] = Field(description="Travel time in minutes", default=0)
    popularity_score: float = Field(ge=0, le=10, description="Popularity score from 0-10")
    uniqueness_score: float = Field(ge=0, le=10, description="Uniqueness score from 0-10")
    category: str = Field(description="Category like 'museum', 'park', 'landmark'")
    coordinates: Optional[Dict[str, float]] = None

class Restaurant(BaseModel):
    name: str
    cuisine_type: str
    price_range: str  # $, $$, $$$, $$$$
    rating: float = Field(ge=0, le=5)
    location: str
    specialties: List[str]
    opening_hours: Optional[str] = None
    estimated_cost_per_person: float
    must_try_dishes: List[str]
    fun_tips: List[str]
    coordinates: Optional[Dict[str, float]] = None

class DayPlan(BaseModel):
    day: int
    date: Optional[str] = None
    morning_activities: List[Attraction] = []
    lunch: Optional[Restaurant] = None
    afternoon_activities: List[Attraction] = []
    dinner: Optional[Restaurant] = None
    evening_activities: List[Attraction] = []
    total_estimated_cost: float = 0.0

class BudgetBreakdown(BaseModel):
    total_budget: float
    accommodation: float = 0.0
    transportation: float = 0.0
    food: float = 0.0
    activities: float = 0.0
    miscellaneous: float = 0.0
    remaining_budget: float = 0.0

class TravelRequest(BaseModel):
    destination: str
    budget: float
    budget_category: BudgetCategory
    travel_preferences: List[TravelPreference]
    start_date: str
    group_size: int = Field(default=1, ge=1, le=10)
    special_requirements: Optional[str] = None

class TravelItinerary(BaseModel):
    destination: str
    total_budget: float
    budget_breakdown: BudgetBreakdown
    day_plans: List[DayPlan]
    total_estimated_cost: float
    budget_utilization_percentage: float
    recommendations: List[str]
    emergency_contacts: List[str]
    created_at: datetime = Field(default_factory=datetime.now)

class AgentResponse(BaseModel):
    agent_name: str
    success: bool
    data: Dict[str, Any]
    error_message: Optional[str] = None
    processing_time: float
