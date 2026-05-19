'use client';

import React, { useState } from 'react';
import { Shield, Truck } from 'lucide-react';
import { useCrisisBackend } from '@/hooks/useCrisisBackend';
import StatusBar from '@/components/StatusBar';
import DiagnosticsSheet from '@/components/DiagnosticsSheet';

export default function ResourcesView() {
  const { state, offlineMode } = useCrisisBackend();
  const [diagOpen, setDiagOpen] = useState(false);

  const hospitals = state?.hospitals ? Object.values(state.hospitals) : [];
  const resources = state?.resources ? Object.values(state.resources) : [];


  return (
    <div className="scroll-panel flex h-full flex-col overflow-y-auto bg-[#050708] pb-24 text-white">
      <StatusBar onMatrixTap={() => setDiagOpen(true)} />
      {offlineMode ? (
        <div className="mx-4 mt-3 rounded border border-yellow-500/40 bg-yellow-500/10 px-3 py-2">
          <p className="font-tech text-[10px] text-yellow-300">
            Backend is not connected. Resource values below are not live.
          </p>
        </div>
      ) : null}

      <div className="mx-4 mt-4 rounded-lg border border-[#333] bg-[#111] p-4">
        <h3 className="mb-6 border-b border-[#333] pb-2 font-display text-[10px] uppercase tracking-widest text-gray-400">
          Hospital Surge Patient Load
        </h3>
        <div className="space-y-5">
          {hospitals.map((h) => {
            const pct = Math.round((h.current_load / h.capacity) * 100);
            return (
              <div key={h.hospital_id}>
                <div className="mb-2 flex items-end justify-between">
                  <span className="text-sm font-semibold">{h.name}</span>
                  <span className="font-tech text-[11px] text-gray-400">
                    {h.current_load} / {h.capacity} ({pct}%)
                  </span>
                </div>
                <div className="h-1.5 w-full overflow-hidden rounded-full bg-[#222]">
                  <div className="h-full bg-[#f8a5a5]/80" style={{ width: `${pct}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mx-4 mt-6 mb-6">
        <h3 className="mb-3 flex items-center gap-2 font-display text-[10px] uppercase tracking-widest text-gray-400">
          <Shield size={12} /> Active Emergency Resources
        </h3>
        <div className="scroll-panel space-y-3">
          {resources.map((res) => (
            <div
              key={res.resource_id}
              className="flex items-center gap-4 rounded-lg border border-[#333] bg-[#111] p-3"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded bg-[#222] text-[#4fd1c5]">
                <Truck size={20} />
              </div>
              <div className="flex flex-1 flex-col">
                <span className="font-tech text-[11px] text-gray-300">
                  {res.resource_id} // {res.type}
                </span>
                <span
                  className={`text-[12px] font-bold ${
                    res.status === 'Available' ? 'text-[#00ff41]' : 'text-[#f8a5a5]'
                  }`}
                >
                  {res.status}
                </span>
              </div>
              <div className="flex flex-col items-end text-right">
                <span className="font-tech text-[9px] tracking-widest text-gray-500">ETA</span>
                <span className="font-tech text-xs text-gray-300">{res.eta_seconds ?? 0}s</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <DiagnosticsSheet open={diagOpen} onClose={() => setDiagOpen(false)} />
    </div>
  );
}
