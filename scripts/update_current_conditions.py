import json
import re
from datetime import datetime, timedelta, timezone

import requests

OUTPUT_FILE = "current_conditions.json"


# ------------------------
# Helpers
# ------------------------

def degrees_to_compass(deg):
    """
    Convert wind direction in degrees to 16-point compass.
    """
    directions = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW"
    ]
    ix = int((deg + 11.25) / 22.5) % 16
    return directions[ix]


def parse_metar_time(metar):
    """
    Parse METAR timestamp like 112353Z into local ISO-8601 time.
    """
    match = re.search(r"\b(\d{2})(\d{2})(\d{2})Z\b", metar)
    if not match:
        return datetime.now(timezone.utc).astimezone().isoformat()

    day, hour, minute = map(int, match.groups())

    now_utc = datetime.now(timezone.utc)

    obs_time = now_utc.replace(
        day=day,
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0
    )

    # Handle month rollover edge case
    if obs_time > now_utc + timedelta(hours=1):
        obs_time -= timedelta(days=1)

    return obs_time.astimezone().isoformat()


def get_cycle_url():
    now_utc = datetime.now(timezone.utc)
    cycle = now_utc.strftime("%HZ")
    return f"https://tgftp.nws.noaa.gov/data/observations/metar/cycles/{cycle}.TXT"


def extract_station_metar(text, station):
    prefix = station + " "
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.strip()
    return None


# ------------------------
# METAR parsing
# ------------------------

def parse_metar(metar):
    observed_at = parse_metar_time(metar)

    # Temperature (C → F)
    temp_match = re.search(r"\b(M?\d{1,2})/(M?\d{1,2})\b", metar)
    temperature_f = 0
    if temp_match:
        temp_c = int(temp_match.group(1).replace("M", "-"))
        temperature_f = int(round(temp_c * 9 / 5 + 32))

    # Wind
    wind_match = re.search(r"\b(\d{3})(\d{2})KT\b", metar)
    wind_direction = "--"
    wind_speed_mph = 0

    if wind_match:
        wind_deg = int(wind_match.group(1))
        wind_kt = int(wind_match.group(2))

        wind_direction = degrees_to_compass(wind_deg)
        wind_speed_mph = int(round(wind_kt * 1.15078))

    # Condition mapping
    if re.search(r"\bSN\b", metar):
        condition = "snow"
    elif re.search(r"\bRA\b", metar):
        condition = "rain"
    else:
        if re.search(r"\b(OVC|BKN)\d{3}\b", metar):
            condition = "cloudy"
        elif re.search(r"\b(SCT|FEW)\d{3}\b", metar):
            condition = "partly_cloudy"
        elif re.search(r"\b(CLR|SKC)\b", metar):
            condition = "clear"
        else:
            condition = "unknown"

    return {
        "station_id": "HYA",
        "location_name": "Hyannis Area",
        "temperature_f": temperature_f,
        "wind_direction": wind_direction,
        "wind_speed_mph": wind_speed_mph,
        "condition": condition,
        "observed_at": observed_at
    }


# ------------------------
# Main
# ------------------------

def main():
    url = get_cycle_url()
    print("Fetching METAR cycle:", url)

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    metar = extract_station_metar(response.text, "HYA")
    if not metar:
        raise RuntimeError("HYA METAR not found")

    data = parse_metar(metar)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("Updated current_conditions.json")
    print("METAR:", metar)


if __name__ == "__main__":
    main()

    now_utc = datetime.now(timezone.utc)

    obs_time = now_utc.replace(
        day=day,
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0
    )

    # Handle month rollover edge case
    if obs_time > now_utc + timedelta(hours=1):
        obs_time -= timedelta(days=1)

    return obs_time.astimezone().isoformat()


def get_cycle_url():
    now_utc = datetime.now(timezone.utc)
    cycle = now_utc.strftime("%HZ")
    return f"https://tgftp.nws.noaa.gov/data/observations/metar/cycles/{cycle}.TXT"


def extract_station_metar(text, station):
    prefix = station + " "
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.strip()
    return None


# ------------------------
# METAR parsing
# ------------------------

def parse_metar(metar):
    observed_at = parse_metar_time(metar)

    # Temperature (C → F)
    temp_match = re.search(r"\b(M?\d{1,2})/(M?\d{1,2})\b", metar)
    temperature_f = 0
    if temp_match:
        temp_c = int(temp_match.group(1).replace("M", "-"))
        temperature_f = int(round(temp_c * 9 / 5 + 32))

    # Wind
    wind_match = re.search(r"\b(\d{3})(\d{2})KT\b", metar)
    wind_direction = "--"
    wind_speed_mph = 0

    if wind_match:
        wind_deg = int(wind_match.group(1))
        wind_kt = int(wind_match.group(2))

        wind_direction = degrees_to_compass(wind_deg)
        wind_speed_mph = int(round(wind_kt * 1.15078))

    # Condition mapping
    if re.search(r"\bSN\b", metar):
        condition = "snow"
    elif re.search(r"\bRA\b", metar):
        condition = "rain"
    else:
        if re.search(r"\b(OVC|BKN)\d{3}\b", metar):
            condition = "cloudy"
        elif re.search(r"\b(SCT|FEW)\d{3}\b", metar):
            condition = "partly_cloudy"
        elif re.search(r"\b(CLR|SKC)\b", metar):
            condition = "clear"
        else:
            condition = "unknown"

    return {
        "station_id": "HYA",
        "location_name": "Hyannis Area",
        "temperature_f": temperature_f,
        "wind_direction": wind_direction,
        "wind_speed_mph": wind_speed_mph,
        "condition": condition,
        "observed_at": observed_at
    }


# ------------------------
# Main
# ------------------------

def main():
    url = get_cycle_url()
    print("Fetching METAR cycle:", url)

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    metar = extract_station_metar(response.text, "HYA")
    if not metar:
        raise RuntimeError("HYA METAR not found")

    data = parse_metar(metar)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("Updated current_conditions.json")
    print("METAR:", metar)


if __name__ == "__main__":
    main()
    wind_speed_mph = 0
    if wind_match:
        wind_direction = wind_match.group(1)
        wind_kt = int(wind_match.group(2))
        wind_speed_mph = int(round(wind_kt * 1.15078))

    # Condition mapping (simple)
    if re.search(r"\bSN\b", metar):
        condition = "snow"
    elif re.search(r"\bRA\b", metar):
        condition = "rain"
    else:
        if re.search(r"\b(OVC|BKN)\d{3}\b", metar):
            condition = "cloudy"
        elif re.search(r"\b(SCT|FEW)\d{3}\b", metar):
            condition = "partly_cloudy"
        elif re.search(r"\b(CLR|SKC)\b", metar):
            condition = "clear"
        else:
            condition = "unknown"

    return {
        "station_id": "KHYA",
        "location_name": "Hyannis Area",
        "temperature_f": temperature_f,
        "wind_direction": wind_direction,
        "wind_speed_mph": wind_speed_mph,
        "condition": condition,
        "observed_at": observed_at
    }


def main():
    url = get_cycle_url()
    print("Fetching METAR cycle:", url)

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    station_metar = extract_station_metar(response.text, "KHYA")
    if not station_metar:
        raise RuntimeError("HYA METAR not found in cycle file")

    data = parse_metar(station_metar)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("Updated", OUTPUT_FILE)
    print("METAR:", station_metar)


if __name__ == "__main__":
    main()
