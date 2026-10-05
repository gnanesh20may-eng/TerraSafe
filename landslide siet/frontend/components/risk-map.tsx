'use client';

import { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

type Coordinates = [number, number];
type SafeZone = { id: string; name: string; latitude: number; longitude: number; type?: string };
const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const styleUrl = 'https://demotiles.maplibre.org/style.json';

export function RiskMap({
  center,
  selectedName,
  showRiskZones = true,
  showShelters = true,
}: {
  center: Coordinates;
  selectedName: string;
  showRiskZones?: boolean;
  showShelters?: boolean;
}) {
  const mapContainer = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markerRef = useRef<maplibregl.Marker | null>(null);
  const shelterMarkers = useRef<maplibregl.Marker[]>([]);
  const latestSelection = useRef({ center, selectedName });
  const [mapLoaded, setMapLoaded] = useState(false);
  const [overlayStatus, setOverlayStatus] = useState<'loading' | 'ready' | 'unavailable'>('loading');

  latestSelection.current = { center, selectedName };

  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;
    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: styleUrl,
      center: latestSelection.current.center,
      zoom: 10,
      pitch: 25,
      bearing: 0,
      attributionControl: {},
      cooperativeGestures: true,
    });
    mapRef.current = map;
    map.addControl(new maplibregl.NavigationControl({ showCompass: true, showZoom: true }), 'top-right');
    map.on('load', () => {
      const popupContent = document.createElement('span');
      popupContent.textContent = latestSelection.current.selectedName;
      markerRef.current = new maplibregl.Marker({ color: '#b42318' })
        .setLngLat(latestSelection.current.center)
        .setPopup(new maplibregl.Popup({ offset: 20 }).setDOMContent(popupContent))
        .addTo(map);
      map.addSource('risk-zones', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });
      map.addLayer({
        id: 'risk-zones-fill', type: 'fill', source: 'risk-zones',
        paint: {
          'fill-color': ['match', ['get', 'zone'], 'CRITICAL', '#b42318', 'HIGH', '#c2410c', 'WATCH', '#a16207', '#15803d'],
          'fill-opacity': 0.22,
        },
      });
      map.addLayer({ id: 'risk-zones-outline', type: 'line', source: 'risk-zones', paint: { 'line-color': '#334155', 'line-width': 1.5 } });
      setMapLoaded(true);
    });
    const resizeObserver = new ResizeObserver(() => map.resize());
    resizeObserver.observe(mapContainer.current);
    return () => {
      resizeObserver.disconnect();
      shelterMarkers.current.forEach((marker) => marker.remove());
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    map.flyTo({ center, zoom: 10, essential: true });
    if (markerRef.current) {
      const popupContent = document.createElement('span');
      popupContent.textContent = selectedName;
      markerRef.current.setLngLat(center).setPopup(new maplibregl.Popup({ offset: 20 }).setDOMContent(popupContent));
    }
  }, [center, selectedName]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;
    const source = map.getSource('risk-zones') as maplibregl.GeoJSONSource | undefined;
    if (!source) return;
    const controller = new AbortController();
    setOverlayStatus('loading');
    fetch(`${API_BASE}/api/v1/map/risk-zones`, { cache: 'no-store', signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) throw new Error(`Risk zones returned HTTP ${response.status}`);
        return response.json();
      })
      .then((geojson) => {
        source.setData(geojson);
        setOverlayStatus('ready');
      })
      .catch(() => {
        if (!controller.signal.aborted) setOverlayStatus('unavailable');
      });
    return () => controller.abort();
  }, [mapLoaded]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;
    if (map.getLayer('risk-zones-fill')) map.setLayoutProperty('risk-zones-fill', 'visibility', showRiskZones ? 'visible' : 'none');
    if (map.getLayer('risk-zones-outline')) map.setLayoutProperty('risk-zones-outline', 'visibility', showRiskZones ? 'visible' : 'none');
  }, [mapLoaded, showRiskZones]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;
    const controller = new AbortController();
    fetch(`${API_BASE}/api/v1/safe-zones`, { cache: 'no-store', signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) throw new Error('Safe-zone data unavailable');
        return response.json();
      })
      .then((payload) => {
        shelterMarkers.current.forEach((marker) => marker.remove());
        shelterMarkers.current = (payload.results as SafeZone[]).map((zone) => {
          const element = document.createElement('button');
          element.type = 'button';
          element.className = 'shelter-marker';
          element.setAttribute('aria-label', `DEMO safe zone: ${zone.name}`);
          element.title = `DEMO: ${zone.name}`;
          element.textContent = 'S';
          const content = document.createElement('div');
          const label = document.createElement('strong');
          label.textContent = zone.name;
          const status = document.createElement('span');
          status.textContent = ' · DEMO LOCATION';
          content.append(label, status);
          return new maplibregl.Marker({ element, anchor: 'bottom' })
            .setLngLat([zone.longitude, zone.latitude])
            .setPopup(new maplibregl.Popup({ offset: 20 }).setDOMContent(content))
            .addTo(map);
        });
        shelterMarkers.current.forEach((marker) => marker.getElement().classList.toggle('is-hidden', !showShelters));
      })
      .catch(() => undefined);
    return () => controller.abort();
  }, [mapLoaded]);

  useEffect(() => {
    shelterMarkers.current.forEach((marker) => marker.getElement().classList.toggle('is-hidden', !showShelters));
  }, [showShelters, mapLoaded]);

  return (
    <div className="relative">
      <div ref={mapContainer} className="h-[320px] w-full bg-slate-100 sm:h-[430px]" role="application" aria-label="Interactive map. Use mouse or touch to pan and zoom; map controls support zoom and compass." />
      <div className="pointer-events-none absolute bottom-3 left-3 border border-slate-300 bg-white/95 px-2 py-1 text-[11px] font-semibold text-slate-800">
        {overlayStatus === 'ready' ? 'Risk overlay · DEMO GIS' : overlayStatus === 'loading' ? 'Risk overlay · loading' : 'Risk overlay · unavailable'}
      </div>
    </div>
  );
}
