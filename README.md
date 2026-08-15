# Dumbarton Fishing Forecast

A minimalist React dashboard with a Python backend for fishing conditions near the Dumbarton Bridge.

The backend calls NOAA CO-OPS and NOAA/NWS endpoints, then calculates a 0-100 fishing score using tide movement, wind, water temperature, moon phase, and time of day. The frontend shows a mobile-first forecast interface inspired by the provided screenshots.

The Explore tab adds a scroll-feed of free learning resources for lake ecology, fishing, weather, environmental protection laws, NOAA programs, research articles, and documentary-style video collections.

The Alerts tab runs an AI-assisted geospatial scan over nearby NOAA/NWS forecast points to spot local weather anomalies such as bridge-area wind, temperature differences, precipitation changes, and active National Weather Service alerts.

## Run

```bash
python3 server.py
```

Open [http://127.0.0.1:8787](http://127.0.0.1:8787).

Use the in-app browser with the `http://127.0.0.1:8787` URL. Opening `static/index.html` directly as a `file://` page will not work because the React app needs the Python backend APIs.

## NOAA Data Sources

- CO-OPS tide predictions: station `9414509`, Dumbarton Bridge
- NOAA/NWS hourly weather forecast: `37.5067,-122.115`
- CO-OPS latest water temperature and wind observations, using Dumbarton Bridge first and San Francisco as fallback when a product is unavailable locally

The app reports `NOAA live` when all major requests succeed and `NOAA partial` when one of the upstream APIs is unavailable.
