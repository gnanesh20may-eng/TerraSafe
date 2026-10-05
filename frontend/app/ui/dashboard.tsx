"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useMemo, useState } from "react";
import type { RiskZone, ShelterPoint } from "./risk-map";

const RiskMapView = dynamic(
  () => import("./risk-map").then((module) => module.RiskMap),
  { ssr: false, loading: () => <div className="map-loading">Loading map…</div> },
);

type AlertRecord = {
  id: string;
  zone_id: string;
  location: string;
  risk_level: string;
  risk_score: number;
  status: string;
  created_at: string;
  latitude: number | null;
  longitude: number | null;
};

type HealthResponse = {
  status: string;
  database: string;
};

type AlertsResponse = {
  alerts: AlertRecord[];
};

type RiskResponse = {
  status: string;
  weather: {
    status: "LIVE" | "DEMO" | "MISSING";
    reason: string | null;
    provider: string | null;
    fetched_at: string | null;
    data_timestamp: string | null;
    precipitation_mm: number | null;
    soil_moisture_fraction: number | null;
    seven_day_trend: { date: string; precipitation_mm: number | null }[] | null;
  };
  zones: RiskZone[];
  shelters: { status: "SIMULATED"; locations: ShelterPoint[]; notice: string };
}

type ScenarioResult = {
  status: "SIMULATED";
  risk_score: number;
  risk_level: string;
  method: string;
  disclaimer: string;
};

type EvacuationResult = {
  status: "SIMULATED";
  feature_status: "SIMULATED";
  nearest_shelter: ShelterPoint;
  distance_km: number;
  distance_method: string;
  route_status: "MISSING";
  notice: string;
};

type FeatureStatus =
  | "LIVE"
  | "DEMO"
  | "SIMULATED"
  | "SCAFFOLD"
  | "MISSING";

type Language = "en" | "ta";

