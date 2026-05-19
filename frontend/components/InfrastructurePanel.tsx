'use client';

import React from 'react';
import { Activity } from 'lucide-react';
import { useCrisisBackend } from '@/hooks/useCrisisBackend';

export default function InfrastructurePanel() {
  const { state } = useCrisisBackend();
  const districts = state?.districts ? Object.values(state.districts) : [];

  return (
    <div className="glass-card rounded-xl p-4 shadow-[0_0_30px_rgba(0,0,0,0.5)]">
      <div className="mb-3 flex items-center gap-2">
        <Activity size={14} className="text-[#e53e3e]" />
        <h3 className="font-display text-[11px] font-normal uppercase tracking-widest text-gray-300">
          Infrastructure Capacity Metrics
        </h3>
      </div>
      <div className="grid grid-cols-3 gap-2">
        {districts.length === 0
          ? ['DOWNTOWN', 'RIVERSIDE', 'UPTOWN'].map((name) => (
              <DistrictCell key={name} name={name} pct={10} />
            ))
          : districts.map((d) => (
              <DistrictCell
                key={d.district_id}
                name={d.name.toUpperCase()}
                pct={Math.round((d.traffic_density + d.infrastructure_stress) * 50)}
              />
            ))}
      </div>
    </div>
  );
}

function DistrictCell({ name, pct }: { name: string; pct: number }) {
  return (
    <div className="flex flex-col items-center rounded-lg border border-[#222] bg-black/40 p-3">
      <span className="mb-2 font-tech text-[9px] tracking-tight text-gray-500">{name}</span>
      <span className="font-tech text-lg font-bold text-[#4fd1c5] glow-teal">{pct}%</span>
    </div>
  );
}
