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
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    return response.json()["current"]


def display_weather(location, weather):
    print()
    print("Location:", location["name"], location.get("country", "Unknown"))
    print("Temperature:", weather["temperature_2m"], "°C")
    print("Feels like:", weather["apparent_temperature"], "°C")
    print("Humidity:", weather["relative_humidity_2m"], "%")
    print("Wind speed:", weather["wind_speed_10m"], "km/h")


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

    except requests.exceptions.Timeout:
        print("Request timed out. Please try again.")

    except requests.exceptions.ConnectionError:
        print("Connection failed. Check your internet connection.")

    except requests.exceptions.RequestException:
        print("An error occurred while contacting the API.")


if __name__ == "__main__":
    main()