const COPY: Record<Language, Record<string, string>> = {
  en: {
    mapTitle: "Nilgiris risk zones",
    mapIntro: "Regional Open-Meteo weather is shared across simulated zones.",
    heatmap: "Risk heatmap",
    zones: "Zone markers",
    shelters: "Shelters",
    trendTitle: "7-day rainfall trend",
    trendMissing: "No verified seven-day trend is available; no sample values are shown.",
    selected: "Selected zone",
    score: "Risk index",
    factors: "Top model factors",
    why: "Why this score",
    token: "Local operator token",
    tokenHint: "Token is used only in memory and is not saved.",
    createAlert: "Create demo alert",
    lifecycle: "Prototype alert actions",
    approve: "Approve",
    send: "Send (mock only)",
    delivered: "Mark delivered",
    acknowledge: "Acknowledge",
    resolve: "Resolve",
    noAlerts: "No alert records returned by the API.",
    weatherAt: "Weather data timestamp",
    riskDisclaimer: "SIMULATED model and zone geometry; DEMO alert workflow. Not a warning.",
    decisionTitle: "Decision support",
    simulationTitle: "Rainfall what-if",
    simulationIntro: "Explore a transparent scenario using the selected synthetic zone baseline.",
    rainfallInput: "What-if rainfall (mm)",
    durationInput: "Rain duration (hours)",
    roadCutInput: "Include a road cut",
    simulateButton: "Run simulated scenario",
    shelterTitle: "Nearest placeholder shelter",
    shelterIntro: "Uses the selected zone and placeholder points; this is not a destination recommendation.",
    shelterButton: "Calculate straight-line distance",
    noDecisionResult: "Run a scenario or distance calculation to see results.",
    routeMissing: "Navigable route: MISSING",
    simulationError: "Scenario simulation failed.",
    evacuationError: "Shelter estimate failed.",
    language: "Language",
  },
  ta: {
    mapTitle: "நீலகிரி இடர் மண்டலங்கள்",
    mapIntro: "Open-Meteo வானிலைத் தரவு உருவக மண்டலங்களுக்கு பொதுவாகப் பயன்படுத்தப்படுகிறது.",
    heatmap: "இடர் வெப்ப வரைபடம்",
    zones: "மண்டலக் குறியீடுகள்",
    shelters: "தங்குமிடங்கள்",
    trendTitle: "7 நாள் மழைப்பொழிவு போக்கு",
    trendMissing: "சரிபார்க்கப்பட்ட ஏழு நாள் போக்கு இல்லை; மாதிரி மதிப்புகள் காட்டப்படவில்லை.",
    selected: "தேர்ந்தெடுத்த மண்டலம்",
    score: "இடர் குறியீடு",
    factors: "மாதிரியின் முக்கிய காரணிகள்",
    why: "இந்த மதிப்புக்கான விளக்கம்",
    token: "உள்ளூர் இயக்குநர் டோக்கன்",
    tokenHint: "டோக்கன் நினைவகத்தில் மட்டும் பயன்படுத்தப்படும்; சேமிக்கப்படாது.",
    createAlert: "டெமோ எச்சரிக்கை உருவாக்கு",
    lifecycle: "மாதிரி எச்சரிக்கை செயல்கள்",
    approve: "ஒப்புதல்",
    send: "அனுப்பு (போலி மட்டும்)",
    delivered: "வழங்கியதாகக் குறி",
    acknowledge: "பெற்றதை உறுதிப்படுத்து",
    resolve: "தீர்வு செய்",
    noAlerts: "API-யில் எச்சரிக்கை பதிவுகள் இல்லை.",
    weatherAt: "வானிலைத் தரவு நேரம்",
    riskDisclaimer: "உருவக மாதிரி மற்றும் மண்டலங்கள்; டெமோ எச்சரிக்கை நடைமுறை. அதிகாரப்பூர்வ எச்சரிக்கை அல்ல.",
    decisionTitle: "முடிவு ஆதரவு",
    simulationTitle: "மழைப்பொழிவு மாற்றுச் சூழல்",
    simulationIntro: "தேர்ந்தெடுத்த உருவக மண்டலத்தின் அடிப்படையில் வெளிப்படையான சூழலை ஆராயுங்கள்.",
    rainfallInput: "மாற்றுச் சூழல் மழை (மி.மீ.)",
    durationInput: "மழை நீடிப்பு (மணி)",
    roadCutInput: "சாலை வெட்டு சேர்க்கவும்",
    simulateButton: "உருவக சூழலைக் கணக்கிடு",
    shelterTitle: "அருகிலுள்ள மாதிரி தங்குமிடம்",
    shelterIntro: "தேர்ந்தெடுத்த மண்டலம் மற்றும் மாதிரி இடங்களைப் பயன்படுத்துகிறது; இது தங்குமிடப் பரிந்துரை அல்ல.",
    shelterButton: "நேர்கோட்டு தூரத்தைக் கணக்கிடு",
    noDecisionResult: "முடிவைக் காண சூழல் அல்லது தூரத்தைக் கணக்கிடுங்கள்.",
    routeMissing: "வழிசெலுத்தும் பாதை: இல்லை",
    simulationError: "சூழல் உருவகப்படுத்தல் தோல்வியடைந்தது.",
    evacuationError: "தங்குமிட மதிப்பீடு தோல்வியடைந்தது.",
    language: "மொழி",
  },
};

const apiBase =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "") ??
  "http://localhost:8000";

const featureCards: {
  name: string;
  status: FeatureStatus;
  detail: string;
}[] = [
  {
    name: "Risk estimate",
    status: "SIMULATED",
    detail: "Generated pilot inputs; never an operational warning.",
  },
  {
    name: "Alert lifecycle",
    status: "DEMO",
    detail: "Local prototype records and tested role gates.",
  },
  {
    name: "Notifications",
    status: "DEMO",
    detail: "SMS, WhatsApp, email, voice, and push are mock-only.",
  },
  {
    name: "SOS intake",
    status: "DEMO",
    detail: "Stores a request; no emergency service is dispatched.",
  },
  {
    name: "Evacuation routes",
    status: "SIMULATED",
    detail: "Nearest placeholder and straight-line distance only; real routes are missing.",
  },
  {
    name: "RESCUE coordination",
    status: "SCAFFOLD",
    detail: "Placeholder only; no live incident coordination.",
  },
  {
    name: "Model metrics",
    status: "MISSING",
    detail: "No real-world evaluation metrics are present.",
  },
];

