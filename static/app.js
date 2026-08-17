const { useEffect, useMemo, useState } = React;
const h = React.createElement;

const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const today = new Date();
const feedFilters = ["All", "Lakes", "Fishing", "Weather", "Ecology", "Laws", "NOAA"];
const speciesOptions = ["Striped bass", "California halibut", "White sturgeon"];
const interestOptions = ["Fishing", "Weather", "Ecology", "Lakes", "Laws", "NOAA"];
const defaultSettings = {
  displayName: "Angler",
  spotName: "Dumbarton Bridge",
  experience: "Beginner",
  units: "US customary",
  alertSensitivity: "Normal",
  preferredSpecies: ["Striped bass", "California halibut"],
  learningInterests: ["Fishing", "Weather", "NOAA"],
};
const exploreFeed = [
  {
    title: "Lake ecology field notes",
    tag: "Lakes",
    tone: "blue",
    size: "tall",
    type: "AI guide",
    image: "https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=900&q=82",
    credit: "Lake photo",
    url: "https://www.epa.gov/wetlands/what-wetland",
    source: "EPA Wetlands",
    summary: "Learn how shallow edges, wetlands, vegetation, and seasonal water levels shape fish habitat.",
  },
  {
    title: "Watch sanctuary science live",
    tag: "NOAA",
    tone: "green",
    size: "wide",
    type: "Live video",
    image: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=82",
    credit: "Ocean photo",
    url: "https://sanctuaries.noaa.gov/live/",
    source: "NOAA Sanctuaries Live",
    summary: "Follow NOAA expeditions, ocean research, livestreams, and scientist chats from protected waters.",
  },
  {
    title: "Why tides change the bite",
    tag: "Fishing",
    tone: "yellow",
    size: "short",
    type: "Quick read",
    image: "https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=900&q=82",
    credit: "Water movement photo",
    url: "https://oceanservice.noaa.gov/education/tutorial_tides/",
    source: "NOAA Ocean Service",
    summary: "Tides move bait, oxygen, scent, and fish. Use this primer before reading the forecast score.",
  },
  {
    title: "Clean Water Act basics",
    tag: "Laws",
    tone: "pink",
    size: "short",
    type: "Law brief",
    image: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=900&q=82",
    credit: "Wetland photo",
    url: "https://www.epa.gov/laws-regulations/summary-clean-water-act",
    source: "EPA",
    summary: "The main U.S. law for pollutant discharge limits and surface-water quality standards.",
  },
  {
    title: "Changing ocean video shelf",
    tag: "Weather",
    tone: "violet",
    size: "tall",
    type: "Documentaries",
    image: "https://images.unsplash.com/photo-1471922694854-ff1b63b20054?auto=format&fit=crop&w=900&q=82",
    credit: "Marine weather photo",
    url: "https://sanctuaries.noaa.gov/education/teachers/changing-ocean/videos.html",
    source: "NOAA Video Collection",
    summary: "Short films on warming waters, storms, acidification, coral bleaching, and ecosystem resilience.",
  },
  {
    title: "Free sanctuary lessons",
    tag: "Ecology",
    tone: "clay",
    size: "wide",
    type: "Lesson library",
    image: "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1200&q=82",
    credit: "Underwater photo",
    url: "https://sanctuaries.noaa.gov/education/teachers/resource-collections.html",
    source: "NOAA Education",
    summary: "Videos, lesson plans, posters, webinars, web stories, virtual reality, and research explainers.",
  },
  {
    title: "Responsible angler checklist",
    tag: "Fishing",
    tone: "green",
    size: "short",
    type: "AI checklist",
    image: "https://images.unsplash.com/photo-1517677208171-0bc6725a3e60?auto=format&fit=crop&w=900&q=82",
    credit: "Fishing photo",
    url: "https://www.fisheries.noaa.gov/topic/sustainable-fisheries",
    source: "NOAA Fisheries",
    summary: "Check regulations, avoid sensitive habitat, pack out line, and handle fish gently before release.",
  },
  {
    title: "Ocean for Life films",
    tag: "NOAA",
    tone: "blue",
    size: "tall",
    type: "Free videos",
    image: "https://images.unsplash.com/photo-1524704796725-9fc3044a58b2?auto=format&fit=crop&w=900&q=82",
    credit: "Fish photo",
    url: "https://sanctuaries.noaa.gov/education/ofl/videos.html",
    source: "NOAA Ocean for Life",
    summary: "Student-made films about ocean stewardship, sense of place, conservation, and cultural connection.",
  },
  {
    title: "Watershed protection law map",
    tag: "Laws",
    tone: "yellow",
    size: "wide",
    type: "Research path",
    image: "https://images.unsplash.com/photo-1437482078695-73f5ca6c96e2?auto=format&fit=crop&w=1200&q=82",
    credit: "Watershed photo",
    url: "https://www.epa.gov/enforcement/clean-water-act-cwa-and-federal-facilities",
    source: "EPA Enforcement",
    summary: "See how permits, dredge-and-fill rules, wetlands, and enforcement connect back to fishable water.",
  },
  {
    title: "Harmful algal blooms in lakes",
    tag: "Lakes",
    tone: "pink",
    size: "short",
    type: "EPA webcast",
    image: "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=900&q=82",
    credit: "Lake water photo",
    url: "https://www.epa.gov/watershedacademy/nitrogen-and-phosphorus-pollution-and-harmful-algal-blooms-lakes",
    source: "EPA Watershed Academy",
    summary: "Understand how nitrogen and phosphorus pollution can feed harmful algal blooms that affect fishing and swimming.",
  },
  {
    title: "NOAA fish habitat restoration",
    tag: "Ecology",
    tone: "green",
    size: "wide",
    type: "Habitat story",
    image: "https://images.unsplash.com/photo-1468581264429-2548ef9eb732?auto=format&fit=crop&w=1200&q=82",
    credit: "Restoration photo",
    url: "https://www.fisheries.noaa.gov/feature-story/restoring-habitat-and-engaging-recreational-community-through-national-fish-habitat",
    source: "NOAA Fisheries",
    summary: "See how NOAA-supported habitat work involves anglers and local communities in restoring fish habitat.",
  },
  {
    title: "Green sturgeon science",
    tag: "Fishing",
    tone: "blue",
    size: "short",
    type: "Species science",
    image: "https://images.unsplash.com/photo-1524704654690-b56c05c78a00?auto=format&fit=crop&w=900&q=82",
    credit: "Fish photo",
    url: "https://www.fisheries.noaa.gov/species/green-sturgeon/science",
    source: "NOAA Fisheries",
    summary: "Learn why sturgeon need careful handling and how fisheries science studies catch-and-release impacts.",
  },
  {
    title: "Rip current basics",
    tag: "Weather",
    tone: "yellow",
    size: "short",
    type: "Safety guide",
    image: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=900&q=82",
    credit: "Surf photo",
    url: "https://oceanservice.noaa.gov/facts/ripcurrent.html",
    source: "NOAA Ocean Service",
    summary: "A simple NOAA explainer on rip currents, why they differ from rip tides, and what to do if caught.",
  },
  {
    title: "NOAA fisheries science data",
    tag: "NOAA",
    tone: "violet",
    size: "wide",
    type: "Research hub",
    image: "https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=1200&q=82",
    credit: "Ocean data photo",
    url: "https://www.fisheries.noaa.gov/science-and-data",
    source: "NOAA Fisheries",
    summary: "Explore NOAA science behind sustainable fisheries, protected species, habitats, and ocean stewardship.",
  },
  {
    title: "Atlantic striped bass profile",
    tag: "Fishing",
    tone: "clay",
    size: "short",
    type: "Species profile",
    image: "https://images.unsplash.com/photo-1574781330855-d0db8cc6a79c?auto=format&fit=crop&w=900&q=82",
    credit: "Striped fish photo",
    url: "https://www.fisheries.noaa.gov/species/atlantic-striped-bass",
    source: "NOAA Fisheries",
    summary: "Use NOAA’s profile to learn about striped bass management, harvest rules, and sustainability context.",
  },
];

