from pydantic import BaseModel, Field
from datetime import date, datetime
from enum import Enum
from typing import Optional, List

class EventType(str, Enum):
    CRICKET = "cricket"
    WEDDING = "wedding"
    HIKING = "hiking"
    CORPORATE = "corporate"
    OTHER = "other"

class EventBase(BaseModel):
    name: str = Field(..., description="Name of the event")
    location: str = Field(..., description="Location of the event")
    event_date: date = Field(..., description="Date of the event")
    event_type: EventType = Field(..., description="Type of the event")
    description: Optional[str] = Field(None, description="Optional description of the event")
    start_time: Optional[datetime] = Field(None, description="Start time of the event")
    end_time: Optional[datetime] = Field(None, description="End time of the event")
    expected_attendees: Optional[int] = Field(None, description="Expected number of attendees")

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True

class WeatherData(BaseModel):
    temperature: float = Field(..., description="Temperature in Celsius")
    precipitation: float = Field(..., description="Precipitation in mm")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    conditions: str = Field(..., description="Weather conditions")
    humidity: float = Field(..., description="Humidity percentage")
    feels_like: Optional[float] = Field(None, description="Feels like temperature")
    pressure: Optional[float] = Field(None, description="Atmospheric pressure")
    visibility: Optional[float] = Field(None, description="Visibility in meters")
    cloud_coverage: Optional[float] = Field(None, description="Cloud coverage percentage")

class WeatherSuitability(str, Enum):
    GOOD = "Good"
    OKAY = "Okay"
    POOR = "Poor"

class EventWeatherResponse(BaseModel):
    event: Event
    weather: WeatherData
    suitability: WeatherSuitability
    score: int = Field(..., description="Weather suitability score (0-100)")
    recommendation: str = Field(..., description="Recommendation based on weather analysis")
    alternative_dates: Optional[List[date]] = Field(None, description="Suggested alternative dates")

class AlternativeDate(BaseModel):
    date: date
    weather: WeatherData
    score: int
    suitability: WeatherSuitability
    recommendation: str

class WeatherCache(BaseModel):
    location: str
    date: date
    data: WeatherData
    cached_at: datetime
    expires_at: datetime