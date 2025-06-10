from typing import Optional, Dict, Union, List
import datetime
from datetime import timedelta
from app.schemas.schemas import Event, WeatherData, WeatherCache

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.schemas.schemas import Event

class Database:
    def __init__(self):
        self.events: Dict[int, Event] = {}
        self.next_id = 1
        self.weather_cache: Dict[str, WeatherCache] = {}
    
    def get_event(self, event_id: int) -> Optional[Event]:
        return self.events.get(event_id)
    
    def get_all_events(self) -> List[Event]:
        return list(self.events.values())
    
    def create_event(self, event: Event) -> Event:
        event.id = self.next_id
        event.created_at = datetime.datetime.now()
        event.updated_at = event.created_at
        self.events[self.next_id] = event
        self.next_id += 1
        return event
    
    def update_event(self, event_id: int, event_data: dict) -> Optional[Event]:
        if event_id not in self.events:
            return None
        event = self.events[event_id]
        for key, value in event_data.items():
            if hasattr(event, key):
                setattr(event, key, value)
        event.updated_at = datetime.datetime.now()
        return event
    
    def cache_weather(self, location: str, date: str, weather_data: WeatherData):
        cache_key = f"{location}_{date}"
        now = datetime.datetime.now()
        expires_at = now + timedelta(hours=3) 
        
        self.weather_cache[cache_key] = WeatherCache(
            location=location,
            date=datetime.datetime.strptime(date, "%Y-%m-%d").date(),
            data=weather_data,
            cached_at=now,
            expires_at=expires_at
        )
    
    def get_cached_weather(self, location: str, date: str) -> Optional[WeatherData]:
        cache_key = f"{location}_{date}"
        cached = self.weather_cache.get(cache_key)
        
        if cached:
            now = datetime.datetime.now()
            if now < cached.expires_at:
                return cached.data
            else:
                del self.weather_cache[cache_key]
        return None
    
    def clear_expired_cache(self):
        now = datetime.datetime.now()
        expired_keys = [
            key for key, cache in self.weather_cache.items()
            if now >= cache.expires_at
        ]
        for key in expired_keys:
            del self.weather_cache[key]

db = Database()

def get_db() -> Database:
    return db