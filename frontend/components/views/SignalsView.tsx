'use client';

import React, { useState } from 'react';
import { Radio, Play } from 'lucide-react';
import { useCrisisBackend } from '@/hooks/useCrisisBackend';
import StatusBar from '@/components/StatusBar';
import SignalIncidentCard from '@/components/SignalIncidentCard';
import DiagnosticsSheet from '@/components/DiagnosticsSheet';
import type { ScenarioKey } from '@/hooks/useCrisisBackend';

export default function SignalsView() {
  const { state, runScenario, offlineMode } = useCrisisBackend();
  const [diagOpen, setDiagOpen] = React.useState(false);
  const [loading, setLoading] = useState<string | null>(null);
  const [toast, setToast] = useState('');

  const incidents = state?.active_incidents
    ? Object.values(state.active_incidents)
        .filter((i) => !['Resolved', 'Retracted'].includes(i.status))
        .sort((a, b) => b.severity - a.severity)
    : [];

  const trigger = async (key: ScenarioKey) => {
    setLoading(key);
    try {
      const s = await runScenario(key);
      setToast(s);
    } catch (e) {
      setToast(String(e));
    } finally {
      setLoading(null);
      setTimeout(() => setToast(''), 4000);
    }
  };

  return (
    <div className="flex h-full flex-col bg-[#050708] text-white">
      <StatusBar onMatrixTap={() => setDiagOpen(true)} />

      <div className="glass-card mx-0 flex flex-1 flex-col overflow-hidden rounded-none border-x-0">
        <div className="flex items-center justify-between border-b border-t border-[#4fd1c5]/30 bg-[#4fd1c5]/5 px-4 py-3">
          <h2 className="flex items-center gap-2 font-tech text-xs font-bold uppercase tracking-widest text-[#4fd1c5]">
            <Radio size={14} />
            Live Signal Feed
          </h2>
          <span className="rounded bg-[#4fd1c5]/20 px-2 py-0.5 font-tech text-[10px] text-[#4fd1c5]">
            {incidents.length} ACTIVE
          </span>
        </div>
        <div className="scroll-panel flex-1 space-y-3 overflow-y-auto px-4 py-4">
          {incidents.length === 0 ? (
            <p className="py-8 text-center font-tech text-xs text-gray-500">Awaiting sensor signals...</p>
          ) : (
            incidents.map((inc) => <SignalIncidentCard key={inc.incident_id} incident={inc} />)
          )}
        </div>
      </div>

      <div className="px-4 pb-6 pt-2">
        <h3 className="mb-3 flex items-center gap-2 font-display text-[10px] uppercase tracking-widest text-gray-400">
          <Play size={12} /> Manual Scenario Stress Control
        </h3>
        <div className="grid grid-cols-2 gap-3">
          <ScenarioBtn
            label={<>SIMULTANEOUS<br />CRISES</>}
            className="border-[#4fd1c5]/40 bg-[#4fd1c5]/5 text-[#4fd1c5]"
            loading={loading === 'simultaneous'}
            disabled={offlineMode}
            onClick={() => trigger('simultaneous')}
          />
          <ScenarioBtn
            label={<>CONTRADICT<br />UPTOWN</>}
            className="border-[#f8a5a5]/40 bg-[#f8a5a5]/5 text-[#f8a5a5]"
            loading={loading === 'contradict'}
            disabled={offlineMode}
            onClick={() => trigger('contradict')}
          />
          <ScenarioBtn
            label={<>EVACUATION<br />SPIRAL</>}
            className="border-[#e53e3e]/40 bg-[#e53e3e]/10 text-[#e53e3e]"
            loading={loading === 'evacuation'}
            disabled={offlineMode}
            onClick={() => trigger('evacuation')}
          />
          <ScenarioBtn
            label={<>RESOURCE<br />EXHAUSTION</>}
            className="border-[#f8a5a5]/30 bg-[#f8a5a5]/5 text-[#f8a5a5]"
            loading={loading === 'exhaustion'}
            disabled={offlineMode}
            onClick={() => trigger('exhaustion')}
          />
        </div>
        {offlineMode ? (
          <p className="mt-3 text-center font-tech text-[10px] text-yellow-300">
            Backend is not connected. Scenario buttons are disabled.
          </p>
        ) : null}
        {toast ? (
          <p className="mt-3 text-center font-tech text-[10px] text-[#4fd1c5]">{toast}</p>
        ) : null}
      </div>
      <DiagnosticsSheet open={diagOpen} onClose={() => setDiagOpen(false)} />
    </div>
  );
}

function ScenarioBtn({
  label,
  className,
  loading,
  disabled = false,
  onClick,
}: {
  label: React.ReactNode;
  className: string;
  loading: boolean;
  disabled?: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      disabled={loading || disabled}
      onClick={onClick}
      className={`flex items-center justify-center rounded-sm border p-4 text-center font-tech text-[10px] font-bold leading-relaxed tracking-widest ${className} disabled:opacity-50`}
    >
      {loading ? '...' : label}
    </button>
  );
}