function loadSettings() {
  try {
    return { ...defaultSettings, ...(JSON.parse(localStorage.getItem("dumbartonFishingSettings") || "{}")) };
  } catch {
    return defaultSettings;
  }
}

function saveSettings(settings) {
  localStorage.setItem("dumbartonFishingSettings", JSON.stringify(settings));
}

function isoDate(date) {
  return date.toISOString().slice(0, 10);
}

function weekDays() {
  return Array.from({ length: 7 }, (_, index) => {
    const date = new Date(today);
    date.setDate(today.getDate() - today.getDay() + index);
    return date;
  });
}

function Icon({ name }) {
  const paths = {
    home: "M3 11.5 12 4l9 7.5V21a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z",
    compass: "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20Zm3.2-13.2-1.8 5.4-5.4 1.8 1.8-5.4 5.4-1.8Z",
    plus: "M12 5v14M5 12h14",
    bell: "M18 8a6 6 0 1 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9ZM10 21h4",
    user: "M20 21a8 8 0 0 0-16 0M12 13a5 5 0 1 0 0-10 5 5 0 0 0 0 10Z",
    fish: "M3 12s4-6 10-6c4 0 7 3 8 6-1 3-4 6-8 6-6 0-10-6-10-6Zm16 0 3-3v6l-3-3ZM8.5 10.5h.1",
    wind: "M3 8h11a3 3 0 1 0-3-3M3 13h16a3 3 0 1 1-3 3M3 18h8",
  };
  return h("svg", { viewBox: "0 0 24 24", "aria-hidden": "true" }, h("path", { d: paths[name] }));
}

