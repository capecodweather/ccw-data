import requests
import json
import re
from datetime import datetime, timezone

METAR_URL = "https://tgftp.nws.noaa.gov/data/observations/metar/stations/HYA.TXT"
OUTPUT_FILE = "current_conditions.json"

def parse_metar(metar: str):
    """
    Very simple METAR parser for:
    - temperature (F)
    - wind direction & speed
    - sky condition
    """

    # Observation time (UTC from METAR header)
    obs_time = datetime.now(timezone.utc).astimezone().isoformat()

    # Temperature (C)
    temp_match = re.search(r"(M?\d{1,2})/(M?\d{1,2})", metar)
    temp_f = 0
    if temp_match:
        temp_c = int(temp_match.group(1).replace("M", "-"))
        temp_f = round(temp_c * 9 / 5 + 32)

    # Wind
    wind_match = re.search(r"(\d{3}|VRB)(\d{2})KT", metar)
    wind_dir = "--"
    wind_spd = 0
    if wind_match:
        wind_dir = wind_match.group(1)
        wind_spd = int(wind_match.group(2))

    # Sky condition (very simple mapping)
    if "SKC" in metar or "CLR" in metar:
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
