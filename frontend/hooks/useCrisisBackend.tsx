'use client';

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { api, toWebSocketUrl } from '@/lib/api';
import type {
  AiConfig,
  GlobalState,
  TerminalLogLine,
  TraceRecord,
  WsClockEvent,
  WsTraceEvent,
  WsOperationEvent,
} from '@/lib/types';
import { threatLabel } from '@/lib/constants';

type CrisisContextValue = {
  baseUrl: string;
  offlineMode: boolean;
  state: GlobalState | null;
  traces: TraceRecord[];
  operations: TraceRecord[];
  terminalLines: TerminalLogLine[];
  aiConfig: AiConfig | null;
  simTime: string | null;
  connected: boolean;
  latencyMs: number;
  systemNominal: string;
  matrixLabel: string;
  clearTerminal: () => void;
  runScenario: (key: ScenarioKey) => Promise<string>;
  runDiagnostic: (key: DiagnosticKey) => Promise<string>;
};

export type ScenarioKey =
  | 'simultaneous'
  | 'contradict'
  | 'evacuation'
  | 'exhaustion';

export type DiagnosticKey =
  | 'hospital_overload'
  | 'flood'
  | 'rainfall'
  | 'pause'
  | 'resume'
  | 'speed_fast';

const CrisisContext = createContext<CrisisContextValue | null>(null);

function shortAgent(name: string): string {
  return name.replace('Agent', '').replace(/([A-Z])/g, ' $1').trim();
}

function traceToLines(t: TraceRecord): TerminalLogLine[] {
  const meta = (t.metadata || {}) as Record<string, string>;
  const isOutcome =
    t.action_type === 'OperationalOutcome' || meta.display_kind === 'outcome';

  if (isOutcome) {
    const headline = meta.headline || t.reasoning.split('\n')[0];
    const rest = t.reasoning.includes('\n') ? t.reasoning.split('\n').slice(1).join('\n').trim() : '';
    const lines: TerminalLogLine[] = [
      { id: `${t.trace_id}-a`, kind: 'sys', text: `[DECISION] ${shortAgent(t.agent_name)}` },
      { id: `${t.trace_id}-h`, kind: 'prompt', text: headline },
    ];
    if (rest) lines.push({ id: `${t.trace_id}-b`, kind: 'detail', text: rest });
    t.trade_offs_considered?.forEach((imp, i) => {
      lines.push({ id: `${t.trace_id}-i-${i}`, kind: 'detail', text: imp });
    });
    return lines;
  }

  return [
    { id: `${t.trace_id}-ag`, kind: 'agent', text: shortAgent(t.agent_name) },
    { id: `${t.trace_id}-r`, kind: 'prompt', text: t.reasoning },
  ];
}