function TideChart({ data }) {
  const points = useMemo(() => {
    if (!data || !data.length) return "";
    const min = Math.min(...data.map((d) => d.height));
    const max = Math.max(...data.map((d) => d.height));
    return data
      .map((d, i) => {
        const x = 18 + (i / Math.max(1, data.length - 1)) * 264;
        const y = 112 - ((d.height - min) / Math.max(0.1, max - min)) * 82;
        return `${x},${y}`;
      })
      .join(" ");
  }, [data]);

  return h(
    "div",
    { className: "chart tide-card" },
    h("div", { className: "chart-head" }, h("span", null, "Tide curve"), h("strong", null, "MLLW ft")),
    h(
      "svg",
      { viewBox: "0 0 300 132", role: "img", "aria-label": "NOAA tide prediction chart" },
      h("path", { className: "grid-line", d: "M18 32H282M18 72H282M18 112H282" }),
      h("polyline", { points, className: "tide-line" }),
      ...(data || [])
        .filter((_, i) => i % 6 === 0)
        .map((d, i) => h("text", { key: d.time, x: 18 + i * 72, y: "126" }, `${d.hour}:00`))
    )
  );
}

function WeatherChart({ data }) {
  const bars = (data || []).slice(0, 12);
  return h(
    "div",
    { className: "chart weather-card" },
    h("div", { className: "chart-head" }, h("span", null, "Wind + weather"), h("strong", null, "mph")),
    h(
      "div",
      { className: "bar-chart" },
      ...bars.map((item) =>
        h(
          "div",
          { className: "bar-wrap", key: item.time },
          h("div", { className: "bar", style: { height: `${Math.max(16, item.wind * 4)}px` } }),
          h("small", null, item.hour)
        )
      )
    )
  );
}

function ScoreRing({ score }) {
  const degrees = Math.round((score / 100) * 360);
  return h(
    "div",
    { className: "score-ring", style: { background: `conic-gradient(#111 ${degrees}deg, #f6d6ce 0deg)` } },
    h("div", null, h("strong", null, score), h("span", null, "/100"))
  );
}

