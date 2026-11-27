import requests

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.text import Text

console = Console()


def get_coordinates(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city,
        "count": 5
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    results = response.json().get("results", [])

    if not results:
        return None

    if len(results) == 1:
        return results[0]

    table = Table(title="Matching Locations")

    table.add_column("No.", style="cyan")
    table.add_column("City", style="bold white")
    table.add_column("Region")
    table.add_column("Country")

    for index, location in enumerate(results, start=1):
        table.add_row(
            str(index),
            location["name"],
            location.get("admin1", ""),
            location.get("country", "Unknown")
        )

    console.print(table)

    while True:
        choice = IntPrompt.ask("Select a location")

        if 1 <= choice <= len(results):
            return results[choice - 1]

        console.print("[red]Invalid selection.[/red]")


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

    content = Text()

    content.append(
        f"{current['temperature_2m']}°C\n\n",
        style="bold cyan"
    )

    content.append(
        f"Feels like: {current['apparent_temperature']}°C\n"
    )

    content.append(
        f"Humidity: {current['relative_humidity_2m']}%\n"
    )

    content.append(
        f"Wind speed: {current['wind_speed_10m']} km/h"
    )

    title = Text(
        f"{location['name']}, {location.get('country', 'Unknown')}",
        style="bold cyan"
    )

    console.print(
        Panel(content, title=title, border_style="cyan")
    )


def display_forecast(weather):
    daily = weather["daily"]

    table = Table(
        title="7-Day Weather Forecast",
        header_style="bold cyan",
        border_style="blue"
    )

    table.add_column("Date", style="white")
    table.add_column("High", style="red")
    table.add_column("Low", style="cyan")
    table.add_column("Precipitation")

    for i in range(len(daily["time"])):
        rain = daily["precipitation_probability_max"][i]

        if rain is None:
            rain_text = Text("N/A", style="dim")
        elif rain >= 50:
            rain_text = Text(f"{rain}%", style="yellow")
        else:
            rain_text = Text(f"{rain}%", style="green")

        table.add_row(
            daily["time"][i],
            f"{daily['temperature_2m_max'][i]}°C",
            f"{daily['temperature_2m_min'][i]}°C",
            rain_text
        )

    console.print(table)


def main():
    console.print(
        Panel(
            "[bold cyan]WEATHER CLI[/bold cyan]\n"
            "Real-time weather and forecasts",
            border_style="cyan"
        )
    )

    city = Prompt.ask("Enter a city").strip()

    if not city:
        console.print("[red]Please enter a city name.[/red]")
        return

    try:
        location = get_coordinates(city)

        if location is None:
            console.print("[red]City not found.[/red]")
            return

        with console.status("[cyan]Retrieving weather data..."):
            weather = get_weather(
                location["latitude"],
                location["longitude"]
            )

        display_weather(location, weather)
        display_forecast(weather)

        console.print(
            "\n[dim]Weather data provided by Open-Meteo[/dim]"
        )

    except requests.exceptions.Timeout:
        console.print("[red]Request timed out. Please try again.[/red]")

    except requests.exceptions.ConnectionError:
        console.print("[red]Connection failed. Check your internet connection.[/red]")

    except requests.exceptions.RequestException:
        console.print("[red]An error occurred while contacting the API.[/red]")


if __name__ == "__main__":
    main()
