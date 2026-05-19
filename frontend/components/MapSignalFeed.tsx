'use client';

import React from 'react';
import { Radio, MapPin } from 'lucide-react';
import { useCrisisBackend } from '@/hooks/useCrisisBackend';
import { resolveDistrictLabel, statusAccent } from '@/lib/constants';
import type { Incident } from '@/lib/types';

function activeIncidents(incidents: Record<string, Incident> | undefined) {
  if (!incidents) return [];
  return Object.values(incidents).filter(
    (i) => !['Resolved', 'Retracted'].includes(i.status)
  );
}

export default function MapSignalFeed() {
  const { state } = useCrisisBackend();
  const list = activeIncidents(state?.active_incidents);
  const top = [...list].sort((a, b) => b.severity - a.severity)[0];

  return (
    <div className="glass-card rounded-xl overflow-hidden">
      <div className="flex items-center justify-between border-b border-[#4fd1c5]/30 bg-[#4fd1c5]/5 px-3 py-2">
        <h2 className="font-tech text-[10px] font-bold uppercase tracking-widest text-[#4fd1c5] flex items-center gap-2">
          <Radio size={12} />
          Live Signal Feed
        </h2>
        <span className="rounded bg-[#4fd1c5]/20 px-2 py-0.5 font-tech text-[10px] text-[#4fd1c5]">
          {list.length} ACTIVE
        </span>
      </div>
      {!top ? (
        <p className="p-6 text-center font-tech text-xs text-gray-500">No active incidents. City is stable.</p>
      ) : (
        <IncidentCard incident={top} />
      )}
    </div>
  );
}

function IncidentCard({ incident }: { incident: Incident }) {
  const accent = statusAccent(incident.status);
  const barColor = accent === 'cyan' ? 'bg-[#4fd1c5]' : 'bg-[#f8a5a5]';
  const borderColor =
    accent === 'red' ? 'border-l-[#e53e3e]' : accent === 'cyan' ? 'border-l-[#4fd1c5]' : 'border-l-[#f8a5a5]';
  const statusColor =
    accent === 'red' ? 'text-[#e53e3e]' : accent === 'cyan' ? 'text-[#4fd1c5]' : 'text-[#f8a5a5]';
  const pct = Math.round(incident.severity * 100);

  return (
    <div className={`relative border-l-4 ${borderColor} bg-[#111] m-3 rounded-lg p-3`}>
      <div className="flex justify-between items-center mb-1">
        <span className={`font-tech text-[10px] uppercase tracking-widest ${statusColor}`}>
          {incident.status.toUpperCase()}
        </span>
        <span className="font-tech text-[10px] text-gray-400">{pct}% SEVERITY</span>
      </div>
      <p className="text-sm font-semibold text-white mb-2">{incident.type}</p>
      <p className="font-tech text-[11px] text-gray-500 flex flex-wrap items-center gap-3">
        <span className="flex items-center gap-1">
          <MapPin size={10} /> Sector: {resolveDistrictLabel(incident.location)}
        </span>
        <span className="flex items-center gap-1">
          <Radio size={10} /> Signals: {incident.signals_clustered}
        </span>
      </p>
      <div className="mt-3 h-1 w-full rounded-full bg-[#333] overflow-hidden">
        <div className={`h-full ${barColor}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}