"""
Weather Module: Fetches real-time weather information using OpenWeatherMap API.
"""

import os
import logging
from typing import Dict, Any, Optional
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import requests
except ImportError:
    requests = None

logger = logging.getLogger(__name__)


class WeatherService:
    """Service to fetch and format weather data."""

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")

    def get_weather(self, city: str) -> str:
        """
        Fetch current weather for a given city and return a natural language response.
        """
        if not city or not city.strip():
            return "Please specify a city name to get the weather."

        city = city.strip()

        if not self.api_key or self.api_key == "your_openweathermap_api_key_here":
            return (
                f"I found {city}, but the OpenWeatherMap API key is not configured. "
                "Please add your OPENWEATHER_API_KEY in the .env file to enable live weather reports."
            )

        if requests is None:
            return "The 'requests' package is not installed. Please run 'pip install requests'."

        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=6)
            if response.status_code == 200:
                data = response.json()
                temp = round(data["main"]["temp"])
                feels_like = round(data["main"]["feels_like"])
                humidity = data["main"]["humidity"]
                desc = data["weather"][0]["description"]
                city_name = data.get("name", city)
                country = data.get("sys", {}).get("country", "")

                location = f"{city_name}, {country}" if country else city_name
                return (
                    f"The current weather in {location} is {temp}°C with {desc}. "
                    f"It feels like {feels_like}°C, and humidity is at {humidity}%."
                )
            elif response.status_code == 404:
                return f"Sorry, I couldn't find weather details for '{city}'. Please check the city name."
            elif response.status_code == 401:
                return "The provided OpenWeatherMap API key is invalid or unauthorized. Please verify your .env file."
            else:
                return f"Weather service returned an error ({response.status_code}). Please try again later."
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather request failed: {e}")
            return "I couldn't connect to the weather service. Please check your internet connection."
