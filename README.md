# Smart Event Planner

## Project Description

The Smart Event Planner is a web application designed to assist users in planning outdoor events by providing real-time weather information, calculating weather suitability scores, and suggesting alternative dates with more favorable weather conditions. The application integrates with the OpenWeatherMap API to fetch current and forecast weather data, helping users make informed decisions for their events.

## Features

*   **Event Creation:** Users can input event details including event name, location, date, and type (e.g., Cricket, Wedding, Hiking, Corporate, Other).
*   **Weather Integration:** Fetches real-time weather data and 5-day forecasts from OpenWeatherMap.
*   **Weather Suitability Scoring:** Calculates a suitability score for the event date based on predefined weather criteria for different event types.
*   **Weather-based Recommendations:** Provides recommendations if weather conditions are not ideal for the chosen event type.
*   **Alternative Date Suggestions:** Suggests up to three alternative dates within the 5-day forecast period that have better weather suitability scores.
*   **User-Friendly Interface:** A simple web interface for easy event input and clear display of weather details, suitability scores, and alternative dates.
*   **Robust Error Handling:** Provides clear messages to the user regarding API limitations, location not found, or other issues during weather data retrieval.

## Prerequisites

Before running the application, ensure you have the following installed:

*   Python 3.8+
*   `pip` (Python package installer)
*   An API key from [OpenWeatherMap](https://openweathermap.org/api).

## Installation

1.  **Clone the repository (if applicable) or navigate to the project directory:**

    ```bash
    cd /path/to/smart-event-planner
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**

    *   **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Set your OpenWeatherMap API key as an environment variable named `OPENWEATHER_API_KEY`.

*   **On Windows (Command Prompt):**
    ```cmd
    set OPENWEATHER_API_KEY=YOUR_API_KEY_HERE
    ```
*   **On Windows (PowerShell):**
    ```powershell
    $env:OPENWEATHER_API_KEY="YOUR_API_KEY_HERE"
    ```
*   **On macOS/Linux:**
    ```bash
    export OPENWEATHER_API_KEY=YOUR_API_KEY_HERE
    ```

    Replace `YOUR_API_KEY_HERE` with your actual OpenWeatherMap API key.

## Usage

1.  **Run the FastAPI application:**

    ```bash
    uvicorn app.main:app --reload
    ```

    The application will typically run on `http://127.0.0.1:8000` or `http://localhost:8000`.

2.  **Access the application:**

    Open your web browser and navigate to `http://localhost:8000`.

3.  **Plan an Event:**

    Fill in the event details (Name, Location, Date, Event Type) and click "Check Weather & Suitability". The application will display weather information, a suitability score, recommendations, and alternative dates if available.

## API Limitations

This application uses the free tier of the OpenWeatherMap API, which has the following limitations:

*   **5-Day Forecast:** Weather forecasts are only available for up to 5 days into the future. If you select a date beyond this range, the application will display a message indicating this limitation.
*   **No Historical Data:** Weather data for past dates is not available through this service. If you select a past date, a relevant message will be displayed.

## Folder Structure

```
smart-event-planner/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/ 
│   │   └── models.py
│   ├── routers/
│   │   ├── events.py
│   │   └── weather.py
│   ├── schemas/
│   │   └── schemas.py
│   ├── services/
│   │   ├── event_service.py
│   │   └── weather_services.py
│   ├── static/
│   │   └── style.css
│   └── templates/
│       └── index.html
├── events.db
├── requirements.txt
└── venv/
``` 