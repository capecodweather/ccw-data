import json
import re
from datetime import datetime, timezone

import requests

OUTPUT_FILE = "current_conditions.json"


def get_cycle_url() -> str:
    """
    Build the correct METAR cycle URL based on current UTC hour.
    Example: 23Z.TXT
    """
    now_utc = datetime.now(timezone.utc)
    cycle = now_utc.strftime("%HZ")  # e.g., "23Z"
    return f"https://tgftp.nws.noaa.gov/data/observations/metar/cycles/{cycle}.TXT"


def extract_station_metar(text: str, station: str) -> str | None:
    """
    Find the METAR line for a specific station (e.g. HYA).
    Cycle files typically contain lines like:
      HYA 111953Z 30012KT ...
    """
    prefix = station + " "
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.strip()
    return None


def parse_metar(metar: str) -> dict:
    """
    Minimal, robust METAR parsing for CCW v1:
    - temperature (F)
    - wind direction + speed (mph)
    - simple sky/precip condition
    - observed time (local ISO-8601 timestamp of fetch time)
    """
    observed_at = datetime.now(timezone.utc).astimezone().isoformat()

    # Temperature group like: 02/M01 or M05/M10
    temp_match = re.search(r"\b(M?\d{1,2})/(M?\d{1,2})\b", metar)
    temperature_f = 0
    if temp_match:
        temp_c = int(temp_match.group(1).replace("M", "-"))
        temperature_f = round(temp_c * 9 / 5 + 32)

    # Wind group like: 30012KT or VRB03KT (gusts ignored for now)
    wind_match = re.search(r"\b(\d{3}|VRB)(\d{2})KT\b", metar)
    wind_direction = "--"
    wind_speed_mph = 0
    if wind_match:
        wind_direction = wind_match.group(1)
        wind_kt = int(wind_match.group(2))
        wind_speed_mph = round(wind_kt * 1.15078)

    # Simple condition mapping
    # Precip first
    if re.search(r"\bSN\b", metar):
        condition = "snow"
    elif re.search(r"\bRA\b", metar):
        condition = "rain"
    else:
        # Sky cover
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
        "observed_at": observed_at,
    }


def main() -> None:
    url = get_cycle_url()
    print(f"Fetching METAR cycle: {url}")

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    metar_text = response.text
    station_metar = extract_station_metar(metar_text, "HYA")

    if not station_metar:
        raise RuntimeError("HYA METAR not found in cycle file")

    data = parse_metar(station_metar)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("Updated current_conditions.json")
    print("METAR:", station_metar)


if __name__ == "__main__":
    main()
    if temp_match:
        temp_c = int(temp_match.group(1).replace("M", "-"))
        temp_f = round(temp_c * 9 / 5 + 32)

    # Wind (KT -> MPH)
    wind_match = re.search(r"(\d{3}|VRB)(\d{2})KT", metar)
    wind_dir = "--"
    wind_mph = 0
    if wind_match:
        wind_dir = wind_match.group(1)
        wind_kt = int(wind_match.group(2))
        wind_mph = round(wind_kt * 1.15078)

    # Sky / weather condition (simple mapping)
    if " SN" in metar:
        condition = "snow"
    elif " RA" in metar:
        condition = "rain"
    elif " BKN" in metar or " OVC" in metar:
        condition = "cloudy"
    elif " SCT" in metar or " FEW" in metar:
        condition = "partly_cloudy"
    elif " CLR" in metar or " SKC" in metar:
        condition = "clear"
    else:
        condition = "unknown"

    return {
        "station_id": "HYA",
        "location_name": "Hyannis Area",
        "temperature_f": temp_f,
        "wind_direction": wind_dir,
        "wind_speed_mph": wind_mph,
        "condition": condition,
        "observed_at": obs_time
    }

def main():
    url = get_cycle_url()
    print(f"Fetching METAR cycle: {url}")

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    metar_text = response.text

    station_metar = extract_station_metar(metar_text, "HYA")
    if not station_metar:
        raise RuntimeError("HYA METAR not found in cycle file")

    data = parse_metar(station_metar)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print("Updated current_conditions.json")
    print(station_metar)

if __name__ == "__main__":
    main()
        condition = "clear"
    elif "BKN" in metar or "OVC" in metar:
        condition = "cloudy"
    elif "SCT" in metar or "FEW" in metar:
        condition = "partly_cloudy"
    elif "RA" in metar:
        condition = "rain"
    elif "SN" in metar:
        condition = "snow"
    else:
        condition = "unknown"

    return {
        "station_id": "HYA",
        "location_name": "Hyannis Area",
        "temperature_f": temp_f,
        "wind_direction": wind_dir,
        "wind_speed_mph": wind_spd,
        "condition": condition,
        "observed_at": obs_time
    }

def main():
    response = requests.get(METAR_URL, timeout=15)
    response.raise_for_status()

    lines = response.text.strip().splitlines()
    metar = lines[-1]

    data = parse_metar(metar)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()
