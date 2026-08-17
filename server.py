from __future__ import annotations

import datetime as dt
import json
import math
import os
import pathlib
import statistics
import time
import urllib.parse
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


ROOT = pathlib.Path(__file__).resolve().parent
STATIC = ROOT / "static"
STATION_ID = "9414509"
STATION_NAME = "Dumbarton Bridge"
LAT = 37.5067
LON = -122.115
CACHE: dict[str, tuple[float, object]] = {}
USER_AGENT = "DumbartonFishingForecast/1.0 contact: local-demo@example.com"
COOPS_OBSERVATION_STATIONS = [
    {"id": STATION_ID, "name": STATION_NAME},
    {"id": "9414290", "name": "San Francisco"},
    {"id": "9414750", "name": "Alameda"},
    {"id": "9414863", "name": "Richmond"},
    {"id": "9414523", "name": "Redwood City"},
    {"id": "9414458", "name": "San Mateo Bridge"},
]
WEATHER_SCAN_POINTS = [
    {"name": "Dumbarton Bridge", "lat": LAT, "lon": LON},
    {"name": "Redwood City shore", "lat": 37.535, "lon": -122.224},
    {"name": "Fremont marsh", "lat": 37.515, "lon": -121.978},
    {"name": "Palo Alto Baylands", "lat": 37.459, "lon": -122.105},
    {"name": "Hayward shoreline", "lat": 37.621, "lon": -122.137},
]


def fetch_json(url: str, ttl: int = 600) -> dict:
    cached = CACHE.get(url)
    now = time.time()
    if cached and now - cached[0] < ttl:
        return cached[1]  # type: ignore[return-value]

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=12) as response:
        payload = json.loads(response.read().decode("utf-8"))
    CACHE[url] = (now, payload)
    return payload


def coops_url(**params: str) -> str:
    base = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    return base + "?" + urllib.parse.urlencode(params)


def get_tide_predictions(day: dt.date, interval: str) -> list[dict]:
    params = {
        "begin_date": day.strftime("%Y%m%d"),
        "end_date": day.strftime("%Y%m%d"),
        "station": STATION_ID,
        "product": "predictions",
        "datum": "MLLW",
        "time_zone": "lst_ldt",
        "units": "english",
        "format": "json",
        "interval": interval,
    }
    data = fetch_json(coops_url(**params), ttl=60 * 60)
    return data.get("predictions", [])


def get_latest_coops_product(product: str, station: str = STATION_ID) -> list[dict]:
    params = {
        "date": "latest",
        "station": station,
        "product": product,
        "time_zone": "lst_ldt",
        "units": "english",
        "format": "json",
    }
    data = fetch_json(coops_url(**params), ttl=15 * 60)
    return data.get("data", [])


def get_hourly_weather(day: dt.date) -> list[dict]:
    return get_hourly_weather_for(LAT, LON, day)


def get_hourly_weather_for(lat: float, lon: float, day: dt.date) -> list[dict]:
    point = fetch_json(f"https://api.weather.gov/points/{lat},{lon}", ttl=60 * 60 * 6)
    hourly_url = point["properties"]["forecastHourly"]
    forecast = fetch_json(hourly_url, ttl=20 * 60)
    periods = forecast["properties"]["periods"]
    wanted = day.isoformat()
    return [p for p in periods if p["startTime"][:10] == wanted]


def get_active_nws_alerts(lat: float, lon: float) -> list[dict]:
    data = fetch_json(f"https://api.weather.gov/alerts/active?point={lat},{lon}", ttl=10 * 60)
    alerts = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        alerts.append(
            {
                "event": props.get("event", "Weather alert"),
                "severity": props.get("severity", "Unknown"),
                "headline": props.get("headline") or props.get("description", "NOAA/NWS active alert"),
                "instruction": props.get("instruction") or "Check the latest National Weather Service guidance before heading out.",
                "area": props.get("areaDesc", "Nearby area"),
            }
        )
    return alerts


def parse_float(value: object) -> float | None:
    try:
        if value in (None, "", " "):
            return None
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def parse_prediction(item: dict) -> dict:
    stamp = dt.datetime.strptime(item["t"], "%Y-%m-%d %H:%M")
    return {"time": stamp.isoformat(), "hour": stamp.hour, "height": float(item["v"])}


