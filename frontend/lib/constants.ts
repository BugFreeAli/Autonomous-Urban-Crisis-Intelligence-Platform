/** Map center & district anchors — matches backend embedded dashboard */
export const DISTRICT_COORDS: Record<string, [number, number]> = {
  D1: [32.1617, 74.1883],
  D2: [32.1717, 74.1983],
  D3: [32.1517, 74.1783],
};

export const DISTRICT_LABELS: Record<string, string> = {
  D1: 'Downtown',
  D2: 'Riverside',
  D3: 'Uptown',
  Downtown: 'Downtown',
  Riverside: 'Riverside',
  Uptown: 'Uptown',
};

export const MAP_CENTER: [number, number] = [32.1617, 74.1883];

export function resolveDistrictLabel(location: string): string {
  if (DISTRICT_LABELS[location]) return DISTRICT_LABELS[location];
  return location;
}

export function resolveDistrictCoords(location: string): [number, number] {
  if (DISTRICT_COORDS[location]) return DISTRICT_COORDS[location];
  const key = Object.entries(DISTRICT_LABELS).find(([, name]) => name === location)?.[0];
  if (key && DISTRICT_COORDS[key]) return DISTRICT_COORDS[key];
  return MAP_CENTER;
}

export function threatLabel(confidence: number): string {
  if (confidence > 0.8) return 'CRITICAL';
  if (confidence > 0.4) return 'ELEVATED';
  return 'LOW';
}

export function statusAccent(status: string): 'pink' | 'cyan' | 'red' {
  const s = status.toUpperCase();
  if (s === 'SUSPECTED' || s === 'EMERGING') return 'cyan';
  if (s === 'CONFIRMED' || s === 'ESCALATING') return 'red';
  return 'pink';
}
