import { CloudRain, MapPin, Mountain, Wind } from 'lucide-react'

export const areas = [
  { name: 'Coimbatore', region: 'Tamil Nadu, India', center: [76.9558, 11.0168], risk: 'watch' },
  { name: 'Ooty', region: 'Tamil Nadu, India', center: [76.695, 11.4064], risk: 'high' },
  { name: 'Mysuru', region: 'Karnataka, India', center: [76.6394, 12.2958], risk: 'low' },
  { name: 'Kochi', region: 'Kerala, India', center: [76.2673, 9.9312], risk: 'watch' },
  { name: 'Chennai', region: 'Tamil Nadu, India', center: [80.2707, 13.0827], risk: 'low' },
]

export const signals = [
  { name: 'Rainfall', value: 'High', change: 'Increasing', changeTone: 'change-up', tone: 'amber', icon: 'rain', spark: [30, 36, 32, 53, 46, 70, 83, 91] },
  { name: 'Soil moisture', value: 'Moderate', change: 'Stable', changeTone: 'change-steady', tone: 'green', icon: 'soil', spark: [46, 52, 49, 57, 54, 59, 55, 61] },
  { name: 'Wind', value: 'Normal', change: 'Stable', changeTone: 'change-steady', tone: 'blue', icon: 'wind', spark: [60, 55, 64, 57, 61, 53, 59, 56] },
  { name: 'Elevation', value: 'Moderate', change: 'Local terrain', changeTone: 'change-neutral', tone: 'stone', icon: 'elevation', spark: [48, 49, 51, 48, 53, 51, 54, 52] },
]

export const safeZones = [
  { name: 'Community Relief Centre', type: 'Community shelter', minutes: 8, status: 'Open' },
  { name: 'Township Higher Secondary School', type: 'Designated assembly point', minutes: 14, status: 'Check locally' },
]

export const timelineData = [
  { label: '6h ago', value: 24 },
  { label: '3h ago', value: 34 },
  { label: 'Now', value: 46 },
  { label: 'Next 3h', value: 63 },
  { label: 'Next 6h', value: 69 },
]

export function getAreaRisk(area, scenario = 42) {
  let key = area.risk || 'watch'
  if (scenario >= 76 && key !== 'high') key = 'high'
  else if (scenario < 20 && key === 'watch') key = 'low'
  const risks = {
    low: { key, label: 'Low', percent: '24%', color: '#518767' },
    watch: { key, label: 'Watch', percent: scenario > 64 ? '68%' : '46%', color: '#d59a42' },
    high: { key, label: 'High', percent: '78%', color: '#cc6254' },
  }
  return risks[key]
}

export function getRiskCopy(risk) {
  const copy = {
    low: { title: 'Conditions look manageable.', description: 'No unusual environmental signals are standing out right now.', pulse: 'Environmental conditions are currently stable in your area.' },
    watch: { title: 'A little extra awareness goes a long way.', description: 'Environmental conditions deserve attention, but there is time to stay prepared.', pulse: 'Conditions are mostly steady, with rainfall worth keeping an eye on.' },
    high: { title: 'Stay alert and follow local guidance.', description: 'Several conditions may increase local vulnerability. Keep plans flexible and check official updates.', pulse: 'Conditions may be changing quickly. Keep local advisories close.' },
  }
  return copy[risk.key]
}

export const riskLayerIcons = { rain: CloudRain, terrain: Mountain, wind: Wind, place: MapPin }