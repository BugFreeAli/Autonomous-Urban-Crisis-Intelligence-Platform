import type { AiConfig, GlobalState, SystemStatus, TraceRecord } from './types';

/** Strip paths/query so pasted status URLs still work (host:port only). */
export function normalizeBaseUrl(input: string): string {
  const raw = input.trim();
  if (!raw) return '';
  let url = raw.replace(/\/$/, '');
  if (!/^https?:\/\//i.test(url)) url = `http://${url}`;
  try {
    const parsed = new URL(url);
    return parsed.origin;
  } catch {
    return url.replace(/\/$/, '');
  }
}

export async function checkBackendReachable(
  input: string
): Promise<{ ok: true; baseUrl: string } | { ok: false; error: string }> {
  const baseUrl = normalizeBaseUrl(input);
  if (!baseUrl) {
    return { ok: false, error: 'Enter your PC IP and port (example: 192.168.100.120:8000)' };
  }
  try {
    await api.getSystemStatus(baseUrl);
    return { ok: true, baseUrl };
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Could not reach server';
    return { ok: false, error: message };
  }
}

export function toWebSocketUrl(httpBase: string): string {
  const u = new URL(httpBase);
  u.protocol = u.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${u.origin}/ws/stream`;
}

async function request<T>(baseUrl: string, path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${baseUrl}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  });
  if (!res.ok) throw new Error(`${path} failed: ${res.status}`);
  return res.json() as Promise<T>;
}

export const api = {
  getSystemStatus: (base: string) => request<SystemStatus>(base, '/api/system/status'),

  getState: (base: string) => request<GlobalState>(base, '/state'),

  getIncidents: (base: string) =>
    request<Record<string, import('./types').Incident>>(base, '/state/incidents'),

  getResources: (base: string) =>
    request<Record<string, import('./types').Resource>>(base, '/state/resources'),

  getTimeline: (base: string) => request<GlobalState[]>(base, '/state/timeline'),

  getTraces: (base: string) => request<TraceRecord[]>(base, '/traces'),

  getOperations: (base: string) => request<TraceRecord[]>(base, '/operations'),

  getAiConfig: (base: string) => request<AiConfig>(base, '/config/ai'),

  post: (base: string, path: string) =>
    request<{ status: string }>(base, path, { method: 'POST' }),

  emitRainfall: (base: string) => api.post(base, '/test/emit_rainfall'),

  triggerSimultaneousCrises: (base: string) =>
    api.post(base, '/simulation/scenarios/simultaneous_crises'),

  triggerContradictoryReports: (base: string) =>
    api.post(base, '/simulation/scenarios/contradictory_reports'),

  triggerHospitalOverload: (base: string) =>
    api.post(base, '/simulation/scenarios/hospital_overload'),

  triggerEvacuationSpiral: (base: string) =>
    api.post(base, '/simulation/scenarios/evacuation_spiral'),

  triggerResourceExhaustion: (base: string) =>
    api.post(base, '/simulation/scenarios/resource_exhaustion'),

  triggerFlood: (base: string) => api.post(base, '/simulation/scenario/flood'),

  pauseClock: (base: string) => api.post(base, '/simulation/clock/pause'),

  resumeClock: (base: string) => api.post(base, '/simulation/clock/resume'),

  setClockSpeed: (base: string, scale: number) =>
    request<{ status: string; scale: number }>(
      base,
      `/simulation/clock/speed?scale=${encodeURIComponent(scale)}`,
      { method: 'POST' }
    ),
};
