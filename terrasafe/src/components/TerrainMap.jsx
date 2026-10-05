import { useEffect, useRef, useState } from 'react'
import { Map as MapLibreMap, Marker, NavigationControl, setWorkerUrl } from 'maplibre-gl'
import mapWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url'
import { Check, Layers, LocateFixed, Rotate3D, X } from 'lucide-react'
import 'maplibre-gl/dist/maplibre-gl.css'
import { areas } from '../data/mockData.js'

const maptilerKey = import.meta.env.VITE_MAPTILER_KEY
setWorkerUrl(mapWorkerUrl)

function makeStyle(satellite = false) {
  if (maptilerKey) return `https://api.maptiler.com/maps/${satellite ? 'satellite' : 'landscape'}/style.json?key=${maptilerKey}`
  return {
    version: 8,
    sources: {
      osm: {
        type: 'raster',
        tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
        tileSize: 256,
        attribution: '&copy; OpenStreetMap contributors',
      },
    },
    layers: [{ id: 'osm', type: 'raster', source: 'osm', paint: { 'raster-saturation': -0.25, 'raster-brightness-max': 0.95 } }],
  }
}

export default function TerrainMap({ area, risk = 'watch', layer = 'Flood', rescue = false, guide = false, terrain3d = true, satellite = false, onAreaSelect }) {
  const mapNode = useRef(null)
  const map = useRef(null)
  const marker = useRef(null)
  const [is3d, setIs3d] = useState(terrain3d)
  const [styleOpen, setStyleOpen] = useState(false)
  const [mapError, setMapError] = useState(false)
  const [droppedArea, setDroppedArea] = useState(null)
  const currentProps = useRef({ area, risk, is3d, satellite, onAreaSelect })

  useEffect(() => {
    currentProps.current = { area, risk, is3d, satellite, onAreaSelect }
  }, [area, risk, is3d, satellite, onAreaSelect])

  useEffect(() => {
    if (!mapNode.current || map.current) return
    const { area: initialArea, is3d: initial3d, satellite: initialSatellite } = currentProps.current
    const center = initialArea.center || [76.9558, 11.0168]
    const instance = new MapLibreMap({
      container: mapNode.current,
      style: makeStyle(initialSatellite),
      center,
      zoom: 11.6,
      pitch: initial3d ? 42 : 0,
      bearing: -18,
      attributionControl: true,
      cooperativeGestures: true,
    })
    map.current = instance
    instance.addControl(new NavigationControl({ showCompass: false }), 'bottom-right')
    instance.on('load', () => {
      const el = document.createElement('div')
      el.className = `map-marker map-marker-${currentProps.current.risk}`
      el.setAttribute('aria-label', `${currentProps.current.area.name} selected location`)
      el.innerHTML = '<span></span>'
      marker.current = new Marker({ element: el, anchor: 'center', draggable: Boolean(currentProps.current.onAreaSelect) }).setLngLat(center).addTo(instance)
      if (currentProps.current.onAreaSelect) {
        instance.on('click', (event) => {
          const pin = event.lngLat
          const nearest = areas.reduce((closest, candidate) => {
            const distance = (candidate.center[0] - pin.lng) ** 2 + (candidate.center[1] - pin.lat) ** 2
            return distance < closest.distance ? { area: candidate, distance } : closest
          }, { area: areas[0], distance: Infinity }).area
          marker.current.setLngLat(pin)
          setDroppedArea(nearest)
        })
        marker.current.on('dragend', () => {
          const pin = marker.current.getLngLat()
          const nearest = areas.reduce((closest, candidate) => {
            const distance = (candidate.center[0] - pin.lng) ** 2 + (candidate.center[1] - pin.lat) ** 2
            return distance < closest.distance ? { area: candidate, distance } : closest
          }, { area: areas[0], distance: Infinity }).area
          setDroppedArea(nearest)
        })
      }
      if (maptilerKey && currentProps.current.is3d) {
        instance.addSource('terrain-dem', { type: 'raster-dem', url: `https://api.maptiler.com/tiles/terrain-rgb/tiles.json?key=${maptilerKey}`, tileSize: 256 })
        instance.setTerrain({ source: 'terrain-dem', exaggeration: 1.15 })
      }
    })
    instance.on('error', (event) => {
      if (event?.error?.message?.includes('Failed to fetch')) setMapError(true)
    })
    return () => { instance.remove(); map.current = null; marker.current = null }
  }, [])

  useEffect(() => {
    if (!map.current || !satellite || maptilerKey) return
    window.dispatchEvent(new CustomEvent('terrasafe-toast', { detail: 'Add a MapTiler key to enable satellite imagery.' }))
  }, [satellite])

  useEffect(() => {
    if (!map.current || !maptilerKey || !map.current.isStyleLoaded()) return
    map.current.setStyle(makeStyle(satellite))
  }, [satellite])

  useEffect(() => {
    if (!map.current || !area.center) return
    map.current.flyTo({ center: area.center, zoom: 11.6, duration: 1000 })
    marker.current?.setLngLat(area.center)
  }, [area])

  useEffect(() => {
    if (marker.current) marker.current.getElement().className = `map-marker map-marker-${risk}`
  }, [risk])

  const toggleTerrain = () => {
    const next = !is3d
    setIs3d(next)
    map.current?.easeTo({ pitch: next ? 42 : 0, duration: 600 })
    if (next && maptilerKey && map.current && map.current.isStyleLoaded() && !map.current.getSource('terrain-dem')) {
      map.current.addSource('terrain-dem', { type: 'raster-dem', url: `https://api.maptiler.com/tiles/terrain-rgb/tiles.json?key=${maptilerKey}`, tileSize: 256 })
      map.current.setTerrain({ source: 'terrain-dem', exaggeration: 1.15 })
    }
    if (!next && map.current?.getTerrain()) map.current.setTerrain(null)
  }

  const confirmArea = () => {
    if (!droppedArea) return
    onAreaSelect?.(droppedArea)
    setDroppedArea(null)
  }

  const cancelArea = () => {
    marker.current?.setLngLat(area.center)
    setDroppedArea(null)
  }

  return <div className={`terrain-map ${rescue ? 'rescue-map' : ''} map-layer-${layer.toLowerCase()} ${guide ? 'guide-active' : ''}`}>
    <div className="map-canvas" ref={mapNode} aria-label={`Interactive map around ${area.name}`} />
    {mapError && <div className="map-error"><LocateFixed size={16} /> Map tiles are unavailable. Check your connection.</div>}
    <div className="map-search-overlay"><span><LocateFixed size={15} /></span><strong>{area.name}</strong><small>{rescue ? 'Local area' : 'Selected area'}</small></div>
    {onAreaSelect && <div className="pin-hint">Drag the pin to check a nearby area</div>}
    {droppedArea && <div className="pin-confirm"><span><LocateFixed size={15} /></span><div><small>SELECTED AREA</small><strong>{droppedArea.name}</strong></div><button aria-label="Confirm selected area" onClick={confirmArea}><Check size={16} /></button><button aria-label="Cancel pin change" onClick={cancelArea}><X size={16} /></button></div>}
    <div className="map-controls-overlay"><button aria-label="Center map on selected area" title="Center map" onClick={() => map.current?.flyTo({ center: area.center, zoom: 11.6, duration: 600 })}><LocateFixed size={16} /></button><button aria-label="Toggle 3D terrain" title="Toggle 3D terrain" className={is3d ? 'control-selected' : ''} onClick={toggleTerrain}><Rotate3D size={16} /></button><button aria-label="Map layers" title="Map layers" className={styleOpen ? 'control-selected' : ''} onClick={() => setStyleOpen(!styleOpen)}><Layers size={16} /></button></div>
    {styleOpen && <div className="map-style-menu"><strong>Map style</strong><button onClick={() => { setStyleOpen(false); if (satellite) window.dispatchEvent(new CustomEvent('terrasafe-toast', { detail: 'Change the map preference in Settings to use street view.' })) }}><MapIconFallback /> Street map {!satellite && <CheckMark />}</button><button onClick={() => { setStyleOpen(false); if (!maptilerKey) window.dispatchEvent(new CustomEvent('terrasafe-toast', { detail: 'Add a MapTiler key to enable satellite imagery.' })) }}>Satellite imagery {satellite && maptilerKey ? <CheckMark /> : !maptilerKey && <small>Key needed</small>}</button></div>}
    {rescue && <div className="map-safe-zone"><span><span className="safe-zone-pulse" /></span><strong>Community Relief Centre</strong><small>Suggested safe zone</small></div>}
    {guide && <svg className="route-overlay" viewBox="0 0 600 300" preserveAspectRatio="none" aria-hidden="true"><path className="route-outline" d="M500 75 C420 110 450 165 340 160 S225 110 170 155 S100 190 75 250" /><path className="route-line" d="M500 75 C420 110 450 165 340 160 S225 110 170 155 S100 190 75 250" /></svg>}
    <div className="map-layer-caption"><span className="layer-caption-dot" />{layer} outlook <small>Illustrative</small></div>
    {!maptilerKey && <div className="map-attribution-note">MapTiler terrain available with a key</div>}
  </div>
}

function MapIconFallback() { return <span aria-hidden="true">◫</span> }
function CheckMark() { return <span aria-hidden="true">✓</span> }