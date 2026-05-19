'use client';

import React from 'react';
import { Shield } from 'lucide-react';
import { useCrisisBackend } from '@/hooks/useCrisisBackend';

export default function StatusBar({
  showNeuralLink = false,
  onMatrixTap,
}: {
  showNeuralLink?: boolean;
  onMatrixTap?: () => void;
}) {
  const { systemNominal, matrixLabel, connected, latencyMs, offlineMode } = useCrisisBackend();
  const matrixShort = matrixLabel.split(' ')[0] ?? '0.00';

  return (
    <div className="w-full border-b border-[#2a2a2a] bg-[#0a0c0d]/90 px-4 pt-[max(12px,env(safe-area-inset-top))] pb-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Shield size={16} className="text-[#4fd1c5]" strokeWidth={1.5} />
          <span className="font-display text-sm text-white">
            System Status:{' '}
            <span className="text-[#4fd1c5]">{connected ? systemNominal : 'Offline'}</span>
          </span>
        </div>
        <button type="button" onClick={onMatrixTap} className="font-tech text-xs text-[#a0aec0]">
          Matrix: <span className="text-white">{matrixShort}</span>
        </button>
      </div>
      {showNeuralLink ? (
        <div className="mt-2 flex items-center justify-between border-t border-[#222] pt-2">
          <div className="flex items-center gap-2">
            <span
              className={`h-2 w-2 rounded-full ${connected ? 'bg-[#00ff41] animate-pulse' : 'bg-red-500'}`}
            />
            <span className="font-tech text-[10px] uppercase tracking-widest text-[#00ff41]">
              Neural Link: {connected ? 'Stable' : 'Disconnected'}
            </span>
          </div>
          <span className="font-tech text-[10px] text-[#a0aec0]">Latency: {latencyMs}ms</span>
        </div>
      ) : null}
      {offlineMode ? (
        <div className="mt-2 rounded border border-yellow-500/40 bg-yellow-500/10 px-2 py-1">
          <p className="font-tech text-[10px] text-yellow-300">
            Backend is not connected. You can explore UI only. Live simulation is disabled.
          </p>
        </div>
      ) : null}
    </div>
  );
}