function HomePage({ selected, setSelected, forecast, loading, settings }) {
  const days = weekDays();
  const score = forecast ? forecast.score : 0;
  const species = ((forecast && forecast.species) || []).slice().sort((a, b) => {
    const aPreferred = settings.preferredSpecies.includes(a.name) ? 0 : 1;
    const bPreferred = settings.preferredSpecies.includes(b.name) ? 0 : 1;
    return aPreferred - bPreferred;
  });
  const noCatch = forecast && forecast.noCatch;

  return [
    h(
      "section",
      { className: "topbar", key: "home-top" },
      h("div", null, h("p", { className: "eyebrow" }, settings.spotName || "Dumbarton Bridge"), h("h1", null, "Fishing today")),
      h("div", { className: "avatar" }, h(Icon, { name: "fish" }))
    ),
    h(
      "section",
      { className: "date-strip", "aria-label": "Choose forecast day", key: "home-days" },
      ...days.map((date) => {
        const active = isoDate(date) === selected;
        return h(
          "button",
          { className: active ? "active" : "", key: date.toISOString(), onClick: () => setSelected(isoDate(date)) },
          h("span", null, dayNames[date.getDay()]),
          h("strong", null, date.getDate())
        );
      })
    ),
    h(
      "section",
      { className: "hero-panel", key: "home-hero" },
      h(
        "div",
        { className: "hero-copy" },
        h("p", { className: "eyebrow" }, "Fishing score"),
        h("h2", null, loading ? "Checking NOAA..." : `${forecast.status} day`),
        h("p", null, forecast ? `Best window: ${forecast.bestWindow}` : "Finding tide and weather timing.")
      ),
      h(ScoreRing, { score }),
      h("div", { className: "fish-scene", "aria-hidden": "true" })
    ),
    h(
      "section",
      { className: "section-head", key: "home-why-title" },
      h("h2", null, "Why it matters"),
      h("span", null, forecast && forecast.dataStatus === "live" ? "NOAA live" : "NOAA partial")
    ),
    h(
      "section",
      { className: "reason-row", key: "home-reasons" },
      ...(forecast ? forecast.reasons : ["Loading tide, wind, water temperature, and moon data."]).map((reason, index) =>
        h("article", { className: "reason-card", key: reason }, h("strong", null, index + 1), h("p", null, reason))
      )
    ),
    h("section", { className: "charts-grid", key: "home-charts" }, h(TideChart, { data: (forecast && forecast.tides) || [] }), h(WeatherChart, { data: (forecast && forecast.weather) || [] })),
    h(
      "section",
      { className: "metrics", key: "home-metrics" },
      h("article", null, h("span", null, "Water"), h("strong", null, forecast && forecast.waterTemp ? `${Math.round(forecast.waterTemp)} F` : "--")),
      h("article", null, h("span", null, "Current"), h("strong", null, forecast && forecast.best && forecast.best.movement ? `${forecast.best.movement} ft/hr` : "--")),
      h("article", null, h("span", null, "Moon"), h("strong", null, `${(forecast && forecast.moon && forecast.moon.illumination) || "--"}%`)),
      h("article", null, h("span", null, "Top tide"), h("strong", null, (forecast && forecast.best && forecast.best.tide) || "--"))
    ),
    h(
      "section",
      { className: "no-catch-panel", key: "home-no-catch" },
      h("div", { className: "section-head compact" }, h("h2", null, "No-catch clues"), h("span", null, "real data")),
      h(
        "div",
        { className: "no-catch-summary" },
        h("div", null, h("span", null, "Blank-trip risk"), h("strong", null, noCatch ? `${noCatch.risk}/100` : "--")),
        h("p", null, noCatch ? noCatch.status : "Checking tide, wind, water, weather, and moon signals.")
      ),
      h("h3", null, noCatch ? noCatch.topCause : "Finding likely cause"),
      h("p", null, noCatch ? noCatch.summary : "The app will explain why a no-catch day may happen once NOAA data loads."),
      h(
        "div",
        { className: "cause-list" },
        ...((noCatch && noCatch.causes) || []).slice(0, 3).map((cause) =>
          h(
            "article",
            { key: cause.name },
            h("span", { className: `severity ${cause.severity.toLowerCase()}` }, cause.severity),
            h("strong", null, cause.name),
            h("p", null, cause.evidence),
            h("small", null, cause.fix)
          )
        )
      )
    ),
    h("section", { className: "section-head", key: "home-species-title" }, h("h2", null, "Species"), h("span", null, "preferred first")),
    h(
      "section",
      { className: "species-list", key: "home-species" },
      ...species.map((fish) =>
        h(
          "article",
          { className: settings.preferredSpecies.includes(fish.name) ? "preferred" : "", key: fish.name },
          h("div", null, h("h3", null, fish.name), h("p", null, fish.note), h("small", null, fish.bait)),
          h("span", null, settings.preferredSpecies.includes(fish.name) ? `Preferred - ${fish.activity}` : fish.activity)
        )
      )
    ),
    h(
      "section",
      { className: "alerts", key: "home-alerts" },
      h("div", { className: "section-head compact" }, h("h2", null, "Safety"), h("span", null, "NOAA flags")),
      ...((forecast && forecast.alerts) || ["Loading alerts."]).map((alert) => h("p", { key: alert }, alert))
    )
  ];
}

