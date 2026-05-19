export interface DistrictState {
  district_id: string;
  name: string;
  population: number;
  vulnerability_index: number;
  traffic_density: number;
  infrastructure_stress: number;
  weather_severity: number;
}

export interface HospitalState {
  hospital_id: string;
  name: string;
  district_id: string;
  capacity: number;
  current_load: number;
  surge_probability: number;
}

export interface Incident {
  incident_id: string;
  type: string;
  severity: number;
  location: string;
  reported_at: string;
  status: string;
  confidence_score: number;
  radius_meters: number;
  signals_clustered: number;
  contradiction_flag: boolean;
  prediction_tags: string[];
}

export interface Resource {
  resource_id: string;
  type: string;
  capacity: number;
  status: string;
  target_location?: string | null;
  location?: string | null;
  eta_seconds?: number | null;
}

export interface GlobalState {
  timestamp: string;
  active_incidents: Record<string, Incident>;
  resources: Record<string, Resource>;
  districts: Record<string, DistrictState>;
  hospitals: Record<string, HospitalState>;
  crisis_confidence: number;
  simulation_mode: boolean;
}

export interface TraceRecord {
  trace_id: string;
  timestamp: string;
  agent_name: string;
  action_type: string;
  trigger_event_id?: string | null;
  reasoning: string;
  confidence_score: number;
  trade_offs_considered: string[];
  metadata?: Record<string, unknown>;
}

export interface AiConfig {
  enabled: boolean;
  provider: string;
  status: string;
}

export interface SystemStatus {
  status: string;
  system: string;
  version: string;
}

export interface WsTraceEvent {
  event: 'trace';
  agent: string;
  reasoning: string;
}

export interface WsOperationEvent {
  event: 'operation';
  agent: string;
  headline: string;
  detail: string;
  outcome_type: string;
  confidence: number;
}

export type OutcomeType =
  | 'action'
  | 'detect'
  | 'confirm'
  | 'retract'
  | 'merge'
  | 'escalate'
  | 'classify'
  | 'forecast'
  | 'dispatch'
  | 'comms'
  | 'command';

export interface WsClockEvent {
  event: 'clock_tick';
  sim_time: string;
}

export type TerminalLogLine = {
  id: string;
  kind: 'sys' | 'prompt' | 'detail' | 'agent';
  text: string;
  highlight?: string;
};
