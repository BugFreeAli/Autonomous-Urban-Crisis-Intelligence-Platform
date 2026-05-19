'use client';

import React from 'react';
import { BrainCircuit } from 'lucide-react';
import { useCrisisBackend } from '@/hooks/useCrisisBackend';

function highlightReasoning(text: string) {
  const parts = text.split(/(MERGE|RETRACT|CONFIRM|ESCALATE)/g);
  return parts.map((part, i) => {
    if (['MERGE', 'RETRACT', 'CONFIRM', 'ESCALATE'].includes(part)) {
      return (
        <span key={i} className="font-bold text-[#4fd1c5]">
          {part}
        </span>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

export default function AgentReasoningPanel({
  compact = false,
  onClear,
}: {
  compact?: boolean;
  onClear?: () => void;
}) {
  const { terminalLines, clearTerminal, traces } = useCrisisBackend();
  const latest =
    terminalLines.filter((l) => l.kind === 'prompt').slice(-1)[0]?.text ||
    traces[traces.length - 1]?.reasoning ||
    'Awaiting autonomous agent decisions...';

  return (
    <div
      className={`glass-card rounded-lg overflow-hidden ${
        compact ? 'mx-4 mb-4' : 'flex-1 mx-4 mb-4 flex flex-col min-h-0'
      }`}
    >
      <div className="flex items-center justify-between border-b border-[#4fd1c5]/25 bg-[#4fd1c5]/5 px-3 py-2">
        <h3 className="font-tech text-[10px] font-bold uppercase tracking-widest text-white flex items-center gap-2">
          <BrainCircuit size={12} className="text-[#f8a5a5]" />
          Agent Reasoning Terminal
        </h3>
        <button
          type="button"
          onClick={onClear ?? clearTerminal}
          className="font-tech text-[9px] uppercase text-[#6b7280] hover:text-white"
        >
          Clear
        </button>
      </div>
      <div className={`bg-black/60 p-3 ${compact ? '' : 'flex-1 overflow-y-auto'}`}>
        <p className="font-tech text-[11px] leading-relaxed text-gray-300">
          <span className="text-[#4fd1c5] mr-1">&gt;</span>
          {highlightReasoning(latest)}
        </p>
      </div>
    </div>
  );
}
