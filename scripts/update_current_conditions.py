import json
import re
from datetime import datetime, timezone

import requests

OUTPUT_FILE = "current_conditions.json"


def get_cycle_url():
    now_utc = datetime.now(timezone.utc)
    cycle = now_utc.strftime("%HZ")  # e.g. "23Z"
    return "https://tgftp.nws.noaa.gov/data/observations/metar/cycles/{cycle}.TXT".format(cycle=cycle)


def extract_station_metar(text, station):
    prefix = station + " "
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.strip()
    return None


def parse_metar(metar):
    observed_at = datetime.now(timezone.utc).astimezone().isoformat()

    # Temperature group like 02/M01 or M05/M10
    temp_match = re.search(r"\b(M?\d{1,2})/(M?\d{1,2})\b", metar)
    temperature_f = 0
    if temp_match:
        temp_c = int(temp_match.group(1).replace("M", "-"))
        temperature_f = int(round(temp_c * 9.0 / 5.0 + 32.0))

    # Wind like 30012KT or VRB03KT (ignores gusts for now)
    wind_match = re.search(r"\b(\d{3}|VRB)(\d{2})KT\b", metar)
    wind_direction = "--"
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