def tide_direction(points: list[dict], index: int) -> str:
    if index <= 0:
        delta = points[min(1, len(points) - 1)]["height"] - points[0]["height"]
    else:
        delta = points[index]["height"] - points[index - 1]["height"]
    if delta > 0.04:
        return "incoming"
    if delta < -0.04:
        return "outgoing"
    return "slack"


def moon_phase(day: dt.date) -> dict:
    # Conway-style approximation, good enough for fishing guidance labels.
    known_new_moon = dt.date(2000, 1, 6)
    lunation = 29.53058867
    age = ((day - known_new_moon).days % lunation)
    illumination = (1 - math.cos(2 * math.pi * age / lunation)) / 2
    labels = [
        (1.8, "New moon"),
        (5.5, "Waxing crescent"),
        (9.2, "First quarter"),
        (12.9, "Waxing gibbous"),
        (16.6, "Full moon"),
        (20.3, "Waning gibbous"),
        (24.0, "Last quarter"),
        (27.7, "Waning crescent"),
        (30.0, "New moon"),
    ]
    label = next(text for limit, text in labels if age <= limit)
    return {"age": round(age, 1), "illumination": round(illumination * 100), "label": label}


def weather_at(hourly: list[dict], hour: int) -> dict:
    if not hourly:
        return {"wind": 12, "temperature": 62, "short": "Forecast unavailable"}
    closest = min(hourly, key=lambda p: abs(int(p["startTime"][11:13]) - hour))
    wind_text = closest.get("windSpeed", "0 mph").split(" to ")[-1]
    wind = parse_float("".join(ch for ch in wind_text if ch.isdigit() or ch == ".")) or 0
    return {
        "wind": wind,
        "temperature": closest.get("temperature"),
        "short": closest.get("shortForecast", "Marine forecast"),
        "direction": closest.get("windDirection", ""),
    }


def score_window(tide_points: list[dict], hourly: list[dict], water_temp: float | None, moon: dict) -> tuple[list[dict], dict]:
    windows = []
    for index, point in enumerate(tide_points):
        hour = int(point["time"][11:13])
        if hour < 5 or hour > 20:
            continue

        direction = tide_direction(tide_points, index)
        previous = tide_points[index - 1]["height"] if index else point["height"]
        movement = abs(point["height"] - previous)
        weather = weather_at(hourly, hour)
        wind = weather["wind"]

        tide_score = 30 if direction == "incoming" else 18 if direction == "outgoing" else 8
        movement_score = min(20, movement * 28)
        wind_score = max(0, 25 - max(0, wind - 7) * 2.2)
        temp_score = 12 if water_temp is None else max(0, 12 - abs(water_temp - 60) * 1.2)
        light_score = 8 if hour in range(6, 10) or hour in range(17, 20) else 4
        moon_score = 5 if moon["label"] in {"New moon", "Full moon"} else 3
        score = round(max(0, min(100, tide_score + movement_score + wind_score + temp_score + light_score + moon_score)))

        windows.append(
            {
                "hour": hour,
                "label": f"{hour % 12 or 12}:00 {'AM' if hour < 12 else 'PM'}",
                "score": score,
                "tide": direction,
                "movement": round(movement, 2),
                "wind": round(wind),
                "forecast": weather["short"],
            }
        )

    best = max(windows, key=lambda row: row["score"]) if windows else {"hour": 7, "score": 0, "tide": "unknown", "wind": 0}
    return windows, best


def format_window(best: dict) -> str:
    start = int(best["hour"])
    end = min(23, start + 3)
    def label(hour: int) -> str:
        return f"{hour % 12 or 12}:00 {'AM' if hour < 12 else 'PM'}"
    return f"{label(start)} - {label(end)}"


