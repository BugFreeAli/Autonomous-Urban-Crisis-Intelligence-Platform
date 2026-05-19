'use client';

import React from 'react';
import { Shield } from 'lucide-react';
import { useCrisisBackend } from '@/hooks/useCrisisBackend';

export default function MobileHeader({ onMatrixTap }: { onMatrixTap?: () => void }) {
  const { systemNominal, matrixLabel, connected, offlineMode } = useCrisisBackend();

  return (
    <div className="pointer-events-auto w-full px-4 pt-[max(44px,env(safe-area-inset-top))]">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded border border-[#4fd1c5]/60 bg-[#4fd1c5]/10 shadow-[0_0_10px_rgba(79,209,197,0.35)]">
            <Shield size={18} className="text-[#4fd1c5]" fill="rgba(79,209,197,0.2)" />
          </div>
          <div>
            <h1 className="font-display text-base font-normal leading-tight tracking-wide text-white">
              URBAN CRISIS
              <br />
              INTELLIGENCE
            </h1>
            <p className="mt-1 font-tech text-[10px] text-[#4fd1c5]">
              System Status: {connected ? systemNominal : 'Offline'}
            </p>
          </div>
        </div>
        <button type="button" onClick={onMatrixTap} className="text-right shrink-0">
          <p className="font-display text-[9px] uppercase tracking-widest text-[#a0aec0]">
            Crisis Threat Matrix
          </p>
          <p className="mt-0.5 font-tech text-sm font-bold text-[#4fd1c5] glow-teal">{matrixLabel}</p>
        </button>
      </div>
      {offlineMode ? (
        <div className="mt-2 pointer-events-auto rounded border border-yellow-500/40 bg-yellow-500/10 px-2 py-1">
          <p className="font-tech text-[10px] text-yellow-300">
            Backend is not connected. Map is visible, but live city data is not available.
          </p>
        </div>
      ) : null}
    </div>
  );
}
