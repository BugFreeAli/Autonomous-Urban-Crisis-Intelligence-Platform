'use client';

import React, { useState } from 'react';
import { useCrisisBackend } from '@/hooks/useCrisisBackend';
import { api } from '@/lib/api';

export default function DiagnosticsSheet({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const { baseUrl, runDiagnostic, offlineMode } = useCrisisBackend();
  const [msg, setMsg] = useState('');

  if (!open) return null;

  const actions: { label: string; run: () => Promise<string> }[] = [
    { label: 'Hospital Overload', run: () => runDiagnostic('hospital_overload') },
    { label: 'Flood Scenario', run: () => runDiagnostic('flood') },
    { label: 'Emit Rainfall Test', run: () => runDiagnostic('rainfall') },
    { label: 'Pause Simulation', run: () => runDiagnostic('pause') },
    { label: 'Resume Simulation', run: () => runDiagnostic('resume') },
    { label: 'Clock 60x Speed', run: () => runDiagnostic('speed_fast') },
    {
      label: 'Fetch Timeline',
      run: async () => {
        const t = await api.getTimeline(baseUrl);
        return `Timeline snapshots: ${t.length}`;
      },
    },
    {
      label: 'Fetch Incidents Only',
      run: async () => {
        const i = await api.getIncidents(baseUrl);
        return `Incidents: ${Object.keys(i).length}`;
      },
    },
    {
      label: 'Fetch Resources Only',
      run: async () => {
        const r = await api.getResources(baseUrl);
        return `Resources: ${Object.keys(r).length}`;
      },
    },
    {
      label: 'Fetch Operations Log',
      run: async () => {
        const o = await api.getOperations(baseUrl);
        return `Operational outcomes: ${o.length}`;
      },
    },
  ];

  return (
    <div className="fixed inset-0 z-[200] flex items-end justify-center bg-black/70 p-4">
      <div className="w-full max-w-md rounded-xl border border-[#4fd1c5]/30 bg-[#111] p-4">
<div className="mb-4 flex items-center justify-between">
          <h3 className="font-display text-sm text-[#4fd1c5]">System Diagnostics</h3>
          <button type="button" onClick={onClose} className="font-tech text-xs text-gray-400">
            Close
          </button>
        </div>
        <p className="mb-3 font-tech text-[10px] text-gray-500">
          Additional API controls (all backend endpoints). Tap Matrix on any screen to open.
        </p>
        {offlineMode ? (
          <p className="mb-3 rounded border border-yellow-500/40 bg-yellow-500/10 p-2 font-tech text-[10px] text-yellow-300">
            Backend is not connected. Diagnostics are disabled.
          </p>
        ) : null}
        <div className="scroll-panel grid grid-cols-2 gap-2 max-h-[50vh] overflow-y-auto">
          {actions.map((a) => (
            <button
              key={a.label}
              type="button"
              disabled={offlineMode}
              className="rounded border border-[#333] bg-black/50 px-2 py-2 font-tech text-[9px] uppercase text-gray-300 hover:border-[#4fd1c5]"
              onClick={async () => {
                try {
                  const s = await a.run();
                  setMsg(s);
                } catch (e) {
                  setMsg(String(e));
                }
              }}
            >
              {a.label}
            </button>
          ))}
        </div>
        {msg ? <p className="mt-3 font-tech text-[10px] text-[#4fd1c5]">{msg}</p> : null}
      </div>
    </div>
  );
}

