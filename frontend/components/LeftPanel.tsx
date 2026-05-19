import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, Activity, Zap } from 'lucide-react';

const mockSignals = [
  { id: '1', type: 'social', message: 'Heavy flooding on Main St, cars underwater.', time: '-2m', credibility: 0.8 },
  { id: '2', type: 'sensor', message: 'River level breached 15ft threshold.', time: '-4m', credibility: 0.99 },
  { id: '3', type: 'emergency', message: 'Multiple 911 calls from Sector 4.', time: '-5m', credibility: 0.95 },
];

export default function LeftPanel() {
  return (
    <div className="absolute top-20 left-4 bottom-32 w-80 glass-panel rounded-lg z-40 flex flex-col overflow-hidden">
      <div className="p-3 border-b border-white/10 bg-primary/10">
        <h2 className="font-mono text-xs font-bold text-white flex items-center gap-2">
          <Activity size={14} className="text-primary" />
          LIVE SIGNAL FEED
        </h2>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
        <AnimatePresence>
          {mockSignals.map((sig) => (
            <motion.div 
              key={sig.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="p-3 bg-white/5 border border-white/10 rounded-md relative overflow-hidden"
            >
              {/* Highlight bar based on credibility */}
              <div 
                className="absolute left-0 top-0 bottom-0 w-1 bg-primary" 
                style={{ opacity: sig.credibility }} 
              />
              <div className="flex justify-between items-center mb-2 pl-2">
                <span className="text-[10px] font-mono text-muted-foreground uppercase">{sig.type}</span>
                <span className="text-[10px] font-mono text-white/50">{sig.time}</span>
              </div>
              <p className="text-xs text-white/90 pl-2 leading-relaxed">{sig.message}</p>
              <div className="mt-2 pl-2 flex items-center gap-2">
                <div className="h-1 flex-1 bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full bg-primary" style={{ width: `${sig.credibility * 100}%` }} />
                </div>
                <span className="text-[9px] font-mono text-primary">{Math.round(sig.credibility * 100)}% VERIFIED</span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