function isHealthResponse(value: unknown): value is HealthResponse {
  return (
    typeof value === "object" &&
    value !== null &&
    "status" in value &&
    "database" in value &&
    typeof value.status === "string" &&
    typeof value.database === "string"
  );
}

function isAlertsResponse(value: unknown): value is AlertsResponse {
  return (
    typeof value === "object" &&
    value !== null &&
    "alerts" in value &&
    Array.isArray(value.alerts) &&
    value.alerts.every(
      (alert: unknown) =>
        typeof alert === "object" &&
        alert !== null &&
        "id" in alert &&
        "location" in alert &&
        "risk_level" in alert &&
        "risk_score" in alert &&
        "zone_id" in alert &&
        "status" in alert &&
        "created_at" in alert &&
        typeof alert.id === "string" &&
        typeof alert.location === "string" &&
        typeof alert.risk_level === "string" &&
        typeof alert.risk_score === "number" &&
        typeof alert.zone_id === "string" &&
        typeof alert.status === "string" &&
        typeof alert.created_at === "string",
    )
  );
}

function isShelterPoint(value: unknown): value is ShelterPoint {
  return (
    typeof value === "object" &&
    value !== null &&
    "shelter_id" in value &&
    "name" in value &&
    "latitude" in value &&
    "longitude" in value &&
    "status" in value &&
    typeof value.shelter_id === "string" &&
    typeof value.name === "string" &&
    typeof value.latitude === "number" &&
    typeof value.longitude === "number" &&
    value.status === "SIMULATED"
  );
}

function isScenarioResult(value: unknown): value is ScenarioResult {
  return (
    typeof value === "object" &&
    value !== null &&
    "status" in value &&
    value.status === "SIMULATED" &&
    "risk_score" in value &&
    typeof value.risk_score === "number" &&
    "risk_level" in value &&
    typeof value.risk_level === "string" &&
    "method" in value &&
    typeof value.method === "string" &&
    "disclaimer" in value &&
    typeof value.disclaimer === "string"
  );
}

function isEvacuationResult(value: unknown): value is EvacuationResult {
  return (
    typeof value === "object" &&
    value !== null &&
    "status" in value &&
    value.status === "SIMULATED" &&
    "feature_status" in value &&
    value.feature_status === "SIMULATED" &&
    "nearest_shelter" in value &&
    isShelterPoint(value.nearest_shelter) &&
    "distance_km" in value &&
    typeof value.distance_km === "number" &&
    "distance_method" in value &&
    typeof value.distance_method === "string" &&
    "route_status" in value &&
    value.route_status === "MISSING" &&
    "notice" in value &&
    typeof value.notice === "string"
  );
}

function isRiskZone(value: unknown): value is RiskZone {
  return (
    typeof value === "object" &&
    value !== null &&
    "zone_id" in value &&
    "location" in value &&
    "latitude" in value &&
    "longitude" in value &&
    "bounds" in value &&
    "risk_score" in value &&
    "risk_level" in value &&
    "risk_status" in value &&
    "weather_status" in value &&
    "terrain_status" in value &&
    "top_factors" in value &&
    "why" in value &&
    typeof value.zone_id === "string" &&
    typeof value.location === "string" &&
    typeof value.latitude === "number" &&
    typeof value.longitude === "number" &&
    Array.isArray(value.bounds) &&
    value.bounds.length === 4 &&
    value.bounds.every((coordinate) => typeof coordinate === "number") &&
    typeof value.risk_score === "number" &&
    typeof value.risk_level === "string" &&
    (value.risk_status === "SIMULATED" || value.risk_status === "DEMO") &&
    (value.weather_status === "LIVE" || value.weather_status === "DEMO") &&
    value.terrain_status === "SIMULATED" &&
    Array.isArray(value.top_factors) &&
    typeof value.why === "string"
  );
}

