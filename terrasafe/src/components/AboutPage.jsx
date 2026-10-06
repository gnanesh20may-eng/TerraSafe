import { ShieldCheck, AlertTriangle, Info, BookOpen, Globe, ExternalLink, Shield, Zap, Layers } from 'lucide-react'

function AboutPage() {
  return (
    <div className="about-page">
      <PageHeading
        eyebrow="ABOUT TERRASAFE"
        title="Know your area. Stay one step ahead."
        subtitle="Early-warning decision support for landslide-prone communities."
      />

      <section className="panel about-section">
        <h2>What is TerraSafe?</h2>
        <p>
          TerraSafe is an experimental early-warning decision support system for landslide-prone regions.
          It combines satellite data, weather forecasts, terrain analysis, and community reports
          to provide localized risk assessments.
        </p>
        <div className="disclaimer-box">
          <AlertTriangle size={20} />
          <div>
            <strong>Important Disclaimer</strong>
            <p>
              AI-based risk estimation. Early-warning decision support.
              This prototype does not replace official disaster-management warnings.
              Never claim 100% accuracy, an official warning, or guaranteed prediction.
            </p>
          </div>
        </div>
      </section>

      <section className="panel about-section">
        <h2>How It Works</h2>
        <div className="features-grid">
          <FeatureCard 
            icon={<Zap />}
            title="Risk Engine"
            desc="Combines susceptibility modeling, antecedent rainfall, slope stability, and dynamic triggers into a 0-100 risk score."
          />
          <FeatureCard 
            icon={<Layers />}
            title="Multi-Source Data"
            desc="Integrates Open-Meteo, NASA, USGS, GSI, IMD, and local sensor data with explicit LIVE/SIMULATED/DEMO labels."
          />
          <FeatureCard 
            icon={<Globe />}
            title="Map Visualization"
            desc="MapLibre GL 3D terrain with risk layer chips, draggable pin, and micro-zone risk maps."
          />
          <FeatureCard 
            icon={<Shield />}
            title="Explainable AI"
            desc="Factor contributions, plain-language explanations, counterfactuals, and what-if simulator."
          />
          <FeatureCard 
            icon={<AlertTriangle />}
            title="Alert System"
            desc="State machine (NEW→ACKNOWLEDGED→ACTIVE→RESOLVED), false-alarm prevention, bilingual (EN/TA) warnings."
          />
          <FeatureCard 
            icon={<BookOpen />}
            title="Rescue Hub"
            desc="Safe zones, vulnerable-location priority, route abstraction, emergency contacts, offline mode."
          />
        </div>
      </section>

      <section className="panel about-section">
        <h2>Risk Levels</h2>
        <p>Unified 0-100 scale exposed via API and UI:</p>
        <div className="risk-levels-table">
          <div className="risk-level-row risk-low">
            <span className="risk-badge risk-low">LOW</span>
            <span>0–24</span>
            <span>Conditions manageable</span>
          </div>
          <div className="risk-level-row risk-watch">
            <span className="risk-badge risk-watch">WATCH</span>
            <span>25–49</span>
            <span>Extra awareness needed</span>
          </div>
          <div className="risk-level-row risk-high">
            <span className="risk-badge risk-high">HIGH</span>
            <span>50–74</span>
            <span>Stay alert, follow guidance</span>
          </div>
          <div className="risk-level-row risk-critical">
            <span className="risk-badge risk-critical">CRITICAL</span>
            <span>75–100</span>
            <span>Immediate action, ≥2 supporting factors required</span>
          </div>
        </div>
      </section>

      <section className="panel about-section">
        <h2>Data Honesty</h2>
        <p>Every value is explicitly labeled:</p>
        <ul className="honesty-list">
          <li><strong>LIVE</strong> — Real-time from verified sources (Open-Meteo, USGS, etc.)</li>
          <li><strong>SIMULATED</strong> — Model outputs, synthetic terrain, demo fallbacks</li>
          <li><strong>HISTORICAL</strong> — Past observations, verified records</li>
          <li><strong>DEMO</strong> — Placeholder data for UI development</li>
        </ul>
        <p className="disclaimer-note">
          Demo data is marked "DEMO DATA". The risk number comes only from the backend engine, 
          never the LLM or frontend. If no real model exists, "Demonstration mode" is shown.
        </p>
      </section>

      <section className="panel about-section">
        <h2>Privacy & Offline</h2>
        <ul className="honesty-list">
          <li>No secrets in frontend code. Uses <code>VITE_API_URL</code> (default <code>/api/v1</code>)</li>
          <li>LocalStorage for saved places, settings, emergency alerts (offline sync)</li>
          <li>No tracking, analytics, or third-party scripts</li>
          <li>Offline-first: emergency alerts queue locally and sync when online</li>
        </ul>
      </section>

      <section className="panel about-section">
        <h2>Tech Stack</h2>
        <div className="tech-grid">
          <TechBadge>Vite + React 19</TechBadge>
          <TechBadge>Tailwind CSS 4</TechBadge>
          <TechBadge>React Router 7</TechBadge>
          <TechBadge>MapLibre GL</TechBadge>
          <TechBadge>Recharts</TechBadge>
          <TechBadge>Framer Motion</TechBadge>
          <TechBadge>FastAPI (Python)</TechBadge>
          <TechBadge>SQLAlchemy + SQLite/Postgres</TechBadge>
          <TechBadge>PostGIS (optional)</TechBadge>
          <TechBadge>Vercel Services</TechBadge>
        </div>
      </section>

      <section className="panel about-section">
        <h2>Links</h2>
        <div className="links-grid">
          <LinkCard 
            icon={<Github />}
            title="Source Code"
            desc="View on GitHub"
            href="https://github.com/gnanesh20may-eng/TerraSafe"
          />
          <LinkCard 
            icon={<BookOpen />}
            title="Documentation"
            desc="API docs at /docs"
            href="/docs"
          />
          <LinkCard 
            icon={<ExternalLink />}
            title="Open-Meteo"
            desc="Weather API provider"
            href="https://open-meteo.com/"
          />
          <LinkCard 
            icon={<ExternalLink />}
            title="USGS Earthquakes"
            desc="Earthquake data source"
            href="https://earthquake.usgs.gov/"
          />
        </div>
      </section>

      <footer className="about-footer">
        <p>
          TerraSafe is experimental decision support software.
          Not a replacement for official IMD, NDMA, GSI, or local emergency services.
        </p>
        <p className="version">v0.2.0 · Built with care for communities at risk</p>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, desc }) {
  return (
    <div className="feature-card">
      <div className="feature-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{desc}</p>
    </div>
  )
}

function TechBadge({ children }) {
  return <span className="tech-badge">{children}</span>
}

function LinkCard({ icon, title, desc, href }) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" className="link-card">
      <div className="link-icon">{icon}</div>
      <div>
        <h4>{title}</h4>
        <p>{desc}</p>
      </div>
    </a>
  )
}

export default AboutPage