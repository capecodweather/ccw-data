import json
from datetime import datetime, timezone

import requests

OUTPUT_FILE = "current_conditions.json"

STATION = "KHYA"
NWS_URL = f"https://api.weather.gov/stations/{STATION}/observations/latest"


def degrees_to_compass(deg):
    directions = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW",
    ]
    ix = int((deg + 11.25) / 22.5) % 16
    return directions[ix]


def c_to_f(c):
    return int(round(c * 9 / 5 + 32))


def mps_to_mph(ms):
    return int(round(ms * 2.23694))


def main():

    print("Fetching NWS observation:", NWS_URL)

    headers = {
        "User-Agent": "CapeCodWeather App (contact: capecodweather.net)"
    }

    resp = requests.get(NWS_URL, headers=headers, timeout=20)
    resp.raise_for_status()

    obs = resp.json()["properties"]

    # Temperature
    temp_c = obs["temperature"]["value"]
    temperature_f = c_to_f(temp_c) if temp_c is not None else 0

    # Wind
    wind_speed_ms = obs["windSpeed"]["value"]
    wind_dir_deg = obs["windDirection"]["value"]

    if wind_speed_ms is None:
        wind_speed_mph = 0
    else:
        wind_speed_mph = mps_to_mph(wind_speed_ms)

    if wind_dir_deg is None:
        wind_direction = "--"
    else:
        wind_direction = degrees_to_compass(wind_dir_deg)

    # Condition text → simplified category
    desc = (obs["textDescription"] or "").lower()

    if "snow" in desc:
        condition = "snow"
    elif "rain" in desc or "shower" in desc:
        condition = "rain"
    elif "cloud" in desc or "overcast" in desc:
        condition = "cloudy"
    elif "clear" in desc or "sunny" in desc:
        condition = "clear"
    else:
        condition = "unknown"

    # Observation time
    timestamp = obs["timestamp"]
    observed_at = (
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        .astimezone()
        .isoformat()
    )

    data = {
        "station_id": STATION,
        "location_name": "Hyannis Area",
        "temperature_f": temperature_f,
        "wind_direction": wind_direction,
        "wind_speed_mph": wind_speed_mph,
        "condition": condition,
        "observed_at": observed_at,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("Updated", OUTPUT_FILE)


if __name__ == "__main__":
    main()