function ExploreCard({ item }) {
  return h(
    "a",
    { className: `explore-card ${item.tone} ${item.size}`, href: item.url, target: "_blank", rel: "noreferrer" },
    h("img", { className: "feed-photo", src: item.image, alt: `${item.title} photo`, loading: "lazy" }),
    h("div", { className: "feed-meta" }, h("span", null, item.type), h("strong", null, item.tag)),
    h("h3", null, item.title),
    h("p", null, item.summary),
    h("small", null, `${item.source} - ${item.credit}`)
  );
}

function ExplorePage({ settings }) {
  const [filter, setFilter] = useState(settings.learningInterests[0] || "All");
  const filtered = filter === "All" ? exploreFeed : exploreFeed.filter((item) => item.tag === filter);

  return [
    h(
      "section",
      { className: "topbar explore-top", key: "explore-top" },
      h("div", null, h("p", { className: "eyebrow" }, "Explore"), h("h1", null, "Nature feed")),
      h("div", { className: "avatar" }, h(Icon, { name: "compass" }))
    ),
    h(
      "section",
      { className: "explore-search", key: "explore-search" },
      h("span", null, `${filtered.length} resources for ${filter}`),
      h("button", { onClick: () => setFilter(settings.learningInterests[0] || "NOAA") }, "My topics")
    ),
    h(
      "section",
      { className: "explore-hero", key: "explore-hero" },
      h("div", null, h("p", { className: "eyebrow" }, "For curious anglers"), h("h2", null, "Know the water before you fish"), h("p", null, "Scroll research, videos, laws, lake ecology, weather science, and protection programs in one gentle feed.")),
      h("div", { className: "hero-badge" }, h("strong", null, "42"), h("span", null, "free paths"))
    ),
    h(
      "section",
      { className: "filter-strip", "aria-label": "Explore filters", key: "explore-filters" },
      ...feedFilters.map((name) => h("button", { className: filter === name ? "active" : "", key: name, onClick: () => setFilter(name) }, name))
    ),
    h(
      "section",
      { className: "insight-row", key: "explore-insights" },
      h("article", null, h("strong", null, "Lake care"), h("p", null, "Watch shorelines, runoff, algae, and wetland buffers.")),
      h("article", null, h("strong", null, "Fish sense"), h("p", null, "Connect bite windows to habitat, oxygen, and weather.")),
      h("article", null, h("strong", null, "Stewardship"), h("p", null, "Read laws and programs that protect public waters."))
    ),
    h(
      "section",
      { className: "feed-grid", key: "explore-feed" },
      ...filtered.map((item) => h(ExploreCard, { item, key: item.title }))
    )
  ];
}

function severityClass(severity) {
  const text = (severity || "").toLowerCase();
  if (text.includes("high") || text.includes("severe") || text.includes("extreme")) return "high";
  if (text.includes("moderate") || text.includes("watch")) return "moderate";
  return "low";
}

function AlertMap({ points = [], center }) {
  const all = points.length ? points : [center].filter(Boolean);
  const lats = all.map((p) => p.lat);
  const lons = all.map((p) => p.lon);
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const minLon = Math.min(...lons);
  const maxLon = Math.max(...lons);
  const plot = (point) => {
    const x = 22 + ((point.lon - minLon) / Math.max(0.001, maxLon - minLon)) * 256;
    const y = 150 - ((point.lat - minLat) / Math.max(0.001, maxLat - minLat)) * 112;
    return { x, y };
  };

  return h(
    "div",
    { className: "alert-map" },
    h("div", { className: "map-head" }, h("strong", null, "Nearby scan map"), h("span", null, "NOAA/NWS grid")),
    h(
      "svg",
      { viewBox: "0 0 300 172", role: "img", "aria-label": "Geospatial weather anomaly map near Dumbarton Bridge" },
      h("path", { className: "map-water", d: "M25 126 C72 92 88 46 142 64 C198 82 217 22 277 36 L277 150 L25 150 Z" }),
      h("path", { className: "map-shore", d: "M25 126 C78 110 105 92 151 102 C201 113 235 82 277 88" }),
      ...all.map((point) => {
        const pos = plot(point);
        const bridge = point.name === "Dumbarton Bridge";
        return h(
          "g",
          { key: point.name },
          h("circle", { className: bridge ? "map-dot bridge" : "map-dot", cx: pos.x, cy: pos.y, r: bridge ? 8 : 6 }),
          h("text", { x: Math.min(236, pos.x + 8), y: Math.max(18, pos.y - 8) }, bridge ? "Bridge" : point.name.split(" ")[0])
        );
      })
    )
  );
}

