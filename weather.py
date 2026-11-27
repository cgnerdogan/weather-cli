import requests


def get_coordinates(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city,
        "count": 5
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    results = data.get("results", [])

    if not results:
        return None

    if len(results) == 1:
        return results[0]

    print("\nMatching locations:")

    for index, location in enumerate(results, start=1):
        name = location["name"]
        region = location.get("admin1", "")
        country = location.get("country", "Unknown")

        print(f"{index}. {name}, {region}, {country}")

    while True:
        try:
            choice = int(input("\nSelect a location: "))

            if 1 <= choice <= len(results):
                return results[choice - 1]

            print("Invalid selection.")

        except ValueError:
            print("Please enter a number.")


def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "forecast_days": 7,
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    return response.json()


def display_weather(location, weather):
    current = weather["current"]

    print()
    print("Location:", location["name"], location.get("country", "Unknown"))
    print("Temperature:", current["temperature_2m"], "°C")
    print("Feels like:", current["apparent_temperature"], "°C")
    print("Humidity:", current["relative_humidity_2m"], "%")
    print("Wind speed:", current["wind_speed_10m"], "km/h")


def display_forecast(weather):
    daily = weather["daily"]

    print("\n7-Day Forecast")
    print("-" * 50)

    for i in range(len(daily["time"])):
        date = daily["time"][i]
        maximum = daily["temperature_2m_max"][i]
        minimum = daily["temperature_2m_min"][i]
        rain = daily["precipitation_probability_max"][i]

        print(f"{date} | High: {maximum}°C | Low: {minimum}°C | Rain: {rain}%")


def main():
    city = input("Enter a city: ").strip()

    if not city:
        print("Please enter a city name.")
        return

    try:
        location = get_coordinates(city)

        if location is None:
            print("City not found.")
            return

        weather = get_weather(
            location["latitude"],
            location["longitude"]
        )

        display_weather(location, weather)
        display_forecast(weather)

    except requests.exceptions.Timeout:
        print("Request timed out. Please try again.")

    except requests.exceptions.ConnectionError:
        print("Connection failed. Check your internet connection.")

    except requests.exceptions.RequestException:
        print("An error occurred while contacting the API.")


if __name__ == "__main__":
    main()