def species_insights(score: int, tide: str, water_temp: float | None, wind: float) -> list[dict]:
    temp = water_temp or 60
    striper_active = score >= 65 and tide in {"incoming", "outgoing"}
    halibut_active = score >= 58 and wind <= 14 and 55 <= temp <= 64
    sturgeon_active = tide == "outgoing" and wind <= 16
    return [
        {
            "name": "Striped bass",
            "activity": "High" if striper_active else "Moderate",
            "bait": "swimbaits, live anchovy, or cut bait along current edges",
            "note": "Moving water near bridge structure gives bass ambush lanes.",
        },
        {
            "name": "California halibut",
            "activity": "High" if halibut_active else "Low" if wind > 18 else "Moderate",
            "bait": "drift live bait or bounce soft plastics near sandy edges",
            "note": "Best when the drift is steady and the wind is not pushing too hard.",
        },
        {
            "name": "White sturgeon",
            "activity": "Moderate" if sturgeon_active else "Watch",
            "bait": "grass shrimp, ghost shrimp, or roe on the bottom",
            "note": "Outgoing tide can help scent travel, but avoid heavy wind chop.",
        },
    ]


def cause_entry(name: str, severity: str, evidence: str, fix: str) -> dict:
    return {"name": name, "severity": severity, "evidence": evidence, "fix": fix}


def water_temperature_signal(water_temp: float | None, station: dict | None = None) -> dict:
    if water_temp is None:
        return {
            "status": "Unavailable",
            "severity": "Low",
            "summary": "No nearby NOAA water-temperature observation is available right now.",
            "advice": "Use tide movement, wind, recent reports, and visible bait activity until a nearby sensor reports again.",
            "station": station,
        }

    station_name = station.get("name") if station else "nearby NOAA station"
    if water_temp < 50:
        status = "Cold water"
        severity = "High"
        summary = f"NOAA {station_name} reports {round(water_temp, 1)} degrees F, cold enough to slow many Bay predators."
        advice = "Fish slower, stay near deeper edges, and give bait more time near bottom or structure."
    elif water_temp < 55:
        status = "Cool water"
        severity = "Medium"
        summary = f"NOAA {station_name} reports {round(water_temp, 1)} degrees F, which can make the bite slower."
        advice = "Use slower retrieves and smaller adjustments before moving spots."
    elif water_temp <= 65:
        status = "Good bite range"
        severity = "Low"
        summary = f"NOAA {station_name} reports {round(water_temp, 1)} degrees F, a useful range for striped bass and halibut activity."
        advice = "Prioritize moving tide, bait presence, and clean current edges because temperature is not the main concern."
    elif water_temp <= 69:
        status = "Warm edge"
        severity = "Medium"
        summary = f"NOAA {station_name} reports {round(water_temp, 1)} degrees F, near the warm edge for a strong daytime bite."
        advice = "Fish earlier, deeper, or near stronger current where oxygen and bait movement are better."
    else:
        status = "Hot water stress"
        severity = "High"
        summary = f"NOAA {station_name} reports {round(water_temp, 1)} degrees F, warm enough to push fish toward cooler, oxygen-rich water."
        advice = "Avoid slow shallow water; look for deeper channels, shade, current, or low-light periods."

    return {"status": status, "severity": severity, "summary": summary, "advice": advice, "station": station}