function AlertsPage({ selected, settings }) {
  const [scan, setScan] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`/api/anomalies?date=${selected}`)
      .then((response) => response.json())
      .then(setScan)
      .finally(() => setLoading(false));
  }, [selected]);

  const rawAnomalies = (scan && scan.anomalies) || [];
  const anomalies = rawAnomalies.filter((item) => {
    if (settings.alertSensitivity === "Cautious") return true;
    if (settings.alertSensitivity === "Relaxed") return severityClass(item.severity) !== "low";
    return item.kind !== "Normal";
  });
  const points = (scan && scan.points) || [];

  return [
    h(
      "section",
      { className: "topbar alert-top", key: "alert-top" },
      h("div", null, h("p", { className: "eyebrow" }, "Weather alerts"), h("h1", null, "Local scan")),
      h("div", { className: "avatar" }, h(Icon, { name: "bell" }))
    ),
    h(
      "section",
      { className: `alert-status ${severityClass(scan && scan.status)}`, key: "alert-status" },
      h("div", null, h("p", { className: "eyebrow" }, `${settings.alertSensitivity} alerts`), h("h2", null, loading ? "Scanning NOAA..." : `${scan.status} conditions`), h("p", null, scan ? scan.summary : "Comparing nearby NOAA/NWS grid points for weather outliers.")),
      h("strong", null, loading ? "--" : anomalies.length)
    ),
    h(AlertMap, { key: "alert-map", points, center: scan && scan.center }),
    h(
      "section",
      { className: "alert-list", key: "alert-list" },
      ...(loading
        ? [h("article", { className: "anomaly-card low", key: "loading" }, h("span", null, "Loading"), h("h3", null, "Checking weather anomaly signals"), h("p", null, "Pulling NOAA/NWS forecast points near Dumbarton Bridge."))]
        : anomalies.map((item) =>
            h(
              "article",
              { className: `anomaly-card ${severityClass(item.severity)}`, key: `${item.kind}-${item.title}` },
              h("span", null, `${item.kind} - ${item.severity}`),
              h("h3", null, item.title),
              h("p", null, item.message),
              h("small", null, item.advice)
            )
          ))
    ),
    h(
      "section",
      { className: "scan-points", key: "scan-points" },
      h("div", { className: "section-head compact" }, h("h2", null, "Scanned places"), h("span", null, "nearby grid")),
      ...points.map((point) =>
        h(
          "article",
          { key: point.name },
          h("strong", null, point.name),
          h("span", null, `${point.wind ?? "--"} mph wind`),
          h("span", null, `${point.temp ?? "--"} F`),
          h("span", null, `${point.precip ?? 0}% rain`)
        )
      )
    )
  ];
}

