"use client";

import {
  CircleMarker,
  MapContainer,
  Popup,
  Rectangle,
  TileLayer,
} from "react-leaflet";

export type RiskZone = {
  zone_id: string;
  location: string;
  latitude: number;
  longitude: number;
  bounds: [number, number, number, number];
  risk_score: number;
  risk_level: string;
  risk_status: "SIMULATED" | "DEMO" | "LIVE";
  weather_status: "LIVE" | "DEMO" | "MISSING";
  terrain_status: "SIMULATED";
  top_factors: { feature: string; value: number; contribution: number }[];
  why: string;
};

export type ShelterPoint = {
  shelter_id: string;
  name: string;
  latitude: number;
  longitude: number;
  status: "SIMULATED";
};

type RiskMapProps = {
  zones: RiskZone[];
  shelters: ShelterPoint[];
  showHeatmap: boolean;
  showZoneMarkers: boolean;
  showShelters: boolean;
  onSelectZone: (zoneId: string) => void;
};

function riskColor(level: string): string {
  if (level === "Red") return "#ef8175";
  if (level === "Orange") return "#efa960";
  if (level === "Yellow") return "#ddc86c";
  return "#8fba89";
}

export function RiskMap({
  zones,
  shelters,
  showHeatmap,
  showZoneMarkers,
  showShelters,
  onSelectZone,
}: RiskMapProps) {
  return (
    <MapContainer
      className="risk-map"
      center={[11.35, 76.55]}
      zoom={9}
      scrollWheelZoom
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {showHeatmap &&
        zones.map((zone) => {
          const [west, south, east, north] = zone.bounds;
          const color = riskColor(zone.risk_level);
          return (
            <Rectangle
              key={`${zone.zone_id}-heat`}
              bounds={[
                [south, west],
                [north, east],
              ]}
              pathOptions={{
                color,
                weight: 1,
                fillColor: color,
                fillOpacity: 0.32,
              }}
            >
              <Popup>
                {zone.location} · {zone.risk_score.toFixed(3)} · SIMULATED
              </Popup>
            </Rectangle>
          );
        })}
      {showZoneMarkers &&
        zones.map((zone) => (
          <CircleMarker
            key={zone.zone_id}
            center={[zone.latitude, zone.longitude]}
            radius={7}
            pathOptions={{
              color: "#f3f4ef",
              weight: 1,
              fillColor: riskColor(zone.risk_level),
              fillOpacity: 0.95,
            }}
            eventHandlers={{ click: () => onSelectZone(zone.zone_id) }}
          >
            <Popup>
              <strong>{zone.location}</strong>
              <br />
              Score {zone.risk_score.toFixed(3)} · {zone.risk_status}
              <br />
              Synthetic zone geometry; not a warning.
            </Popup>
          </CircleMarker>
        ))}
      {showShelters &&
        shelters.map((shelter) => (
          <CircleMarker
            key={shelter.shelter_id}
            center={[shelter.latitude, shelter.longitude]}
            radius={6}
            pathOptions={{
              color: "#f3f4ef",
              weight: 1,
              fillColor: "#b59ae6",
              fillOpacity: 0.9,
            }}
          >
            <Popup>
              <strong>{shelter.name}</strong>
              <br />
              SIMULATED placeholder only—not an actual shelter or destination.
            </Popup>
          </CircleMarker>
        ))}
    </MapContainer>
  );
}