def feeding_positioning_plan(best: dict, moon: dict, water_temp: float | None) -> dict:
    illumination = int(moon.get("illumination") or 0)
    waxing = "Waxing" in moon.get("label", "")
    if waxing and 20 <= illumination <= 75:
        moon_cue = (
            f"With {illumination}% {moon['label'].lower()} light, use the moon as a positioning clue: "
            "check slightly deeper water and depth transitions before leaving visible bait."
        )
    elif illumination <= 10:
        moon_cue = (
            f"With only {illumination}% moon illumination, very low light can reduce visual feeding efficiency. "
            "Work slower and keep the lure or bait in the strike zone longer."
        )
    else:
        moon_cue = (
            f"The moon is {moon['label'].lower()} at {illumination}% illumination. Treat it as a search clue, "
            "not a precise feeding clock."
        )

    temp_cue = "Temperature is not the main positioning clue right now."
    if water_temp is not None and water_temp > 65:
        temp_cue = "Warm water makes deeper, shaded, or stronger-current water more important because oxygen and comfort can improve there."
    elif water_temp is not None and water_temp < 55:
        temp_cue = "Cool water favors slower presentations near deeper edges, cover, and places where fish can ambush without chasing far."

    return {
        "title": "Where fish may be feeding when the surface looks quiet",
        "summary": (
            "No surface activity does not mean no feeding. Predators can sit below visible bait, on the outside edge, "
            "down-current or downwind, or along the first drop-off where prey has fewer escape options."
        ),
        "moonCue": moon_cue,
        "temperatureCue": temp_cue,
        "researchNote": (
            "Light and water clarity affect how deep visual predators can hunt. Largemouth bass studies also link lunar "
            "illumination with activity and depth distribution, but they do not support fake-precision solunar timing."
        ),
        "sequence": [
            {
                "trigger": "Visible bait but no strikes",
                "move": "Cast past the bait and retrieve through the outside edge first.",
                "why": "Predators often intercept weak or separated prey on the edge instead of sitting in the middle of the school.",
            },
            {
                "trigger": "Surface disturbance but no hookup",
                "move": "Probe 1-2 depth zones under the activity before moving.",
                "why": "Fish can feed vertically below bait without making obvious surface signs.",
            },
            {
                "trigger": "Shallow flat or grass line nearby",
                "move": "Work the closest transition: flat to drop-off, grass to clean edge, cover to open water.",
                "why": "Transitions give fish access to prey plus a quick escape route to deeper or safer water.",
            },
            {
                "trigger": "Wind or tide pushes bait one direction",
                "move": "Fish the down-current or downwind side of the bait and cover.",
                "why": "Disoriented prey often drifts that way, so predators can wait instead of chase.",
            },
            {
                "trigger": "The surface looks dead",
                "move": "Make one deliberate depth change before abandoning the spot.",
                "why": "A deeper or slower presentation can reveal fish that are feeding out of sight.",
            },
        ],
        "avoid": "Do not use the moon to claim fish will feed at an exact time. Use it to modify where and how deep you search.",
        "bestCurrentClue": f"Today's best modeled window has {best.get('tide', 'unknown')} tide movement near {best.get('movement', '--')} ft/hr.",
    }


