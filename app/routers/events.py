from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date
from app.schemas.schemas import Event, EventCreate, EventWeatherResponse, AlternativeDate
from app.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=Event)
def create_event(event: EventCreate):
    return EventService.create_event(event.dict())

@router.get("/", response_model=List[Event])
def list_events():
    return EventService.get_all_events()

@router.get("/{event_id}", response_model=Event)
def get_event(event_id: int):
    event = EventService.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put("/{event_id}", response_model=Event)
def update_event(event_id: int, event_data: EventCreate):
    updated_event = EventService.update_event(event_id, event_data.dict())
    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated_event

@router.get("/{event_id}/weather", response_model=EventWeatherResponse)
def check_event_weather(event_id: int):
    result = EventService.check_event_weather(event_id)
    if not result:
        raise HTTPException(status_code=404, detail="Event or weather data not found")
    return result

@router.get("/{event_id}/alternatives", response_model=List[AlternativeDate])
def get_alternative_dates(event_id: int):
    alternatives = EventService.get_alternative_dates(event_id)
    if not alternatives:
        raise HTTPException(status_code=404, detail="No alternatives found or event not found")
    return alternatives