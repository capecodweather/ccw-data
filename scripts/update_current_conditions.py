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
    Convert value to mph based on NWS unitCode (UCUM-ish strings).
    Common ones seen:
      - unit:m_s-1   (meters/second)
      - unit:km_h-1  (kilometers/hour)
      - unit:kn      (knots)  [rare but handle it]
    """
    if value is None:
        return 0

    u = (unit_code or "").strip().lower()

    if u == "unit:m_s-1":
        mph = value * 2.2369362920544
    elif u == "unit:km_h-1":
        mph = value * 0.62137119223733
    elif u == "unit:kn":
        mph = value * 1.1507794480235
    else:
        # Safe fallback: many stations *should* be m/s,
        # but we print debug so you can see what unitCode you got.
        mph = value * 2.2369362920544

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

    # Temperature
    temp_c = obs.get("temperature", {}).get("value")
    temperature_f = c_to_f(temp_c) if temp_c is not None else 0

    # Wind direction
    wind_dir_deg = obs.get("windDirection", {}).get("value")
    wind_direction = degrees_to_compass(float(wind_dir_deg)) if wind_dir_deg is not None else "--"

    # Wind speed (sustained)
    ws = obs.get("windSpeed", {})
    wind_speed_val = ws.get("value")
    wind_speed_unit = ws.get("unitCode")
    wind_speed_mph = to_mph(wind_speed_val, wind_speed_unit)

    # Wind gust
    wg = obs.get("windGust", {})
    wind_gust_val = wg.get("value")
    wind_gust_unit = wg.get("unitCode")
    wind_gust_mph = to_mph(wind_gust_val, wind_gust_unit) if wind_gust_val is not None else None

    # Condition text → simplified category
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

    # Observation time
    timestamp = obs.get("timestamp")  # ISO8601
    observed_at = ""
    if timestamp:
        observed_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).astimezone().isoformat()

    # DEBUG: prints to help you verify the conversion
    print("RAW windSpeed:", wind_speed_val, wind_speed_unit)
    print("RAW windGust :", wind_gust_val, wind_gust_unit)
    print("MPH sustained:", wind_speed_mph, "gust:", wind_gust_mph)

    data = {
        "station_id": STATION,
        "location_name": "Hyannis Area",
        "temperature_f": temperature_f,
        "wind_direction": wind_direction,
        "wind_speed_mph": wind_speed_mph,
        "wind_gust_mph": wind_gust_mph,  # extra field (optional)
        "condition": condition,
        "observed_at": observed_at,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("Updated", OUTPUT_FILE)


if __name__ == "__main__":
    main()
