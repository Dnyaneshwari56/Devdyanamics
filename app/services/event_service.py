from typing import List, Optional
from datetime import date
from app.schemas.schemas import Event, EventWeatherResponse, AlternativeDate
from app.database import get_db
db = get_db()
from app.services.weather_services import WeatherService

class EventService:
    @staticmethod
    def create_event(event_data: dict) -> Event:
        event = Event(**event_data)
        return db.create_event(event)
    
    @staticmethod
    def get_event(event_id: int) -> Optional[Event]:
        return db.get_event(event_id)
    
    @staticmethod
    def get_all_events() -> List[Event]:
        return db.get_all_events()
    
    @staticmethod
    def update_event(event_id: int, event_data: dict) -> Optional[Event]:
        return db.update_event(event_id, event_data)
    
    @staticmethod
    def check_event_weather(event_id: int) -> Optional[EventWeatherResponse]:
        event = db.get_event(event_id)
        if not event:
            return None
        
        weather = WeatherService.get_weather(event.location, event.event_date)
        if not weather:
            return None
        
        score, suitability, recommendation = WeatherService.calculate_suitability_score(
            event.event_type, weather
        )
        
        return EventWeatherResponse(
            event=event,
            weather=weather,
            suitability=suitability,
            score=score,
            recommendation=recommendation
        )
    
    @staticmethod
    def get_alternative_dates(event_id: int) -> Optional[List[AlternativeDate]]:
        event = db.get_event(event_id)
        if not event:
            return None
        
        alternatives = WeatherService.get_alternative_dates(
            event.location, event.event_date, event.event_type
        )
        
        return [
            AlternativeDate(
                date=alt["date"],
                weather=alt["weather"],
                score=alt["score"],
                suitability=alt["suitability"]
            )
            for alt in alternatives
        ]