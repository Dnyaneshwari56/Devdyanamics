from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.routers import events, weather
from app.config import settings
from app.services.weather_services import WeatherService
from app.services.event_service import EventService
from datetime import datetime, date
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Smart Event Planner API",
    description="API for planning outdoor events with weather considerations",
    version="1.0.0"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

app.include_router(events.router)
app.include_router(weather.router)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/check", response_class=HTMLResponse)
def check_event(request: Request, name: str = Form(...), location: str = Form(...), event_date: str = Form(...), event_type: str = Form(...)):
    weather_data = None
    alternatives_data = None
    score = None
    suitability = None
    recommendation = None
    try:
        date_obj = datetime.strptime(event_date, "%Y-%m-%d").date()
        
        weather_data = WeatherService.get_weather(location, date_obj)
        
        if weather_data and "error" in weather_data:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error": weather_data["error"]
            })
        
        if not weather_data:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error": "Could not retrieve weather data for this location and date."
            })

        score, suitability, recommendation = WeatherService.calculate_suitability_score(event_type, weather_data)
        
        if "Incomplete weather data" in recommendation or "Invalid weather data" in recommendation:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error": recommendation
            })

        alternatives_data = WeatherService.get_alternative_dates(location, date_obj, event_type)
        
        if alternatives_data and isinstance(alternatives_data, list) and alternatives_data and "error" in alternatives_data[0]:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "weather": weather_data,
                "score": score,
                "suitability": suitability,
                "recommendation": recommendation,
                "alternatives": [], 
                "error_alternatives": alternatives_data[0]["error"]
            })

        return templates.TemplateResponse("index.html", {
            "request": request,
            "weather": weather_data,
            "score": score,
            "suitability": suitability,
            "recommendation": recommendation,
            "alternatives": alternatives_data
        })
    except Exception as e:
        logger.exception("An unexpected server error occurred") 
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "An unexpected server error occurred. Please try again later." 
        })