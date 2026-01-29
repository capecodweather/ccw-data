import json
from datetime import datetime

import requests

OUTPUT_FILE = "current_conditions.json"

STATION = "KHYA"
NWS_URL = f"https://api.weather.gov/stations/{STATION}/observations/latest"


def degrees_to_compass(deg: float) -> str:
    directions = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW",
    ]
    ix = int((deg + 11.25) / 22.5) % 16
    return directions[ix]


def c_to_f(c: float) -> int:
    return int(round(c * 9 / 5 + 32))


def to_mph(value: float, unit_code: str | None) -> int:
    """
    Convert NWS wind values to MPH.
    Handles:
      - km/h
      - m/s
      - knots
    """

    if value is None:
        return 0

    u = (unit_code or "").lower()

    if "km_h" in u:
        mph = value * 0.621371
    elif "m_s" in u:
        mph = value * 2.23694
    elif "kn" in u:
        mph = value * 1.15078
    else:
        # Safe fallback
        mph = value * 2.23694

    return int(round(mph))


def main():
    print("Fetching NWS observation:", NWS_URL)

    headers = {
        "User-Agent": "CapeCodWeather App (contact: capecodweather.net)",
        "Accept": "application/geo+json",
    }

    resp = requests.get(NWS_URL, headers=headers, timeout=20)
    resp.raise_for_status()

    obs = resp.json()["properties"]

    # -------------------
    # Temperature
    # -------------------

    temp_c = obs.get("temperature", {}).get("value")
    temperature_f = c_to_f(temp_c) if temp_c is not None else 0

    # -------------------
    # Wind (sustained)
    # -------------------

    ws = obs.get("windSpeed", {})
    wind_speed_val = ws.get("value")
    wind_speed_unit = ws.get("unitCode")

    wind_speed_mph = to_mph(wind_speed_val, wind_speed_unit)

    # -------------------
    # Wind Direction
    # -------------------

    wind_dir_deg = obs.get("windDirection", {}).get("value")

    # If calm or no data → CALM
    if wind_speed_mph == 0 or wind_dir_deg is None:
        wind_direction = "CALM"
    else:
        wind_direction = degrees_to_compass(float(wind_dir_deg))

    # -------------------
    # Wind Gust
    # -------------------

    wg = obs.get("windGust", {})
    wind_gust_val = wg.get("value")
    wind_gust_unit = wg.get("unitCode")

    if wind_gust_val is not None:
        wind_gust_mph = to_mph(wind_gust_val, wind_gust_unit)
    else:
        wind_gust_mph = None

    # -------------------
    # Condition
    # -------------------

    desc = (obs.get("textDescription") or "").lower()

    if "snow" in desc:
        condition = "snow"
    elif "rain" in desc or "shower" in desc or "drizzle" in desc:
        condition = "rain"
    elif "fog" in desc or "mist" in desc or "haze" in desc:
        condition = "fog"
    elif "cloud" in desc or "overcast" in desc:
        condition = "cloudy"
    elif "clear" in desc or "sunny" in desc:
        condition = "clear"
    else:
        condition = "unknown"

    # -------------------
    # Observation time
    # -------------------

    timestamp = obs.get("timestamp")
    observed_at = ""

    if timestamp:
        observed_at = (
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            .astimezone()
            .isoformat()
        )

    # -------------------
    # Debug output
    # -------------------

    print("RAW windSpeed:", wind_speed_val, wind_speed_unit)
    print("RAW windGust :", wind_gust_val, wind_gust_unit)
    print("MPH sustained:", wind_speed_mph, "gust:", wind_gust_mph)
    print("Direction:", wind_direction)

    # -------------------
    # Output JSON
    # -------------------

    data = {
        "station_id": STATION,
        "location_name": "Hyannis Area",
        "temperature_f": temperature_f,
        "wind_direction": wind_direction,
        "wind_speed_mph": wind_speed_mph,
        "wind_gust_mph": wind_gust_mph,
        "condition": condition,
        "observed_at": observed_at,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("Updated", OUTPUT_FILE)


if __name__ == "__main__":
    main()