export function CrisisBackendProvider({
  baseUrl,
  children,
}: {
  baseUrl: string;
  children: React.ReactNode;
}) {
  const offlineMode = !baseUrl;
  const [state, setState] = useState<GlobalState | null>(null);
  const [traces, setTraces] = useState<TraceRecord[]>([]);
  const [operations, setOperations] = useState<TraceRecord[]>([]);
  const [terminalLines, setTerminalLines] = useState<TerminalLogLine[]>([
    { id: 'boot-1', kind: 'sys', text: '[SYS] Initializing analysis sequence...' },
    { id: 'boot-2', kind: 'sys', text: '[SYS] Scanning input data...' },
  ]);
  const [aiConfig, setAiConfig] = useState<AiConfig | null>(null);
  const [simTime, setSimTime] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);
  const [latencyMs, setLatencyMs] = useState(12);
  const seenTraceIds = useRef(new Set<string>());
  const wsRef = useRef<WebSocket | null>(null);

  const appendTerminal = useCallback((lines: TerminalLogLine[]) => {
    setTerminalLines((prev) => {
      const next = [...prev, ...lines];
      return next.slice(-120);
    });
  }, []);

  const clearTerminal = useCallback(() => {
    setTerminalLines([
      { id: `clear-${Date.now()}`, kind: 'sys', text: '[SYS] Terminal cleared.' },
    ]);
  }, []);

  useEffect(() => {
    if (!offlineMode) return;
    appendTerminal([
      {
        id: `offline-${Date.now()}`,
        kind: 'sys',
        text: '[SYS] Backend is not connected. Live simulation and actions are disabled.',
      },
    ]);
  }, [offlineMode, appendTerminal]);

  const poll = useCallback(async () => {
    if (offlineMode) {
      setConnected(false);
      return;
    }
    const start = performance.now();
    try {
      const [s, tr, ops, ai] = await Promise.all([
        api.getState(baseUrl),
        api.getTraces(baseUrl),
        api.getOperations(baseUrl),
        api.getAiConfig(baseUrl),
      ]);
      setLatencyMs(Math.round(performance.now() - start));
      setState(s);
      setTraces(tr);
      setOperations(ops);
      setAiConfig(ai);
      setConnected(true);

      tr.forEach((t) => {
        if (!seenTraceIds.current.has(t.trace_id)) {
          seenTraceIds.current.add(t.trace_id);
          appendTerminal(traceToLines(t));
        }
      });
    } catch {
      setConnected(false);
    }
  }, [baseUrl, appendTerminal, offlineMode]);

  useEffect(() => {
    poll();
    const id = setInterval(poll, 1000);
    return () => clearInterval(id);
  }, [poll]);

  useEffect(() => {
    if (offlineMode) {
      return;
    }
    const wsUrl = toWebSocketUrl(baseUrl);
    let cancelled = false;
    let retryTimer: ReturnType<typeof setTimeout>;

    const connect = () => {
      if (cancelled) return;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        appendTerminal([
          { id: `ws-open-${Date.now()}`, kind: 'sys', text: '[SYS] Neural link established.' },
        ]);
      };

      ws.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data) as WsTraceEvent | WsClockEvent | WsOperationEvent;
          if (data.event === 'clock_tick') {
            setSimTime(data.sim_time);
            return;
          }
          if (data.event === 'operation') {
            const id = `ws-op-${Date.now()}`;
            appendTerminal([
              { id: `${id}-sys`, kind: 'sys', text: `[DECISION] ${shortAgent(data.agent)}` },
              { id: `${id}-h`, kind: 'prompt', text: data.headline },
              { id: `${id}-d`, kind: 'detail', text: data.detail },
            ]);
            setOperations((prev) => [
              {
                trace_id: id,
                timestamp: new Date().toISOString(),
                agent_name: data.agent,
                action_type: 'OperationalOutcome',
                reasoning: `${data.headline}\n\n${data.detail}`,
                confidence_score: data.confidence ?? 0.9,
                trade_offs_considered: [],
                metadata: {
                  display_kind: 'outcome',
                  headline: data.headline,
                  outcome_type: data.outcome_type,
                },
              },
              ...prev,
            ].slice(0, 80));
            return;
          }
          if (data.event === 'trace') {
            const id = `ws-${data.agent}-${Date.now()}`;
            appendTerminal([
              { id: `${id}-agent`, kind: 'agent', text: shortAgent(data.agent) },
              { id: `${id}-reason`, kind: 'prompt', text: data.reasoning },
            ]);
          }
        } catch {
          /* ignore */
        }
      };

      ws.onclose = () => {
        if (!cancelled) retryTimer = setTimeout(connect, 3000);
      };
    };

    connect();
    return () => {
      cancelled = true;
      clearTimeout(retryTimer);
      wsRef.current?.close();
    };
  }, [baseUrl, appendTerminal, offlineMode]);

  const runScenario = useCallback(
    async (key: ScenarioKey) => {
      if (offlineMode) {
        throw new Error(
          'Backend is not connected. Connect backend first to run this simulation.'
        );
      }
      const map: Record<ScenarioKey, () => Promise<{ status: string }>> = {
        simultaneous: () => api.triggerSimultaneousCrises(baseUrl),
        contradict: () => api.triggerContradictoryReports(baseUrl),
        evacuation: () => api.triggerEvacuationSpiral(baseUrl),
        exhaustion: () => api.triggerResourceExhaustion(baseUrl),
      };
      const res = await map[key]();
      appendTerminal([
        { id: `sc-${key}`, kind: 'sys', text: `[SYS] ${res.status}` },
      ]);
      await poll();
      return res.status;
    },
    [baseUrl, appendTerminal, poll, offlineMode]
  );

  const runDiagnostic = useCallback(
    async (key: DiagnosticKey) => {
      if (offlineMode) {
        throw new Error(
          'Backend is not connected. Diagnostics cannot run without backend.'
        );
      }
      let res: { status: string };
      switch (key) {
        case 'hospital_overload':
          res = await api.triggerHospitalOverload(baseUrl);
          break;
        case 'flood':
          res = await api.triggerFlood(baseUrl);
          break;
        case 'rainfall':
          res = await api.emitRainfall(baseUrl);
          break;
        case 'pause':
          res = await api.pauseClock(baseUrl);
          break;
        case 'resume':
          res = await api.resumeClock(baseUrl);
          break;
        case 'speed_fast':
          res = await api.setClockSpeed(baseUrl, 60);
          break;
      }
      appendTerminal([{ id: `diag-${key}`, kind: 'sys', text: `[SYS] ${res.status}` }]);
      await poll();
      return res.status;
    },
    [baseUrl, appendTerminal, poll, offlineMode]
  );

  const crisisConfidence = state?.crisis_confidence ?? 0;
  const matrixLabel = `${crisisConfidence.toFixed(2)} (${threatLabel(crisisConfidence)})`;
  const systemNominal = connected
    ? aiConfig?.enabled
      ? 'Nominal 99.9%'
      : 'Nominal 99.9%'
    : 'OFFLINE';

  const value = useMemo(
    () => ({
      baseUrl,
      offlineMode,
      state,
      traces,
      operations,
      terminalLines,
      aiConfig,
      simTime,
      connected,
      latencyMs,
      systemNominal,
      matrixLabel,
      clearTerminal,
      runScenario,
      runDiagnostic,
    }),
    [
      baseUrl,
      offlineMode,
      state,
      traces,
      operations,
      terminalLines,
      aiConfig,
      simTime,
      connected,
      latencyMs,
      systemNominal,
      matrixLabel,
      clearTerminal,
      runScenario,
      runDiagnostic,
    ]
  );

  return <CrisisContext.Provider value={value}>{children}</CrisisContext.Provider>;
}

export function useCrisisBackend() {
  const ctx = useContext(CrisisContext);
  if (!ctx) throw new Error('useCrisisBackend must be used within CrisisBackendProvider');
  return ctx;
}