function isRiskResponse(value: unknown): value is RiskResponse {
  if (
    typeof value !== "object" ||
    value === null ||
    !("status" in value) ||
    !("weather" in value) ||
    !("zones" in value) ||
    !("shelters" in value) ||
    typeof value.status !== "string" ||
    !Array.isArray(value.zones) ||
    !value.zones.every(isRiskZone) ||
    typeof value.weather !== "object" ||
    value.weather === null ||
    typeof value.shelters !== "object" ||
    value.shelters === null ||
    !("status" in value.weather) ||
    !("reason" in value.weather) ||
    !("provider" in value.weather) ||
    !("fetched_at" in value.weather) ||
    !("data_timestamp" in value.weather) ||
    !("precipitation_mm" in value.weather) ||
    !("soil_moisture_fraction" in value.weather) ||
    !("seven_day_trend" in value.weather) ||
    !("status" in value.shelters) ||
    !("locations" in value.shelters) ||
    !("notice" in value.shelters) ||
    (value.weather.status !== "LIVE" &&
      value.weather.status !== "DEMO" &&
      value.weather.status !== "MISSING") ||
    value.shelters.status !== "SIMULATED" ||
    !Array.isArray(value.shelters.locations) ||
    typeof value.shelters.notice !== "string"
  ) {
    return false;
  }
  return true;
}

