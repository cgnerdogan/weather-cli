import requests

city = input("Enter a city: ")

url = "https://geocoding-api.open-meteo.com/v1/search"

params = {
    "name": city,
    "count": 1
}

response = requests.get(url, params=params, timeout=10)
response.raise_for_status()

data = response.json()

if not data.get("results"):
    print("City not found.")
else:
    location = data["results"][0]

    latitude = location["latitude"]
    longitude = location["longitude"]

    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m",
        "timezone": "auto"
    }

    weather_response = requests.get(
        weather_url, params=weather_params, timeout=10
    )

    weather_response.raise_for_status()

    weather_data = weather_response.json()
    current = weather_data["current"]

    print()
    print("Location:", location["name"], location.get("country", "Unknown"))
    print("Temperature:", current["temperature_2m"], "°C")
    print("Feels like:", current["apparent_temperature"], "°C")
    print("Humidity:", current["relative_humidity_2m"], "%")
    print("Wind speed:", current["wind_speed_10m"], "km/h")
