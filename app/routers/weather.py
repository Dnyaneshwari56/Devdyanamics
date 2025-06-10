from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date
from app.schemas.schemas import WeatherData, EventWeatherResponse, AlternativeDate
from app.services.weather_services import WeatherService
from app.services.event_service import EventService

router = APIRouter(prefix="/weather", tags=["weather"])

@router.get("/{location}/{target_date}", response_model=WeatherData)
def get_weather(location: str, target_date: date):
    weather = WeatherService.get_weather(location, target_date)
    if not weather:
        raise HTTPException(status_code=404, detail="Weather data not available")
    return weather

@router.get("/cache/status")
def get_cache_status():
    from app.database import db
    cache_info = {
        "total_cached": len(db.weather_cache),
        "locations": list(set(cache.location for cache in db.weather_cache.values())),
        "dates": list(set(cache.date for cache in db.weather_cache.values()))
    }
    return cache_info

@router.get("/cache/clear")
def clear_cache():
    from app.database import db
    db.clear_expired_cache()
    return {"message": "Cache cleared successfully"}

@router.get("/test/invalid-location")
def test_invalid_location():
    try:
        weather = WeatherService.get_weather("InvalidCity123", date.today())
        if not weather:
            return {"status": "error", "message": "Location not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/test/api-downtime")
def test_api_downtime():
    original_key = settings.openweather_api_key
    settings.openweather_api_key = "invalid_key"
    try:
        weather = WeatherService.get_weather("Mumbai", date.today())
        return {"status": "error", "message": "API should have failed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        settings.openweather_api_key = original_key

@router.post("/events/{event_id}/weather-check", response_model=EventWeatherResponse)
def check_event_weather(event_id: int):
    result = EventService.check_event_weather(event_id)
    if not result:
        raise HTTPException(status_code=404, detail="Event or weather data not found")
    return result

@router.get("/events/{event_id}/alternatives", response_model=List[AlternativeDate])
def get_alternative_dates(event_id: int):
    alternatives = EventService.get_alternative_dates(event_id)
    if not alternatives:
        raise HTTPException(status_code=404, detail="No alternatives found or event not found")
    return alternatives

@router.get("/events/{event_id}/suitability", response_model=EventWeatherResponse)
def get_event_suitability(event_id: int):
    result = EventService.check_event_weather(event_id)
    if not result:
        raise HTTPException(status_code=404, detail="Event or weather data not found")
    return result