import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_real_weather(city: str) -> str:
    """
    Fetches real-time weather data for a specific city using OpenWeatherMap API.
    Input should be just the city name (e.g., 'London', 'Tokyo').
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: OpenWeather API key is missing in .env file."

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric" # Use 'imperial' for Fahrenheit
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code == 200:
            weather_desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            return f"In {city}, it is currently {temp}°C (feels like {feels_like}°C) with {weather_desc}. Humidity is {humidity}%."
        else:
            return f"Error fetching weather: {data.get('message', 'Unknown error')}"
    except Exception as e:
        return f"Failed to connect to Weather API: {str(e)}"