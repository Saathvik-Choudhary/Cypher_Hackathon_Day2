from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import asyncio
from datetime import datetime
import os

from models import TravelRequest, TravelItinerary, TravelPreference, BudgetCategory
from orchestrator import TravelBuddyOrchestrator
from config import Config
from services.cache import cache_service

# Initialize FastAPI app
app = FastAPI(
    title="AI Weekend Travel Buddy",
    description="Multi-agent AI system for creating personalized 2-day travel itineraries",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = TravelBuddyOrchestrator()

# In-memory storage for demo purposes (in production, use a database)
itinerary_cache = {}

class CreateItineraryRequest(BaseModel):
    destination: str
    budget: float
    budget_category: str  # "budget", "moderate", "luxury"
    travel_preferences: List[str]  # List of preference strings
    start_date: str  # YYYY-MM-DD format
    group_size: int = 1
    special_requirements: Optional[str] = None

class ItineraryResponse(BaseModel):
    success: bool
    itinerary: Optional[TravelItinerary] = None
    error_message: Optional[str] = None
    processing_time: float

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the React frontend"""
    try:
        # Try to serve the built React app
        react_build_path = "frontend/build/index.html"
        if os.path.exists(react_build_path):
            return FileResponse(react_build_path)
        else:
            # Fallback to static directory if React build doesn't exist
            static_path = "static/index.html"
            if os.path.exists(static_path):
                return FileResponse(static_path)
            else:
                return HTMLResponse(content="""
                <html>
                    <head>
                        <title>AI Weekend Travel Buddy</title>
                        <style>
                            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                            .container { text-align: center; }
                            .api-link { display: inline-block; margin: 10px; padding: 10px 20px; background: #3b82f6; color: white; text-decoration: none; border-radius: 5px; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>AI Weekend Travel Buddy</h1>
                            <p>Welcome to the AI Weekend Travel Buddy API!</p>
                            <p>The React frontend is not built yet. Please build the frontend or use the API directly.</p>
                            <a href="/docs" class="api-link">API Documentation</a>
                            <a href="/api/health" class="api-link">Health Check</a>
                        </div>
                    </body>
                </html>
                """)
    except Exception as e:
        return HTMLResponse(content=f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>")

@app.post("/api/create-itinerary", response_model=ItineraryResponse)
async def create_itinerary(request: CreateItineraryRequest):
    """Create a personalized 2-day travel itinerary"""
    
    start_time = datetime.now()
    
    try:
        # Validate and convert request
        travel_request = TravelRequest(
            destination=request.destination,
            budget=request.budget,
            budget_category=BudgetCategory(request.budget_category),
            travel_preferences=[TravelPreference(pref) for pref in request.travel_preferences],
            start_date=request.start_date,
            group_size=request.group_size,
            special_requirements=request.special_requirements
        )
        
        # Generate cache key
        cache_key = f"itinerary_{travel_request.destination}_{travel_request.budget}_{travel_request.budget_category.value}_{travel_request.start_date}_{travel_request.group_size}"
        
        # Try to get from cache first
        cached_itinerary = await cache_service.get(cache_key)
        if cached_itinerary:
            processing_time = (datetime.now() - start_time).total_seconds()
            return ItineraryResponse(
                success=True,
                itinerary=TravelItinerary(**cached_itinerary),
                processing_time=processing_time
            )
        
        # Create itinerary using orchestrator
        itinerary = await orchestrator.create_itinerary(travel_request)
        
        # Cache the result (both in memory and Redis)
        await cache_service.set(cache_key, itinerary.dict(), ttl=3600)  # 1 hour cache
        itinerary_cache[cache_key] = itinerary
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ItineraryResponse(
            success=True,
            itinerary=itinerary,
            processing_time=processing_time
        )
        
    except ValueError as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        return ItineraryResponse(
            success=False,
            error_message=f"Invalid request parameters: {str(e)}",
            processing_time=processing_time
        )
    
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        return ItineraryResponse(
            success=False,
            error_message=f"Failed to create itinerary: {str(e)}",
            processing_time=processing_time
        )

@app.get("/api/itinerary/{cache_key}")
async def get_cached_itinerary(cache_key: str):
    """Get a cached itinerary by key"""
    
    if cache_key in itinerary_cache:
        return {"success": True, "itinerary": itinerary_cache[cache_key]}
    else:
        raise HTTPException(status_code=404, detail="Itinerary not found")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Weekend Travel Buddy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/destinations/popular")
async def get_popular_destinations():
    """Get list of popular destinations"""
    return {
        "destinations": [
            {"name": "Paris, France", "country": "France", "category": "culture"},
            {"name": "Tokyo, Japan", "country": "Japan", "category": "adventure"},
            {"name": "New York, USA", "country": "USA", "category": "nightlife"},
            {"name": "Barcelona, Spain", "country": "Spain", "category": "culture"},
            {"name": "Bangkok, Thailand", "country": "Thailand", "category": "food"},
            {"name": "Rome, Italy", "country": "Italy", "category": "culture"},
            {"name": "Sydney, Australia", "country": "Australia", "category": "adventure"},
            {"name": "Amsterdam, Netherlands", "country": "Netherlands", "category": "culture"},
            {"name": "Dubai, UAE", "country": "UAE", "category": "luxury"},
            {"name": "San Francisco, USA", "country": "USA", "category": "adventure"}
        ]
    }

@app.get("/api/preferences")
async def get_travel_preferences():
    """Get available travel preferences"""
    return {
        "preferences": [
            {"value": "adventure", "label": "Adventure & Outdoor Activities"},
            {"value": "culture", "label": "Culture & History"},
            {"value": "relaxation", "label": "Relaxation & Wellness"},
            {"value": "food", "label": "Food & Culinary Experiences"},
            {"value": "nightlife", "label": "Nightlife & Entertainment"},
            {"value": "family", "label": "Family-Friendly Activities"}
        ]
    }

@app.get("/api/budget-categories")
async def get_budget_categories():
    """Get available budget categories"""
    return {
        "categories": [
            {"value": "budget", "label": "Budget ($0-100 per day)", "range": "$0-100"},
            {"value": "moderate", "label": "Moderate ($100-300 per day)", "range": "$100-300"},
            {"value": "luxury", "label": "Luxury ($300+ per day)", "range": "$300+"}
        ]
    }

@app.post("/api/optimize-itinerary")
async def optimize_itinerary(request: CreateItineraryRequest):
    """Optimize an existing itinerary with real-time data"""
    
    start_time = datetime.now()
    
    try:
        # Validate and convert request
        travel_request = TravelRequest(
            destination=request.destination,
            budget=request.budget,
            budget_category=BudgetCategory(request.budget_category),
            travel_preferences=[TravelPreference(pref) for pref in request.travel_preferences],
            start_date=request.start_date,
            group_size=request.group_size,
            special_requirements=request.special_requirements
        )
        
        # Create optimized itinerary
        itinerary = await orchestrator.create_itinerary(travel_request)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ItineraryResponse(
            success=True,
            itinerary=itinerary,
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        return ItineraryResponse(
            success=False,
            error_message=f"Failed to optimize itinerary: {str(e)}",
            processing_time=processing_time
        )

@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    try:
        if hasattr(cache_service, 'redis_client') and cache_service.redis_client:
            info = cache_service.redis_client.info()
            return {
                "cache_type": "Redis",
                "connected_clients": info.get('connected_clients', 0),
                "used_memory": info.get('used_memory_human', '0B'),
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0)
            }
        else:
            return {
                "cache_type": "Memory",
                "cached_items": len(cache_service.memory_cache),
                "status": "active"
            }
    except Exception as e:
        return {"error": str(e)}

# Mount static files for React build
try:
    # First try to mount the React build directory
    if os.path.exists("frontend/build"):
        app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")
    else:
        # Fallback to static directory
        app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    # Static directory doesn't exist yet, that's okay
    pass

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=Config.DEBUG
    )
