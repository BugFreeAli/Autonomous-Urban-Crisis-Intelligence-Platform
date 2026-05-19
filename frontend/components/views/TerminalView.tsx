'use client';

import React, { useEffect, useRef, useState } from 'react';
import { TerminalSquare } from 'lucide-react';
import { useCrisisBackend } from '@/hooks/useCrisisBackend';
import StatusBar from '@/components/StatusBar';
import DiagnosticsSheet from '@/components/DiagnosticsSheet';
import type { TerminalLogLine } from '@/lib/types';

function renderLine(line: TerminalLogLine) {
  if (line.kind === 'sys') {
    return <span className="text-[#00ff41]">{line.text}</span>;
  }
  if (line.kind === 'detail') {
    return <span className="pl-4 text-gray-500">{line.text}</span>;
  }
  if (line.kind === 'agent') {
    return <span className="font-bold text-[#4fd1c5]">{line.text}</span>;
  }
  const parts = line.text.split(/(MERGE|RETRACT|CONFIRM|ESCALATE)/g);
  return (
    <span className="text-white">
      {parts.map((p, i) =>
        ['MERGE', 'RETRACT', 'CONFIRM', 'ESCALATE'].includes(p) ? (
          <span key={i} className="font-bold text-[#4fd1c5]">
            {p}
          </span>
        ) : (
          <span key={i}>{p.startsWith('>') ? p : `> ${p}`}</span>
        )
      )}
    </span>
  );
}

export default function TerminalView() {
  const { terminalLines, clearTerminal, simTime, offlineMode } = useCrisisBackend();
  const scrollRef = useRef<HTMLDivElement>(null);
  const [diagOpen, setDiagOpen] = useState(false);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [terminalLines]);

  return (
    <div className="flex h-full min-h-0 flex-col bg-[#050708] pb-[72px] text-white">
      <StatusBar showNeuralLink onMatrixTap={() => setDiagOpen(true)} />
      {offlineMode ? (
        <div className="mx-3 mt-2 rounded border border-yellow-500/40 bg-yellow-500/10 px-3 py-2">
          <p className="font-tech text-[10px] text-yellow-300">
            Backend is not connected. Terminal is showing local placeholder/system messages only.
          </p>
        </div>
      ) : null}

      <div className="terminal-notch mx-3 mt-3 flex min-h-0 flex-1 flex-col overflow-hidden rounded-sm border border-[#4fd1c5] bg-black">
        <div className="flex items-center justify-between border-b border-[#4fd1c5]/30 px-3 py-2">
          <h2 className="font-tech text-[11px] font-bold uppercase tracking-widest text-[#4fd1c5]">
            Agent Reasoning
          </h2>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={clearTerminal}
              className="font-tech text-[9px] uppercase text-gray-500"
            >
              Clear
            </button>
            <TerminalSquare size={16} className="text-[#4fd1c5]" />
          </div>
        </div>

        <div ref={scrollRef} className="scroll-panel flex-1 overflow-y-auto p-3 font-tech text-[10px] leading-relaxed">
          {terminalLines.map((line) => (
            <div key={line.id} className="mb-2">
              {renderLine(line)}
            </div>
          ))}
          <div className="mt-2 h-[12px] w-2 animate-pulse bg-[#4fd1c5]" />
        </div>
      </div>

      {simTime ? (
        <p className="px-3 py-1 text-center font-tech text-[9px] text-gray-600">
          Sim clock: {new Date(simTime).toLocaleString()}
        </p>
      ) : null}

      <DiagnosticsSheet open={diagOpen} onClose={() => setDiagOpen(false)} />
    </div>
  );
}
