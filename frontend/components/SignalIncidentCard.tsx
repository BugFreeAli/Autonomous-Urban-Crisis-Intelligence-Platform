'use client';

import React from 'react';
import { resolveDistrictLabel, statusAccent } from '@/lib/constants';
import type { Incident } from '@/lib/types';

export default function SignalIncidentCard({ incident }: { incident: Incident }) {
  const accent = statusAccent(incident.status);
  const barColor = accent === 'cyan' ? 'bg-[#4fd1c5]' : 'bg-[#f8a5a5]';
  const borderClass =
    accent === 'cyan' ? 'border-l-[#4fd1c5]' : accent === 'red' ? 'border-l-[#e53e3e]' : 'border-l-[#f8a5a5]';
  const statusClass =
    accent === 'cyan' ? 'text-[#4fd1c5]' : accent === 'red' ? 'text-[#e53e3e]' : 'text-[#f8a5a5]';
  const pct = Math.round(incident.severity * 100);

  return (
    <div
      className={`relative overflow-hidden rounded-lg border border-[#333] bg-[#111] p-3 shadow-lg ${borderClass} border-l-4`}
    >
      <div className="mb-2 flex items-center justify-between pl-1">
        <span className={`font-tech text-[10px] uppercase tracking-widest ${statusClass}`}>
          {incident.status.toUpperCase()}
        </span>
        <span className="font-tech text-[10px] text-gray-400">{pct}% SEVERITY</span>
      </div>
      <h3 className="mb-1 pl-1 text-sm font-semibold text-gray-100">{incident.type}</h3>
      <p className="pl-1 font-tech text-[11px] text-gray-500">
        Sector: {resolveDistrictLabel(incident.location)} | Signals: {incident.signals_clustered}
      </p>
      <div className="mt-3 max-w-[60%] pl-1">
        <div className="h-1 w-full overflow-hidden rounded-full bg-[#333]">
          <div className={`h-full ${barColor}`} style={{ width: `${pct}%` }} />
        </div>
      </div>
    </div>
  );
}