function ProfilePage({ settings, setSettings }) {
  const updateSetting = (key, value) => {
    setSettings((current) => ({ ...current, [key]: value }));
  };
  const toggleArraySetting = (key, value) => {
    setSettings((current) => {
      const existing = current[key] || [];
      const next = existing.includes(value) ? existing.filter((item) => item !== value) : [...existing, value];
      return { ...current, [key]: next.length ? next : [value] };
    });
  };
  const resetSettings = () => setSettings(defaultSettings);

  return [
    h(
      "section",
      { className: "topbar profile-top", key: "profile-top" },
      h("div", null, h("p", { className: "eyebrow" }, "Profile"), h("h1", null, "Settings & Help")),
      h("div", { className: "avatar" }, h(Icon, { name: "user" }))
    ),
    h(
      "section",
      { className: "profile-card", key: "profile-card" },
      h("p", { className: "eyebrow" }, `Hello, ${settings.displayName || "Angler"}`),
      h("h2", null, settings.spotName || "Dumbarton Bridge"),
      h("p", null, "Customize the app so forecast cards, fish tips, alerts, and learning resources match how you fish.")
    ),
    h(
      "section",
      { className: "settings-panel", key: "settings-panel" },
      h("div", { className: "section-head compact" }, h("h2", null, "Customize"), h("span", null, "saved here")),
      h("label", null, h("span", null, "Display name"), h("input", { value: settings.displayName, onChange: (event) => updateSetting("displayName", event.target.value), placeholder: "Angler" })),
      h("label", null, h("span", null, "Fishing spot label"), h("input", { value: settings.spotName, onChange: (event) => updateSetting("spotName", event.target.value), placeholder: "Dumbarton Bridge" })),
      h(
        "label",
        null,
        h("span", null, "Experience level"),
        h("select", { value: settings.experience, onChange: (event) => updateSetting("experience", event.target.value) }, h("option", null, "Beginner"), h("option", null, "Intermediate"), h("option", null, "Experienced"))
      ),
      h(
        "label",
        null,
        h("span", null, "Alert sensitivity"),
        h("select", { value: settings.alertSensitivity, onChange: (event) => updateSetting("alertSensitivity", event.target.value) }, h("option", null, "Cautious"), h("option", null, "Normal"), h("option", null, "Relaxed"))
      ),
      h(
        "label",
        null,
        h("span", null, "Units"),
        h("select", { value: settings.units, onChange: (event) => updateSetting("units", event.target.value) }, h("option", null, "US customary"), h("option", null, "Metric soon"))
      ),
      h("div", { className: "choice-group" }, h("strong", null, "Preferred fish"), h("p", null, "These appear first on Home."), ...speciesOptions.map((name) => h("button", { className: settings.preferredSpecies.includes(name) ? "active" : "", key: name, onClick: () => toggleArraySetting("preferredSpecies", name) }, name))),
      h("div", { className: "choice-group" }, h("strong", null, "Learning topics"), h("p", null, "Explore opens with your first selected topic."), ...interestOptions.map((name) => h("button", { className: settings.learningInterests.includes(name) ? "active" : "", key: name, onClick: () => toggleArraySetting("learningInterests", name) }, name))),
      h("button", { className: "reset-button", onClick: resetSettings }, "Reset defaults")
    ),
    h(
      "section",
      { className: "profile-list", key: "profile-list" },
      h("article", null, h("strong", null, "Preferred species"), h("span", null, settings.preferredSpecies.join(", "))),
      h("article", null, h("strong", null, "Alert style"), h("span", null, `${settings.alertSensitivity} plain-language NOAA/NWS alerts`)),
      h("article", null, h("strong", null, "Learning interests"), h("span", null, settings.learningInterests.join(", "))),
      h("article", null, h("strong", null, "Data sources"), h("span", null, "NOAA tides, NWS weather, EPA water resources, NOAA Fisheries, geospatial scan"))
    ),
    h(
      "section",
      { className: "help-section", key: "help-section" },
      h("div", { className: "section-head compact" }, h("h2", null, "Help"), h("span", null, "How to use")),
      h(
        "article",
        null,
        h("h3", null, "Start on Home"),
        h("p", null, "Use the fishing score, best time window, no-catch clues, tide chart, wind chart, and species tips to decide whether today is worth fishing.")
      ),
      h(
        "article",
        null,
        h("h3", null, "Use No-catch clues after a blank trip"),
        h("p", null, "The app checks NOAA tide movement, NWS wind and weather, water temperature when available, and moon timing to explain likely reasons nothing bit.")
      ),
      h(
        "article",
        null,
        h("h3", null, "Check Alerts before going"),
        h("p", null, "Alerts compares nearby NOAA/NWS weather points and calls out unusual wind, rain, temperature, or active weather warnings.")
      ),
      h(
        "article",
        null,
        h("h3", null, "Learn in Explore"),
        h("p", null, "Explore has free NOAA, EPA, and education resources about fishing, weather, ecology, lakes, water laws, and conservation.")
      ),
      h("div", { className: "faq-title" }, "FAQs"),
      h("details", null, h("summary", null, "What does the fishing score mean?"), h("p", null, "It is a 0 to 100 estimate based on tide movement, wind, water temperature when available, moon phase, and daylight timing.")),
      h("details", null, h("summary", null, "Why did I not catch anything?"), h("p", null, "Open Home and read No-catch clues. It points to likely causes such as slack current, strong wind, water temperature mismatch, changing weather, or technique and location fit.")),
      h("details", null, h("summary", null, "How often does the app update?"), h("p", null, "Weather and alerts can refresh about every 10 to 20 minutes. Tide predictions are cached for about 1 hour.")),
      h("details", null, h("summary", null, "Is this a safety guarantee?"), h("p", null, "No. It is a decision aid. Always look at the water, check official warnings, and avoid fishing if conditions feel unsafe.")),
      h("details", null, h("summary", null, "Why does water temperature sometimes show blank?"), h("p", null, "Some NOAA stations do not report every product at all times. When water temperature is missing, the app leans more on tide, wind, and light.")),
      h("details", null, h("summary", null, "Which tab should I use first?"), h("p", null, "Use Home for today’s fishing decision, Alerts for safety, Explore for learning, and Profile for help and app settings."))
    )
  ];
}

