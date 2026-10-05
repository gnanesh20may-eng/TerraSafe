"use client";

import { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

const styleUrl = 'https://demotiles.maplibre.org/style.json';

export function RiskMap({ center, selectedName }: { center: [number, number]; selectedName: string }) {
  const mapContainer = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markerRef = useRef<maplibregl.Marker | null>(null);

  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;

    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: styleUrl,
      center,
      zoom: 10,
      pitch: 35,
      bearing: 0,
      attributionControl: false,
    });

    mapRef.current = map;

    map.on('load', () => {
      new maplibregl.Marker({ color: '#ef4444' })
        .setLngLat(center)
        .setPopup(new maplibregl.Popup({ offset: 20 }).setHTML(`<strong>${selectedName}</strong>`))
        .addTo(map);
    });

    const resizeObserver = new ResizeObserver(() => map.resize());
    resizeObserver.observe(mapContainer.current);

    return () => {
      resizeObserver.disconnect();
      map.remove();
      mapRef.current = null;
    };
  }, [center, selectedName]);

  useEffect(() => {
    if (!mapRef.current) return;
    mapRef.current.flyTo({ center, zoom: 10, essential: true });
    if (markerRef.current) {
      markerRef.current.remove();
    }
    markerRef.current = new maplibregl.Marker({ color: '#ef4444' }).setLngLat(center).addTo(mapRef.current);
  }, [center]);

  return <div ref={mapContainer} className="h-[280px] w-full rounded-2xl border border-slate-200 bg-slate-100" />;
}