def build_no_catch_diagnosis(
    windows: list[dict],
    best: dict,
    tides: list[dict],
    hourly: list[dict],
    water_temp: float | None,
    water_temp_station: dict | None,
    wind_observation: dict | None,
    moon: dict,
) -> dict:
    causes = []
    best_score = int(best.get("score") or 0)
    best_tide = best.get("tide", "unknown")
    best_wind = float(best.get("wind") or 0)
    best_movement = float(best.get("movement") or 0)
    fishable = [row for row in windows if 5 <= int(row.get("hour", 0)) <= 20]
    slow_windows = [row for row in fishable if float(row.get("movement") or 0) < 0.18 or row.get("tide") == "slack"]
    fast_windows = [row for row in fishable if float(row.get("movement") or 0) > 1.15]
    morning_evening = [row for row in fishable if int(row.get("hour", 0)) in range(6, 10) or int(row.get("hour", 0)) in range(17, 20)]
    precip_values = [
        parse_float((period.get("probabilityOfPrecipitation") or {}).get("value"))
        for period in hourly
    ]
    precip_values = [value for value in precip_values if value is not None]
    rain_chance = max(precip_values) if precip_values else 0
    poor_weather_words = {"Rain", "Showers", "Thunderstorms", "Fog", "Windy"}
    rough_periods = [
        period.get("shortForecast", "")
        for period in hourly
        if any(word.lower() in period.get("shortForecast", "").lower() for word in poor_weather_words)
    ]
    water_signal = water_temperature_signal(water_temp, water_temp_station)

    if best_score < 50:
        causes.append(
            cause_entry(
                "Low overall bite signal",
                "High" if best_score < 40 else "Medium",
                f"The best available window only scores {best_score}/100 using NOAA tide timing and NWS wind.",
                "Plan around the highest-scoring window, or treat the trip as scouting instead of a high-odds catch trip.",
            )
        )

    if best_tide == "slack" or (fishable and len(slow_windows) / len(fishable) >= 0.35):
        causes.append(
            cause_entry(
                "Weak or slack current",
                "High" if best_tide == "slack" else "Medium",
                f"The best window is {best_tide}, with about {round(best_movement, 2)} ft/hr tide movement.",
                "Fish the first half of the incoming or outgoing tide, and move baits along current seams, pilings, and depth changes.",
            )
        )

    if fast_windows and best_movement > 1.15:
        causes.append(
            cause_entry(
                "Presentation may be moving too fast",
                "Medium",
                f"NOAA tide predictions show up to {round(max(float(row.get('movement') or 0) for row in fast_windows), 2)} ft/hr movement during fishable hours.",
                "Use heavier sinkers, shorter drifts, or fish edges where current slows behind structure.",
            )
        )

    observed_gust = parse_float((wind_observation or {}).get("gust"))
    if best_wind >= 15 or (observed_gust is not None and observed_gust >= 22):
        wind_evidence = f"NWS forecast wind is about {round(best_wind)} mph in the best window"
        if observed_gust is not None:
            wind_evidence += f", and NOAA observed gusts are near {round(observed_gust)} mph"
        causes.append(
            cause_entry(
                "Wind and chop made fishing harder",
                "High" if best_wind >= 20 or (observed_gust is not None and observed_gust >= 28) else "Medium",
                f"{wind_evidence}.",
                "Pick protected shorelines, shorten casts, add weight, or wait for a calmer tide window.",
            )
        )

    if water_temp is not None and water_signal["severity"] in {"Medium", "High"}:
        causes.append(
            cause_entry(
                "Water temperature may be shaping the bite",
                water_signal["severity"],
                water_signal["summary"],
                water_signal["advice"],
            )
        )

    if morning_evening and best.get("hour") not in [row.get("hour") for row in morning_evening] and best_score < 65:
        causes.append(
            cause_entry(
                "Missed low-light feeding window",
                "Medium",
                f"The best modeled hour is {best.get('label', 'later in the day')}, while dawn and evening windows score lower today.",
                "If you fished midday, try the next dawn/evening tide overlap when fish are less light-shy.",
            )
        )

    if rain_chance >= 35 or rough_periods:
        causes.append(
            cause_entry(
                "Changing weather may have shifted fish behavior",
                "Medium" if rain_chance < 65 else "High",
                f"NWS hourly forecast shows up to {round(rain_chance)}% precipitation chance and {rough_periods[0] if rough_periods else 'unsettled weather'} nearby.",
                "Watch for fronts, pressure changes, muddy water, and reduced visibility; simplify bait choice and fish slower.",
            )
        )

    if best_score >= 65 and not causes:
        causes.append(
            cause_entry(
                "Technique or exact location mismatch",
                "Medium",
                f"Conditions look fishable: {best_tide} tide, {round(best_wind)} mph wind, {water_signal['status'].lower()}, and a {best_score}/100 score.",
                "Change one variable at a time: bait size, depth, casting angle, retrieve speed, or move to current edges with birds or baitfish.",
            )
        )

    if len(causes) < 3:
        causes.append(
            cause_entry(
                "Fish may be feeding outside the visible spot",
                "Low",
                f"The moon is {moon['label'].lower()} with {moon['illumination']}% illumination, which is better used as a positioning clue than a feeding clock.",
                "Work the outside edge of visible bait, then probe deeper and fish the nearest drop-off, cover edge, or current break before relocating.",
            )
        )

    severity_points = {"High": 28, "Medium": 18, "Low": 8}
    risk = max(5, min(100, 100 - best_score + sum(severity_points.get(item["severity"], 8) for item in causes[:3]) // 2))
    top = max(causes, key=lambda item: severity_points.get(item["severity"], 0))
    status = "High no-catch risk" if risk >= 70 else "Moderate no-catch risk" if risk >= 45 else "Low no-catch risk"
    summary = (
        f"The most likely blank-trip clue is {top['name'].lower()}. "
        f"This is based on NOAA tide movement, NWS hourly weather, observed water/wind data when available, and the moon phase."
    )
    return {
        "risk": round(risk),
        "status": status,
        "topCause": top["name"],
        "summary": summary,
        "causes": causes[:5],
        "waterTemperature": water_signal,
        "positioning": feeding_positioning_plan(best, moon, water_temp),
        "dataUsed": [
            "NOAA CO-OPS tide movement and tide direction",
            "NOAA/NWS hourly wind and weather forecast",
            "NOAA observed water temperature and wind when available",
            "Moon phase approximation for light and feeding timing",
        ],
    }


def summarize_scan_period(periods: list[dict]) -> dict:
    if not periods:
        return {"wind": None, "temp": None, "precip": 0, "short": "Forecast unavailable", "hour": None}
    first_six = periods[:6] or periods
    winds = [weather_at([p], int(p["startTime"][11:13]))["wind"] for p in first_six]
    temps = [p.get("temperature") for p in first_six if isinstance(p.get("temperature"), (int, float))]
    precip = [
        parse_float((p.get("probabilityOfPrecipitation") or {}).get("value"))
        for p in first_six
    ]
    precip_values = [value for value in precip if value is not None]
    dominant = max(
        {p.get("shortForecast", "Forecast unavailable") for p in first_six},
        key=lambda label: sum(1 for p in first_six if p.get("shortForecast", "Forecast unavailable") == label),
    )
    return {
        "wind": round(max(winds), 1) if winds else None,
        "temp": round(statistics.mean(temps), 1) if temps else None,
        "precip": round(max(precip_values), 1) if precip_values else 0,
        "short": dominant,
        "hour": int(first_six[0]["startTime"][11:13]) if first_six else None,
    }


def severity_for(kind: str, value: float) -> str:
    if kind == "wind":
        if value >= 25:
            return "High"
        if value >= 18:
            return "Moderate"
    if kind == "precip":
        if value >= 65:
            return "High"
        if value >= 35:
            return "Moderate"
    if kind == "temp":
        if value >= 10:
            return "Moderate"
    return "Low"


def build_weather_anomalies(day: dt.date) -> dict:
    points = []
    errors = []
    for point in WEATHER_SCAN_POINTS:
        try:
            periods = get_hourly_weather_for(point["lat"], point["lon"], day)
            summary = summarize_scan_period(periods)
            points.append({**point, **summary})
        except Exception as exc:
            errors.append(f"{point['name']} forecast unavailable: {exc}")

    active_alerts = []
    try:
        active_alerts = get_active_nws_alerts(LAT, LON)
    except Exception as exc:
        errors.append(f"NWS active alerts unavailable: {exc}")

    usable = [p for p in points if p.get("wind") is not None]
    anomalies = []
    if usable:
        bridge = next((p for p in usable if p["name"] == "Dumbarton Bridge"), usable[0])
        nearby = [p for p in usable if p["name"] != bridge["name"]] or usable
        wind_values = [p["wind"] for p in nearby if p.get("wind") is not None]
        temp_values = [p["temp"] for p in nearby if p.get("temp") is not None]
        precip_values = [p["precip"] for p in nearby if p.get("precip") is not None]
        avg_wind = statistics.mean(wind_values) if wind_values else bridge.get("wind") or 0
        avg_temp = statistics.mean(temp_values) if temp_values and bridge.get("temp") is not None else bridge.get("temp") or 0
        avg_precip = statistics.mean(precip_values) if precip_values else 0

        wind_delta = (bridge.get("wind") or 0) - avg_wind
        if (bridge.get("wind") or 0) >= 18 or wind_delta >= 7:
            severity = severity_for("wind", bridge.get("wind") or 0)
            anomalies.append(
                {
                    "kind": "Wind",
                    "severity": severity,
                    "title": "Wind stands out near the bridge",
                    "message": f"NOAA/NWS forecast shows about {round(bridge.get('wind') or 0)} mph wind near Dumbarton, {round(abs(wind_delta), 1)} mph {'above' if wind_delta >= 0 else 'below'} the nearby scan average.",
                    "advice": "Use extra caution from shore and avoid small craft if gusts rise or whitecaps appear.",
                    "lat": bridge["lat"],
                    "lon": bridge["lon"],
                }
            )

        precip_delta = (bridge.get("precip") or 0) - avg_precip
        if (bridge.get("precip") or 0) >= 35 or precip_delta >= 25:
            severity = severity_for("precip", bridge.get("precip") or 0)
            anomalies.append(
                {
                    "kind": "Rain",
                    "severity": severity,
                    "title": "Rain chance is elevated nearby",
                    "message": f"The bridge scan shows a {round(bridge.get('precip') or 0)}% precipitation chance, compared with a nearby average near {round(avg_precip)}%.",
                    "advice": "Bring rain gear, watch road visibility, and pause fishing if thunder develops.",
                    "lat": bridge["lat"],
                    "lon": bridge["lon"],
                }
            )

        if bridge.get("temp") is not None:
            temp_delta = abs((bridge.get("temp") or 0) - avg_temp)
            if temp_delta >= 8:
                severity = severity_for("temp", temp_delta)
                anomalies.append(
                    {
                        "kind": "Temperature",
                        "severity": severity,
                        "title": "Temperature differs from nearby shorelines",
                        "message": f"Dumbarton is about {round(temp_delta, 1)} degrees F away from the nearby forecast average.",
                        "advice": "Layer clothing and expect comfort to change quickly near open water.",
                        "lat": bridge["lat"],
                        "lon": bridge["lon"],
                    }
                )

        condition_counts: dict[str, int] = {}
        for p in nearby:
            condition_counts[p.get("short") or "Forecast unavailable"] = condition_counts.get(p.get("short") or "Forecast unavailable", 0) + 1
        common_condition = max(condition_counts, key=condition_counts.get) if condition_counts else bridge.get("short")
        if bridge.get("short") != common_condition and bridge.get("short") not in {"Forecast unavailable", None}:
            anomalies.append(
                {
                    "kind": "Microclimate",
                    "severity": "Low",
                    "title": "Bridge forecast differs from nearby points",
                    "message": f"Dumbarton shows '{bridge.get('short')}', while nearby points most often show '{common_condition}'.",
                    "advice": "Check the sky before committing to a long session; Bay edges can shift quickly.",
                    "lat": bridge["lat"],
                    "lon": bridge["lon"],
                }
            )

    for alert in active_alerts:
        anomalies.insert(
            0,
            {
                "kind": "NWS alert",
                "severity": alert["severity"],
                "title": alert["event"],
                "message": alert["headline"],
                "advice": alert["instruction"],
                "lat": LAT,
                "lon": LON,
                "area": alert["area"],
            },
        )

    if not anomalies:
        anomalies.append(
            {
                "kind": "Normal",
                "severity": "Low",
                "title": "No local weather anomaly detected",
                "message": "The NOAA/NWS scan does not show a major wind, rain, or temperature outlier around Dumbarton Bridge right now.",
                "advice": "Still check visible conditions before fishing because Bay weather can change quickly.",
                "lat": LAT,
                "lon": LON,
            }
        )

    high_count = sum(1 for item in anomalies if item.get("severity") in {"High", "Extreme", "Severe"})
    moderate_count = sum(1 for item in anomalies if item.get("severity") == "Moderate")
    status = "Watch" if high_count else "Caution" if moderate_count else "Clear"

    return {
        "date": day.isoformat(),
        "updated": dt.datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "summary": "AI-assisted geospatial scan using NOAA/NWS forecast points around Dumbarton Bridge.",
        "center": {"name": STATION_NAME, "lat": LAT, "lon": LON},
        "points": points,
        "anomalies": anomalies[:6],
        "errors": errors,
        "sources": [
            "NOAA/National Weather Service hourly forecast grid",
            "NOAA/National Weather Service active weather alerts",
            "Local geospatial comparison around Dumbarton Bridge",
        ],
    }


def build_forecast(day: dt.date) -> dict:
    errors = []
    tides = []
    extremes = []
    hourly = []
    water_temp = None
    water_temp_station = None
    wind_observation = None

    try:
        tides = [parse_prediction(item) for item in get_tide_predictions(day, "h")]
        extremes = get_tide_predictions(day, "hilo")
    except Exception as exc:
        errors.append(f"Tide predictions unavailable: {exc}")

    try:
        hourly = get_hourly_weather(day)
    except Exception as exc:
        errors.append(f"Hourly weather unavailable: {exc}")

    for station in COOPS_OBSERVATION_STATIONS:
        try:
            values = get_latest_coops_product("water_temperature", station["id"])
            water_temp = parse_float(values[0].get("v")) if values else None
            if water_temp is not None:
                water_temp_station = station
                break
        except Exception:
            continue

    for station in COOPS_OBSERVATION_STATIONS:
        try:
            values = get_latest_coops_product("wind", station["id"])
            if values:
                wind_observation = {
                    "speed": parse_float(values[0].get("s")),
                    "gust": parse_float(values[0].get("g")),
                    "station": station,
                }
                break
        except Exception:
            continue

    if not tides:
        tides = [{"time": dt.datetime.combine(day, dt.time(hour=h)).isoformat(), "hour": h, "height": 3 + math.sin(h / 24 * math.tau)} for h in range(24)]

    moon = moon_phase(day)
    windows, best = score_window(tides, hourly, water_temp, moon)
    water_signal = water_temperature_signal(water_temp, water_temp_station)
    no_catch = build_no_catch_diagnosis(windows, best, tides, hourly, water_temp, water_temp_station, wind_observation, moon)
    score = best.get("score", 0)
    wind = best.get("wind", 0)
    alerts = []
    if wind >= 18:
        alerts.append("Strong afternoon wind may make the bridge area uncomfortable and less safe.")
    if wind_observation and wind_observation.get("gust") and wind_observation["gust"] >= 25:
        alerts.append("NOAA observed gusts are elevated; check conditions before launching.")
    if best.get("tide") == "slack":
        alerts.append("Slack tide means weaker current and less bait movement.")

    reasons = [
        f"The top window lines up with an {best.get('tide', 'unknown')} tide and about {best.get('wind', 0)} mph wind.",
        "Moving tide is weighted heavily because it concentrates bait near bridge structure.",
        f"The moon is {moon['label'].lower()} with {moon['illumination']}% illumination.",
    ]
    if water_temp:
        station_label = water_temp_station.get("name", "nearby station") if water_temp_station else "nearby station"
        reasons.append(f"NOAA {station_label} water temperature is {round(water_temp, 1)} degrees F: {water_signal['status'].lower()}.")
    else:
        reasons.append("Nearby NOAA water temperature is unavailable right now, so the app does not treat water temperature as a no-catch cause.")

    if water_temp is None:
        errors.append("Nearby NOAA water temperature observation unavailable.")

    return {
        "station": {"id": STATION_ID, "name": STATION_NAME, "lat": LAT, "lon": LON},
        "date": day.isoformat(),
        "updated": dt.datetime.now().isoformat(timespec="seconds"),
        "score": score,
        "status": "Great" if score >= 75 else "Good" if score >= 60 else "Fair" if score >= 42 else "Poor",
        "bestWindow": format_window(best),
        "best": best,
        "reasons": reasons,
        "alerts": alerts or ["No major NOAA-based safety flags for the best window."],
        "tides": tides,
        "extremes": extremes,
        "weather": [
            {
                "time": p["startTime"],
                "hour": int(p["startTime"][11:13]),
                "temp": p.get("temperature"),
                "wind": weather_at([p], int(p["startTime"][11:13]))["wind"],
                "short": p.get("shortForecast", ""),
            }
            for p in hourly
        ],
        "waterTemp": water_temp,
        "waterTempStation": water_temp_station,
        "waterTempSignal": water_signal,
        "windObservation": wind_observation,
        "moon": moon,
        "windows": windows,
        "species": species_insights(score, best.get("tide", ""), water_temp, wind),
        "noCatch": no_catch,
        "dataStatus": "live" if not errors else "partial",
        "errors": errors,
        "sources": [
            "NOAA CO-OPS tide predictions station 9414509",
            "NOAA/NWS hourly forecast API for Dumbarton Bridge coordinates",
            "NOAA CO-OPS observed water temperature and wind when available",
            "No-catch diagnosis uses NOAA tide movement, NWS weather, observed water/wind data, and moon phase timing",
        ],
    }


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/forecast":
            query = urllib.parse.parse_qs(parsed.query)
            selected = query.get("date", [dt.date.today().isoformat()])[0]
            try:
                day = dt.date.fromisoformat(selected)
            except ValueError:
                day = dt.date.today()
            payload = build_forecast(day)
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/api/anomalies":
            query = urllib.parse.parse_qs(parsed.query)
            selected = query.get("date", [dt.date.today().isoformat()])[0]
            try:
                day = dt.date.fromisoformat(selected)
            except ValueError:
                day = dt.date.today()
            payload = build_weather_anomalies(day)
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/":
            self.path = "/index.html"
        return super().do_GET()


def main() -> None:
    port = int(os.environ.get("PORT", "8787"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Dumbarton fishing forecast running at http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
