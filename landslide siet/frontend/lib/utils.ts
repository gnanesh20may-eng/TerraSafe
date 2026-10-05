export type RiskLevel = 'LOW' | 'WATCH' | 'HIGH' | 'CRITICAL';

export type LocationOption = {
  id: string;
  name: string;
  region: string;
  latitude: number;
  longitude: number;
  riskLevel: RiskLevel;
  score: number;
};

export const demoLocations: LocationOption[] = [
  { id: 'coonor', name: 'Coonoor', region: 'Nilgiris District', latitude: 11.35, longitude: 76.8, riskLevel: 'HIGH', score: 68 },
  { id: 'ooty', name: 'Ooty', region: 'Nilgiris District', latitude: 11.41, longitude: 76.7, riskLevel: 'WATCH', score: 41 },
  { id: 'kodaikanal', name: 'Kodaikanal', region: 'Dindigul District', latitude: 10.24, longitude: 77.48, riskLevel: 'LOW', score: 18 },
];

export const riskColors: Record<RiskLevel, string> = {
  LOW: '#22c55e',
  WATCH: '#facc15',
  HIGH: '#f97316',
  CRITICAL: '#ef4444',
};

export const getRiskLabel = (score: number): RiskLevel => {
  if (score >= 75) return 'CRITICAL';
  if (score >= 50) return 'HIGH';
  if (score >= 25) return 'WATCH';
  return 'LOW';
};

export function cn(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(' ');
}
