import React from 'react';
import { motion } from 'framer-motion';
import { BrainCircuit, ShieldAlert, FileSearch } from 'lucide-react';

export default function RightPanel() {
  return (
    <div className="absolute top-20 right-4 bottom-32 w-96 glass-panel rounded-lg z-40 flex flex-col overflow-hidden">
      <div className="p-3 border-b border-warning/30 bg-warning/10">
        <h2 className="font-mono text-xs font-bold text-white flex items-center gap-2">
          <BrainCircuit size={14} className="text-warning" />
          AI INTELLIGENCE & CASCADES
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        {/* Active Cascade Prediction */}
        <div className="border border-destructive/30 rounded-md bg-destructive/5 p-3">
          <h3 className="text-xs font-mono text-destructive mb-3 flex items-center gap-2">
            <ShieldAlert size={12} /> ESCALATION PREDICTION
          </h3>
          <div className="relative">
            {/* Cascade Flow */}
            <div className="absolute left-2 top-2 bottom-2 w-px bg-destructive/30" />
            <div className="flex flex-col gap-4">
              <div className="pl-6 relative">
                <div className="absolute left-[5px] top-1.5 w-1.5 h-1.5 rounded-full bg-destructive" />
                <span className="text-xs text-white">River Flooding (Active)</span>
              </div>
              <div className="pl-6 relative">
                <div className="absolute left-[5px] top-1.5 w-1.5 h-1.5 rounded-full bg-warning" />
                <span className="text-xs text-white/80">Major Traffic Collapse (80% Prob)</span>
              </div>
              <div className="pl-6 relative">
                <div className="absolute left-[5px] top-1.5 w-1.5 h-1.5 rounded-full bg-warning/50 border border-warning" />
                <span className="text-xs text-white/50">Ambulance Routing Failure (ETA +25m)</span>
              </div>
            </div>
          </div>
        </div>

        {/* AI Trace Log */}
        <div>
          <h3 className="font-mono text-[10px] text-muted-foreground mb-2 mt-2">AGENT REASONING TRACE</h3>
          <div className="space-y-2">
            <div className="p-2 border border-white/10 rounded bg-white/5 text-xs">
              <div className="flex justify-between mb-1">
                <span className="text-[10px] text-primary font-mono">ResourceOptAgent</span>
                <span className="text-[10px] text-white/50">Conf: 0.88</span>
              </div>
              <p className="text-white/80 text-[11px]">Rerouting Unit A7 to Memorial Hospital to avoid sector 4 gridlock.</p>
              <div className="mt-1 text-[9px] text-destructive/80 font-mono">Trade-off: +5m ETA, -15% Flood Risk</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
