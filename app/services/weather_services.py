import requests
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Tuple, Union
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    @staticmethod
    def get_weather(location: str, input_date: Union[datetime, date]) -> Optional[Dict]:
        try:
            logger.info(f"Fetching weather for location: {location}, date: {input_date}")
            
            target_date = input_date.date() if isinstance(input_date, datetime) else input_date
            
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={settings.openweather_api_key}"
            logger.info(f"Geocoding URL: {geo_url}")
            
            geo_response = requests.get(geo_url)
            geo_data = geo_response.json()
            
            if not geo_data:
                logger.error(f"Location not found: {location}")
                return {"error": f"Location '{location}' not found. Please check the spelling and try again."}
                
            lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
            logger.info(f"Location coordinates: lat={lat}, lon={lon}")
            
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={settings.openweather_api_key}"
            logger.info(f"Forecast URL: {forecast_url}")
            
            forecast_response = requests.get(forecast_url)
            forecast_data = forecast_response.json()
            
            if "list" not in forecast_data or not forecast_data["list"]:
                logger.error(f"Forecast data 'list' not found or empty for {location}")
                return {"error": "No forecast data available for this location."}

            daily_forecasts = {}
            for item in forecast_data['list']:
                main_data = item.get('main', {})
                weather_array = item.get('weather', [])
                
                if not main_data or not weather_array:
                    logger.warning(f"Skipping malformed forecast item (missing main or weather array): {item}")
                    continue
                
                forecast_datetime = datetime.fromtimestamp(item.get('dt', 0))
                forecast_date = forecast_datetime.date()
                
                if forecast_date not in daily_forecasts:
                    daily_forecasts[forecast_date] = []
                daily_forecasts[forecast_date].append(item)
            
            logger.info(f"Available forecast dates: {list(daily_forecasts.keys())}")
            
            if target_date in daily_forecasts:
                best_slot = min(daily_forecasts[target_date], 
                              key=lambda x: (x.get('rain', {}).get('3h', 0), 
                                           abs(x.get('main', {}).get('temp', 0) - 22))) 
                
                weather_data = {
                    'temperature': best_slot.get('main', {}).get('temp', 0.0), 
                    'precipitation': best_slot.get('rain', {}).get('3h', 0.0),
                    'wind_speed': best_slot.get('wind', {}).get('speed', 0.0), 
                    'conditions': best_slot.get('weather', [{}])[0].get('main', '') if best_slot.get('weather') else '', 
                    'humidity': best_slot.get('main', {}).get('humidity', 0), 
                    'time': datetime.fromtimestamp(best_slot.get('dt', 0)).strftime('%H:%M')
                }
                logger.info(f"Weather data found: {weather_data}")
                return weather_data
            else:
                today = date.today()
                if target_date < today:
                    error_msg = f"Weather data for past dates like {target_date} is not available via this service. Please select a future date."
                else:
                    error_msg = f"Weather forecast for {target_date} is beyond the 5-day limit of this service. Please select a date within the next 5 days."
                
                logger.warning(error_msg)
                return {"error": error_msg}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}", exc_info=True)
            return {"error": "Failed to connect to weather service. Please check your internet connection or API key."}
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}", exc_info=True)
            return {"error": "An unexpected error occurred while fetching weather data. Please try again."}

    @staticmethod
    def calculate_suitability_score(event_type: str, weather: Dict) -> Tuple[int, str, str]:
        
        required_keys = ['temperature', 'precipitation', 'wind_speed', 'conditions', 'humidity']
        if not all(key in weather for key in required_keys):
            missing_keys = [key for key in required_keys if key not in weather]
            logger.error(f"Missing required weather data keys for suitability calculation: {', '.join(missing_keys)}. Received weather data: {weather}")
            return 0, "Poor", f"Incomplete weather data: Missing {', '.join(missing_keys)}"

        temp = weather.get('temperature')
        precip = weather.get('precipitation')
        wind_speed_ms = weather.get('wind_speed')
        conditions = weather.get('conditions')
        humidity = weather.get('humidity')

        if not isinstance(temp, (int, float)) or \
           not isinstance(precip, (int, float)) or \
           not isinstance(wind_speed_ms, (int, float)) or \
           not isinstance(conditions, str) or \
           not isinstance(humidity, (int, float)):
            logger.error(f"Invalid type for weather data. Temperature: {type(temp)}, Precipitation: {type(precip)}, Wind Speed: {type(wind_speed_ms)}, Conditions: {type(conditions)}, Humidity: {type(humidity)}")
            return 0, "Poor", "Incomplete or invalid weather data received from API. Cannot calculate suitability."

        score = 0
        recommendation = []
        
        wind = wind_speed_ms * 3.6  

        if event_type in ['cricket', 'hiking']:
            
            if 15 <= temp <= 30:
                score += 30
            elif 10 <= temp < 15 or 30 < temp <= 35:
                score += 15
                recommendation.append("Temperature is slightly outside ideal range")
            else:
                recommendation.append("Temperature is not suitable for outdoor sports")
                
            if precip < 20:
                score += 25
            elif precip < 40:
                score += 10
                recommendation.append("Moderate precipitation expected")
            else:
                recommendation.append("High precipitation expected")
                
            if wind < 20:
                score += 20
            elif wind < 30:
                score += 10
                recommendation.append("Wind conditions are moderate")
            else:
                recommendation.append("Wind conditions are not suitable")
                
            if conditions in ['Clear', 'Clouds']:
                score += 25
            else:
                recommendation.append("Weather conditions are not ideal")
                
        elif event_type in ['wedding', 'corporate']:
            
            if 18 <= temp <= 28:
                score += 30
            elif 15 <= temp < 18 or 28 < temp <= 32:
                score += 15
                recommendation.append("Temperature is slightly outside ideal range")
            else:
                recommendation.append("Temperature is not suitable for formal events")
                
            if precip < 10:
                score += 30
            elif precip < 20:
                score += 15
                recommendation.append("Light precipitation expected")
            else:
                recommendation.append("Significant precipitation expected")
                
            if wind < 15:
                score += 25
            elif wind < 25:
                score += 10
                recommendation.append("Wind conditions are moderate")
            else:
                recommendation.append("Wind conditions are not suitable")
                
            if conditions in ['Clear', 'Clouds']:
                score += 15
            else:
                recommendation.append("Weather conditions are not ideal for formal events")
        
        if score >= 90:
            suitability = "Excellent"
        elif score >= 70:
            suitability = "Good"
        elif score >= 50:
            suitability = "Moderate"
        else:
            suitability = "Poor"
            
        return score, suitability, " ".join(recommendation) if recommendation else "Weather conditions are suitable"

    @staticmethod
    def get_alternative_dates(location: str, input_date: Union[datetime, date], event_type: str) -> List[Dict]:
        try:
            logger.info(f"Getting alternative dates for location: {location}, date: {input_date}, event type: {event_type}")
            
            target_date = input_date.date() if isinstance(input_date, datetime) else input_date

            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={settings.openweather_api_key}"
            geo_response = requests.get(geo_url)
            geo_data = geo_response.json()
            
            if not geo_data:
                logger.error(f"Location not found: {location}")
                return [{"error": f"Location '{location}' not found for alternative dates. Please check the spelling."}]
                
            lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
            logger.info(f"Location coordinates: lat={lat}, lon={lon}")
            
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={settings.openweather_api_key}"
            forecast_response = requests.get(forecast_url)
            forecast_data = forecast_response.json()
            
            if "list" not in forecast_data or not forecast_data["list"]:
                logger.error(f"Forecast data 'list' not found or empty for alternative dates for {location}")
                return [{"error": "No forecast data available for this location for alternative dates."}]

            daily_forecasts = {}
            for item in forecast_data['list']:
                main_data = item.get('main', {})
                weather_array = item.get('weather', [])

                if not main_data or not weather_array:
                    logger.warning(f"Skipping malformed alternative forecast item (missing main or weather array): {item}")
                    continue

                forecast_date = datetime.fromtimestamp(item.get('dt', 0)).date()
                if forecast_date not in daily_forecasts:
                    daily_forecasts[forecast_date] = []
                daily_forecasts[forecast_date].append(item)
            
            logger.info(f"Available forecast dates for alternatives: {list(daily_forecasts.keys())}")
            
            alternatives = []
            for forecast_date, slots in daily_forecasts.items():
                best_slot = min(slots, 
                              key=lambda x: (x.get('rain', {}).get('3h', 0), 
                                           abs(x.get('main', {}).get('temp', 0) - 22))) 
                
                weather = {
                    'temperature': best_slot.get('main', {}).get('temp', 0.0), 
                    'precipitation': best_slot.get('rain', {}).get('3h', 0.0),
                    'wind_speed': best_slot.get('wind', {}).get('speed', 0.0), 
                    'conditions': best_slot.get('weather', [{}])[0].get('main', '') if best_slot.get('weather') else '', 
                    'humidity': best_slot.get('main', {}).get('humidity', 0) 
                }
                
                score, suitability, recommendation = WeatherService.calculate_suitability_score(event_type, weather)
                
                alternative = {
                    'date': forecast_date.strftime('%Y-%m-%d'),
                    'time': datetime.fromtimestamp(best_slot.get('dt', 0)).strftime('%H:%M'),
                    'weather': weather,
                    'score': score,
                    'suitability': suitability,
                    'recommendation': recommendation
                }
                logger.info(f"Alternative date found: {alternative}")
                alternatives.append(alternative)
            
            sorted_alternatives = sorted(alternatives, key=lambda x: x['score'], reverse=True)[:3]
            logger.info(f"Returning {len(sorted_alternatives)} alternative dates")
            
            if not sorted_alternatives and (target_date < date.today() or target_date > date.today() + timedelta(days=5)):
                return [{"error": "Alternative date suggestions are only available for dates within the 5-day forecast range."}]

            return sorted_alternatives
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for alternative dates: {str(e)}", exc_info=True)
            return [{"error": "Failed to connect to weather service for alternative dates. Please check your internet connection or API key."}]
        except Exception as e:
            logger.error(f"Error getting alternative dates: {str(e)}", exc_info=True)
            return [{"error": "An unexpected error occurred while fetching alternative dates. Please try again."}]