async function getJson(path: string): Promise<unknown> {
  const response = await fetch(`${apiBase}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`${path} returned HTTP ${response.status}`);
  }
  return response.json();
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Unexpected API response.";
}

function StatusTag({ status }: { status: FeatureStatus }) {
  return <span className={`status-tag status-${status.toLowerCase()}`}>{status}</span>;
}

function formatTimestamp(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

export function Dashboard() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [alerts, setAlerts] = useState<AlertRecord[]>([]);
  const [risk, setRisk] = useState<RiskResponse | null>(null);
  const [healthError, setHealthError] = useState("");
  const [alertsError, setAlertsError] = useState("");
  const [riskError, setRiskError] = useState("");
  const [selectedZoneId, setSelectedZoneId] = useState("");
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showZoneMarkers, setShowZoneMarkers] = useState(true);
  const [showShelters, setShowShelters] = useState(false);
  const [language, setLanguage] = useState<Language>("en");
  const [operatorToken, setOperatorToken] = useState("");
  const [actionError, setActionError] = useState("");
  const [pendingAction, setPendingAction] = useState("");
  const [whatIfRainfall, setWhatIfRainfall] = useState("0");
  const [whatIfDuration, setWhatIfDuration] = useState("24");
  const [includeRoadCut, setIncludeRoadCut] = useState(false);
  const [scenarioResult, setScenarioResult] = useState<ScenarioResult | null>(null);
  const [evacuationResult, setEvacuationResult] = useState<EvacuationResult | null>(null);
  const [supportError, setSupportError] = useState("");
  const [supportPending, setSupportPending] = useState("");
  const [loading, setLoading] = useState(true);
  const t = COPY[language];

  const refresh = useCallback(async () => {
    setLoading(true);
    const [healthResult, alertsResult, riskResult] = await Promise.allSettled([
      getJson("/health"),
      getJson("/api/v1/alerts"),
      getJson("/api/v1/risk?location=Nilgiris"),
    ]);

    if (healthResult.status === "fulfilled" && isHealthResponse(healthResult.value)) {
      setHealth(healthResult.value);
      setHealthError("");
    } else {
      setHealth(null);
      setHealthError(
        healthResult.status === "rejected"
          ? errorMessage(healthResult.reason)
          : "The API returned an unexpected health response.",
      );
    }

    if (alertsResult.status === "fulfilled" && isAlertsResponse(alertsResult.value)) {
      setAlerts(alertsResult.value.alerts);
      setAlertsError("");
    } else {
      setAlerts([]);
      setAlertsError(
        alertsResult.status === "rejected"
          ? errorMessage(alertsResult.reason)
          : "The API returned an unexpected alert response.",
      );
    }
    if (riskResult.status === "fulfilled" && isRiskResponse(riskResult.value)) {
      const riskData = riskResult.value;
      setRisk(riskData);
      setRiskError("");
      setSelectedZoneId((current) =>
        riskData.zones.some((zone) => zone.zone_id === current)
          ? current
          : riskData.zones[0]?.zone_id ?? "",
      );
    } else {
      setRisk(null);
      setRiskError(
        riskResult.status === "rejected"
          ? errorMessage(riskResult.reason)
          : "The API returned an unexpected risk response.",
      );
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const apiIsLive = health?.status === "LIVE" && health.database === "LIVE";
  const selectedZone = useMemo(
    () => risk?.zones.find((zone) => zone.zone_id === selectedZoneId) ?? null,
    [risk, selectedZoneId],
  );

  async function submitAlert() {
    if (!selectedZone) return;
    setActionError("");
    setPendingAction("create");
    try {
      const response = await fetch(`${apiBase}/api/v1/alerts`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${operatorToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          zone_id: selectedZone.zone_id,
          location: selectedZone.location,
          latitude: selectedZone.latitude,
          longitude: selectedZone.longitude,
          risk_score: selectedZone.risk_score,
          language: language === "ta" ? "ta" : "en",
          message: selectedZone.why,
        }),
      });
      if (!response.ok) throw new Error(`Alert creation returned HTTP ${response.status}`);
      await refresh();
    } catch (error) {
      setActionError(errorMessage(error));
    } finally {
      setPendingAction("");
    }
  }

  async function runScenario() {
    if (!selectedZone) return;
    setSupportError("");
    setScenarioResult(null);
    setSupportPending("scenario");
    try {
      const response = await fetch(`${apiBase}/api/v1/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          baseline_score: selectedZone.risk_score,
          rainfall_mm: Number(whatIfRainfall),
          duration_hours: Number(whatIfDuration),
          road_cut: includeRoadCut,
        }),
      });
      if (!response.ok) {
        throw new Error(`/api/v1/simulate returned HTTP ${response.status}`);
      }
      const result: unknown = await response.json();
      if (!isScenarioResult(result)) throw new Error(t.simulationError);
      setScenarioResult(result);
    } catch (error) {
      setSupportError(errorMessage(error));
    } finally {
      setSupportPending("");
    }
  }

  async function findNearestShelter() {
    if (!selectedZone) return;
    setSupportError("");
    setEvacuationResult(null);
    setSupportPending("evacuation");
    try {
      const query = new URLSearchParams({
        latitude: String(selectedZone.latitude),
        longitude: String(selectedZone.longitude),
      });
      const response = await fetch(`${apiBase}/api/v1/evacuation?${query}`);
      if (!response.ok) {
        throw new Error(`/api/v1/evacuation returned HTTP ${response.status}`);
      }
      const result: unknown = await response.json();
      if (!isEvacuationResult(result)) throw new Error(t.evacuationError);
      setEvacuationResult(result);
    } catch (error) {
      setSupportError(errorMessage(error));
    } finally {
      setSupportPending("");
    }
  }

  function nextTransition(alert: AlertRecord): { event: string; label: string } | null {
    const transitions: Record<string, { event: string; label: string }> = {
      Created: { event: "Approved", label: t.approve },
      Approved: { event: "Sent", label: t.send },
      Sent: { event: "Delivered", label: t.delivered },
      Delivered: { event: "Acknowledged", label: t.acknowledge },
      Acknowledged: { event: "Resolved", label: t.resolve },
    };
    return transitions[alert.status] ?? null;
  }

  async function transitionAlert(alert: AlertRecord) {
    const transition = nextTransition(alert);
    if (!transition) return;
    setActionError("");
    setPendingAction(alert.id);
    try {
      const response = await fetch(
        `${apiBase}/api/v1/alerts/${encodeURIComponent(alert.id)}/transition`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${operatorToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ event: transition.event }),
        },
      );
      if (!response.ok) {
        throw new Error(`Alert transition returned HTTP ${response.status}`);
      }
      await refresh();
    } catch (error) {
      setActionError(errorMessage(error));
    } finally {
      setPendingAction("");
    }
  }

  const trendPoints = risk?.weather.seven_day_trend ?? [];
  const trendValues = trendPoints
    .map((point) => point.precipitation_mm)
    .filter((value): value is number => value !== null);
  const trendMax = Math.max(1, ...trendValues);

  return (
    <main className="page-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="TerraSafe home">
          <span className="brand-mark" aria-hidden="true">
            TS
          </span>
          <span>
            <strong>TerraSafe</strong>
            <small>RESCUE / FIELD VIEW</small>
          </span>
        </a>
        <div className="topbar-right">
          <span className="prototype-label">PROTOTYPE · NOT AN OFFICIAL ALERT</span>
          <label className="language-picker">
            <span>{t.language}</span>
            <select
              value={language}
              onChange={(event) => setLanguage(event.target.value as Language)}
              aria-label={t.language}
            >
              <option value="en">English</option>
              <option value="ta">தமிழ்</option>
            </select>
          </label>
          <button className="refresh-button" onClick={() => void refresh()} disabled={loading}>
            {loading ? "Checking…" : "Refresh"}
          </button>
        </div>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">LANDSLIDE DECISION SUPPORT</p>
          <h1>See the status.<br /><span>Know the limits.</span></h1>
          <p className="hero-description">
            An experimental monitoring dashboard. Use official IMD, NDMA, and
            GSI information and local emergency services for real decisions.
          </p>
        </div>
        <aside className="connection-card" aria-live="polite">
          <div className="card-heading">
            <span className="pulse" aria-hidden="true" />
            <span>API + DATABASE</span>
            <StatusTag status={apiIsLive ? "LIVE" : "MISSING"} />
          </div>
          {healthError ? (
            <p className="connection-message">
              Backend unavailable: {healthError}
            </p>
          ) : health ? (
            <p className="connection-message">
              API {health.status} · database {health.database}
            </p>
          ) : (
            <p className="connection-message">Checking local API…</p>
          )}
          <code>{apiBase}</code>
        </aside>
      </section>

      <section className="disclaimer" role="note">
        <span className="disclaimer-icon" aria-hidden="true">!</span>
        <p>
          <strong>Safety notice</strong>
          This prototype is not a replacement for official IMD, NDMA, or GSI
          warnings. No route or emergency dispatch is provided here.
        </p>
      </section>

      <section className="section-block map-section">
        <div className="section-title">
          <div>
            <p className="eyebrow">SIMULATED ZONES · WEATHER SOURCE TAGGED</p>
            <h2>{t.mapTitle}</h2>
          </div>
          <StatusTag status={risk?.weather.status ?? "MISSING"} />
        </div>
        <p className="map-intro">{t.mapIntro}</p>
        {riskError ? (
          <div className="empty-state" role="status">
            <strong>Risk map unavailable</strong>
            <span>{riskError}</span>
          </div>
        ) : (
          <div className="map-layout">
            <div className="map-main">
              <div className="map-toolbar">
                <label>
                  <input
                    type="checkbox"
                    checked={showHeatmap}
                    onChange={(event) => setShowHeatmap(event.target.checked)}
                  />
                  {t.heatmap} <StatusTag status="SIMULATED" />
                </label>
                <label>
                  <input
                    type="checkbox"
                    checked={showZoneMarkers}
                    onChange={(event) => setShowZoneMarkers(event.target.checked)}
                  />
                  {t.zones} <StatusTag status="SIMULATED" />
                </label>
                <label>
                  <input
                    type="checkbox"
                    checked={showShelters}
                    onChange={(event) => setShowShelters(event.target.checked)}
                  />
                  {t.shelters} <StatusTag status="SIMULATED" />
                </label>
              </div>
              {risk ? (
                <RiskMapView
                  zones={risk.zones}
                  shelters={risk.shelters.locations}
                  showHeatmap={showHeatmap}
                  showZoneMarkers={showZoneMarkers}
                  showShelters={showShelters}
                  onSelectZone={(zoneId) => {
                    setSelectedZoneId(zoneId);
                    setScenarioResult(null);
                    setEvacuationResult(null);
                  }}
                />
              ) : (
                <div className="map-loading">Loading risk data…</div>
              )}
              <p className="map-attribution">
                Map tiles © OpenStreetMap contributors. Risk grid is synthetic;
                shelter points are placeholders, not actual sites.
              </p>
            </div>
            <aside className="zone-drawer" aria-live="polite">
              <p className="eyebrow">{t.selected}</p>
              {selectedZone ? (
                <>
                  <h3>{selectedZone.location}</h3>
                  <div className="drawer-tags">
                    <StatusTag status={selectedZone.risk_status} />
                    <StatusTag status={selectedZone.weather_status} />
                    <StatusTag status={selectedZone.terrain_status} />
                  </div>
                  <p className="zone-score">
                    <span>{t.score}</span>
                    <strong>{selectedZone.risk_score.toFixed(3)}</strong>
                    <small>{selectedZone.risk_level}</small>
                  </p>
                  <h4>{t.factors}</h4>
                  <ul className="factor-list">
                    {selectedZone.top_factors.map((factor) => (
                      <li key={factor.feature}>
                        <span>{factor.feature.replaceAll("_", " ")}</span>
                        <strong>{factor.contribution.toFixed(3)}</strong>
                      </li>
                    ))}
                  </ul>
                  <h4>{t.why}</h4>
                  <p className="zone-why">{selectedZone.why}</p>
                </>
              ) : (
                <p className="zone-why">Select a simulated zone marker.</p>
              )}
              <p className="drawer-disclaimer">{t.riskDisclaimer}</p>
            </aside>
          </div>
        )}
      </section>

      <section className="section-block trend-section">
        <div className="section-title">
          <div>
            <p className="eyebrow">OPEN-METEO OBSERVATIONS · NO GENERATED SERIES</p>
            <h2>{t.trendTitle}</h2>
          </div>
          <StatusTag status={risk?.weather.status ?? "MISSING"} />
        </div>
        {trendPoints.length === 7 ? (
          <div className="trend-chart" role="img" aria-label={t.trendTitle}>
            {trendPoints.map((point) => (
              <div className="trend-column" key={point.date}>
                <span className="trend-value">
                  {point.precipitation_mm === null
                    ? "—"
                    : `${point.precipitation_mm.toFixed(1)} mm`}
                </span>
                <div className="trend-track">
                  <div
                    className="trend-bar"
                    style={{
                      height:
                        point.precipitation_mm === null
                          ? "0%"
                          : `${Math.max(4, (point.precipitation_mm / trendMax) * 100)}%`,
                    }}
                  />
                </div>
                <span className="trend-date">{point.date.slice(5)}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <strong>{risk?.weather.status === "LIVE" ? t.trendMissing : t.trendMissing}</strong>
            <span>
              {risk?.weather.reason
                ? `Weather status: ${risk.weather.status} (${risk.weather.reason}).`
                : "The provider has not returned a complete seven-day series."}
            </span>
          </div>
        )}
        <p className="records-note">
          {t.weatherAt}: {risk?.weather.data_timestamp ?? "unavailable"} ·{" "}
          <StatusTag status={risk?.weather.status ?? "MISSING"} />
        </p>
      </section>

      <section className="section-block decision-section">
        <div className="section-title">
          <div>
            <p className="eyebrow">WHAT-IF · PLACEHOLDER SHELTERS</p>
            <h2>{t.decisionTitle}</h2>
          </div>
          <StatusTag status="SIMULATED" />
        </div>
        <div className="decision-grid">
          <article className="decision-card">
            <h3>{t.simulationTitle} <StatusTag status="SIMULATED" /></h3>
            <p>{t.simulationIntro}</p>
            <div className="decision-controls">
              <label>
                {t.rainfallInput}
                <input
                  type="number"
                  min="0"
                  max="1000"
                  step="0.1"
                  value={whatIfRainfall}
                  onChange={(event) => setWhatIfRainfall(event.target.value)}
                />
              </label>
              <label>
                {t.durationInput}
                <input
                  type="number"
                  min="0.1"
                  max="720"
                  step="0.1"
                  value={whatIfDuration}
                  onChange={(event) => setWhatIfDuration(event.target.value)}
                />
              </label>
              <label className="decision-checkbox">
                <input
                  type="checkbox"
                  checked={includeRoadCut}
                  onChange={(event) => setIncludeRoadCut(event.target.checked)}
                />
                {t.roadCutInput}
              </label>
            </div>
            <button
              className="action-button"
              disabled={!selectedZone || supportPending !== ""}
              onClick={() => void runScenario()}
            >
              {supportPending === "scenario" ? "Working…" : t.simulateButton}
            </button>
            {scenarioResult ? (
              <div className="decision-result" aria-live="polite">
                <div className="drawer-tags">
                  <StatusTag status={scenarioResult.status} />
                  <strong>{scenarioResult.risk_score.toFixed(4)} · {scenarioResult.risk_level}</strong>
                </div>
                <p>{scenarioResult.method}</p>
                <p>{scenarioResult.disclaimer}</p>
              </div>
            ) : (
              <p className="decision-result">{t.noDecisionResult}</p>
            )}
          </article>
          <article className="decision-card">
            <h3>{t.shelterTitle} <StatusTag status="SIMULATED" /></h3>
            <p>{t.shelterIntro}</p>
            <p className="decision-origin">
              {t.selected}: {selectedZone?.location ?? "unavailable"}
            </p>
            <button
              className="action-button"
              disabled={!selectedZone || supportPending !== ""}
              onClick={() => void findNearestShelter()}
            >
              {supportPending === "evacuation" ? "Working…" : t.shelterButton}
            </button>
            {evacuationResult ? (
              <div className="decision-result" aria-live="polite">
                <div className="drawer-tags">
                  <StatusTag status={evacuationResult.feature_status} />
                  <strong>{evacuationResult.nearest_shelter.name}</strong>
                </div>
                <p>{evacuationResult.distance_km.toFixed(3)} km · {evacuationResult.distance_method}</p>
                <p>{evacuationResult.notice}</p>
                <StatusTag status={evacuationResult.route_status} />
              </div>
            ) : (
              <p className="decision-result">{t.routeMissing}</p>
            )}
          </article>
        </div>
        {supportError && <p className="action-error" role="alert">{supportError}</p>}
        <p className="records-note">
          {t.routeMissing}. {t.riskDisclaimer}
        </p>
      </section>

      <section className="section-block">
        <div className="section-title">
          <div>
            <p className="eyebrow">CAPABILITY STATUS</p>
            <h2>What this prototype can—and cannot—do</h2>
          </div>
          <p className="section-side-note">Labels reflect implemented evidence, not readiness.</p>
        </div>
        <div className="feature-grid">
          {featureCards.map((feature) => (
            <article className="feature-card" key={feature.name}>
              <div className="feature-card-top">
                <span className="feature-dot" aria-hidden="true" />
                <StatusTag status={feature.status} />
              </div>
              <h3>{feature.name}</h3>
              <p>{feature.detail}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section-block alerts-section">
        <div className="section-title">
          <div>
            <p className="eyebrow">LOCAL API RECORDS · DEMO</p>
            <h2>Recent alert records</h2>
          </div>
          <span className="record-count">{loading ? "…" : `${alerts.length} records`}</span>
        </div>
        <div className="alert-controls">
          <label>
            {t.token}
            <input
              type="password"
              autoComplete="off"
              value={operatorToken}
              onChange={(event) => setOperatorToken(event.target.value)}
              placeholder="Bearer token"
            />
          </label>
          <span>{t.tokenHint}</span>
          <button
            className="refresh-button"
            disabled={!operatorToken || !selectedZone || pendingAction !== ""}
            onClick={() => void submitAlert()}
          >
            {pendingAction === "create" ? "Working…" : t.createAlert}
          </button>
        </div>
        {actionError && <p className="action-error" role="alert">{actionError}</p>}
        {alertsError ? (
          <div className="empty-state" role="status">
            <strong>Alert records unavailable</strong>
            <span>{alertsError}</span>
          </div>
        ) : alerts.length === 0 ? (
          <div className="empty-state">
            <strong>{loading ? "Loading alert records…" : t.noAlerts}</strong>
            <span>
              This list contains only API records. No sample incidents or
              locations are inserted by the dashboard.
            </span>
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Location</th>
                  <th>Risk level</th>
                  <th>Workflow</th>
                  <th>Created</th>
                  <th>Label</th>
                  <th>{t.lifecycle}</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((alert) => (
                  <tr key={alert.id}>
                    <td>{alert.location}</td>
                    <td>{alert.risk_level}</td>
                    <td>{alert.status}</td>
                    <td>{formatTimestamp(alert.created_at)}</td>
                    <td><StatusTag status="DEMO" /></td>
                    <td>
                      {nextTransition(alert) && (
                        <button
                          className="action-button"
                          disabled={!operatorToken || pendingAction !== ""}
                          onClick={() => void transitionAlert(alert)}
                        >
                          {pendingAction === alert.id
                            ? "Working…"
                            : nextTransition(alert)?.label}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <p className="records-note">
          These are prototype records, not verified hazards or public warnings.
        </p>
      </section>

      <footer className="footer">
        <span>TerraSafe · PSA 04</span>
        <span>Not a replacement for IMD / NDMA / GSI warnings</span>
      </footer>
    </main>
  );
}
