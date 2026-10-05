"use client";

import { useCallback, useEffect, useState } from "react";

type AlertRecord = {
  id: string;
  location: string;
  risk_level: string;
  status: string;
  created_at: string;
  feature_status: string;
};

type HealthResponse = {
  status: string;
  database: string;
};

type AlertsResponse = {
  alerts: AlertRecord[];
};

type FeatureStatus =
  | "LIVE"
  | "DEMO"
  | "SIMULATED"
  | "SCAFFOLD"
  | "MISSING";

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
    status: "MISSING",
    detail: "No verified shelter dataset or directions are available.",
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
        "status" in alert &&
        "created_at" in alert &&
        typeof alert.id === "string" &&
        typeof alert.location === "string" &&
        typeof alert.risk_level === "string" &&
        typeof alert.status === "string" &&
        typeof alert.created_at === "string",
    )
  );
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
  const [healthError, setHealthError] = useState("");
  const [alertsError, setAlertsError] = useState("");
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    const [healthResult, alertsResult] = await Promise.allSettled([
      getJson("/health"),
      getJson("/api/v1/alerts"),
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
    setLoading(false);
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const apiIsLive = health?.status === "LIVE" && health.database === "LIVE";

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
        {alertsError ? (
          <div className="empty-state" role="status">
            <strong>Alert records unavailable</strong>
            <span>{alertsError}</span>
          </div>
        ) : alerts.length === 0 ? (
          <div className="empty-state">
            <strong>{loading ? "Loading alert records…" : "No alert records returned."}</strong>
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