function BottomNav({ activeTab, setActiveTab }) {
  return h(
    "nav",
    { className: "bottom-nav", "aria-label": "Main navigation" },
    h("button", { className: activeTab === "home" ? "selected" : "", onClick: () => setActiveTab("home") }, h(Icon, { name: "home" }), h("span", null, "Home")),
    h("button", { className: activeTab === "explore" ? "selected" : "", onClick: () => setActiveTab("explore") }, h(Icon, { name: "compass" }), h("span", null, "Explore")),
    h("button", { className: "add", onClick: () => setActiveTab("explore"), "aria-label": "Open learning feed" }, h(Icon, { name: "plus" })),
    h("button", { className: activeTab === "alerts" ? "selected" : "", onClick: () => setActiveTab("alerts") }, h(Icon, { name: "bell" }), h("span", null, "Alerts")),
    h("button", { className: activeTab === "profile" ? "selected" : "", onClick: () => setActiveTab("profile") }, h(Icon, { name: "user" }), h("span", null, "Profile"))
  );
}

function App() {
  if (window.location.protocol === "file:") {
    return h(
      "main",
      { className: "phone-shell file-shell" },
      h(
        "section",
        { className: "topbar" },
        h("div", null, h("p", { className: "eyebrow" }, "App setup"), h("h1", null, "Open with server")),
        h("div", { className: "avatar" }, h(Icon, { name: "fish" }))
      ),
      h(
        "section",
        { className: "file-card" },
        h("h2", null, "This file view cannot load NOAA data"),
        h("p", null, "The app needs the local Python backend for tides, weather, alerts, and settings. Use the server link below."),
        h("a", { href: "http://127.0.0.1:8787/" }, "Open working app")
      ),
      h(
        "section",
        { className: "help-section" },
        h("div", { className: "section-head compact" }, h("h2", null, "How to open")),
        h("article", null, h("h3", null, "Use the localhost link"), h("p", null, "Keep the Python server running, then open http://127.0.0.1:8787 in the browser."))
      )
    );
  }

  const [selected, setSelected] = useState(isoDate(today));
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("home");
  const [settings, setSettings] = useState(loadSettings);

  useEffect(() => {
    setLoading(true);
    fetch(`/api/forecast?date=${selected}`)
      .then((response) => response.json())
      .then(setForecast)
      .finally(() => setLoading(false));
  }, [selected]);

  useEffect(() => {
    saveSettings(settings);
  }, [settings]);

  return h(
    "main",
    { className: `phone-shell ${activeTab === "explore" ? "explore-shell" : ""} ${activeTab === "alerts" ? "alerts-shell" : ""}` },
    activeTab === "explore"
      ? h(ExplorePage, { key: "explore-page", settings })
      : activeTab === "alerts"
        ? h(AlertsPage, { key: "alerts-page", selected, settings })
        : activeTab === "profile"
          ? h(ProfilePage, { key: "profile-page", settings, setSettings })
          : h(HomePage, { key: "home-page", selected, setSelected, forecast, loading, settings }),
    h(BottomNav, { activeTab, setActiveTab })
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(h(App));
