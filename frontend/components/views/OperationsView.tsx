'use client';

import React, { useMemo, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield,
  Truck,
  Radio,
  Megaphone,
  AlertTriangle,
  CheckCircle2,
  GitMerge,
  UserCog,
  Sparkles,
  type LucideIcon,
} from 'lucide-react';
import { useCrisisBackend } from '@/hooks/useCrisisBackend';
import StatusBar from '@/components/StatusBar';
import DiagnosticsSheet from '@/components/DiagnosticsSheet';
import type { TraceRecord } from '@/lib/types';
import type { OutcomeType } from '@/lib/types';

const OUTCOME_STYLE: Record<
  string,
  { border: string; bg: string; text: string; Icon: LucideIcon }
> = {
  dispatch: { border: 'border-[#4fd1c5]', bg: 'bg-[#4fd1c5]/10', text: 'text-[#4fd1c5]', Icon: Truck },
  comms: { border: 'border-[#f8a5a5]', bg: 'bg-[#f8a5a5]/10', text: 'text-[#f8a5a5]', Icon: Megaphone },
  forecast: { border: 'border-[#e9d5a5]', bg: 'bg-[#e9d5a5]/10', text: 'text-[#e9d5a5]', Icon: AlertTriangle },
  retract: { border: 'border-gray-500', bg: 'bg-gray-500/10', text: 'text-gray-400', Icon: CheckCircle2 },
  confirm: { border: 'border-[#4fd1c5]', bg: 'bg-[#4fd1c5]/10', text: 'text-[#4fd1c5]', Icon: Shield },
  classify: { border: 'border-[#4fd1c5]', bg: 'bg-[#4fd1c5]/15', text: 'text-[#4fd1c5]', Icon: Sparkles },
  command: { border: 'border-[#00ff41]', bg: 'bg-[#00ff41]/10', text: 'text-[#00ff41]', Icon: UserCog },
  merge: { border: 'border-[#a78bfa]', bg: 'bg-[#a78bfa]/10', text: 'text-[#a78bfa]', Icon: GitMerge },
  detect: { border: 'border-[#f8a5a5]', bg: 'bg-[#f8a5a5]/10', text: 'text-[#f8a5a5]', Icon: Radio },
  escalate: { border: 'border-[#e53e3e]', bg: 'bg-[#e53e3e]/10', text: 'text-[#e53e3e]', Icon: AlertTriangle },
  action: { border: 'border-[#4fd1c5]', bg: 'bg-[#4fd1c5]/10', text: 'text-[#4fd1c5]', Icon: Shield },
};

function agentLabel(name: string): string {
  return name.replace('Agent', '').replace(/([A-Z])/g, ' $1').trim();
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  } catch {
    return '';
  }
}

function OperationCard({ op, index }: { op: TraceRecord; index: number }) {
  const meta = (op.metadata || {}) as Record<string, string>;
  const outcomeType = (meta.outcome_type as OutcomeType) || 'action';
  const style = OUTCOME_STYLE[outcomeType] || OUTCOME_STYLE.action;
  const headline = meta.headline || op.reasoning.split('\n')[0];
  const body = op.reasoning.includes('\n') ? op.reasoning.split('\n').slice(1).join('\n').trim() : '';
  const Icon = style.Icon;

  return (
    <motion.article
      initial={{ opacity: 0, y: 16, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay: index * 0.04, duration: 0.35 }}
      className={`relative overflow-hidden rounded-xl border-l-4 ${style.border} border border-[#333] bg-[#111] shadow-lg`}
    >

<div className={`absolute inset-0 ${style.bg} opacity-40 pointer-events-none`} />
      <div className="relative p-4">
<div className="mb-3 flex items-start justify-between gap-2">
          <div className="flex items-center gap-2">
            <div className={`flex h-9 w-9 items-center justify-center rounded-lg border ${style.border} ${style.bg}`}>
              <Icon size={18} className={style.text} />
            </div>
            <div>
              <p className={`font-tech text-[9px] uppercase tracking-widest ${style.text}`}>
                {outcomeType}
              </p>
              <p className="font-tech text-[10px] text-gray-500">{agentLabel(op.agent_name)}</p>
            </div>
          </div>
          <span className="shrink-0 font-tech text-[9px] text-gray-600">{formatTime(op.timestamp)}</span>
        </div>

        <h3 className="mb-2 font-display text-base leading-snug text-white">{headline}</h3>
        {body ? <p className="mb-3 font-tech text-[11px] leading-relaxed text-gray-400">{body}</p> : null}

        {op.trade_offs_considered && op.trade_offs_considered.length > 0 && (
          <div className="rounded-lg border border-[#222] bg-black/40 p-3">
            <p className="mb-2 font-tech text-[9px] uppercase tracking-widest text-[#4fd1c5]">What happened</p>
            <ul className="space-y-1.5">
              {op.trade_offs_considered.map((line, i) => (
                <li key={i} className="flex gap-2 font-tech text-[11px] text-gray-300">
                  <span className="text-[#4fd1c5]">▸</span>
                  {line}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="mt-3 flex items-center justify-between border-t border-[#222] pt-2">
          <span className="font-tech text-[9px] text-gray-600">Confidence</span>
          <span className={`font-tech text-xs font-bold ${style.text}`}>
            {Math.round(op.confidence_score * 100)}%
          </span>
        </div>
      </div>
    </motion.article>
  );
}

export default function OperationsView() {
  const { operations, offlineMode } = useCrisisBackend();
  const [diagOpen, setDiagOpen] = React.useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const prevCount = useRef(0);

  const sorted = useMemo(
    () => [...operations].reverse(),
    [operations]
  );

  useEffect(() => {
    if (sorted.length > prevCount.current && scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
    prevCount.current = sorted.length;
  }, [sorted.length]);

  return (
    <div className="flex h-full flex-col bg-[#050708] text-white">
      <StatusBar onMatrixTap={() => setDiagOpen(true)} />
      {offlineMode ? (
        <div className="mx-4 mt-3 rounded border border-yellow-500/40 bg-yellow-500/10 px-3 py-2">
          <p className="font-tech text-[10px] text-yellow-300">
            Backend is not connected. No live operations can be generated.
          </p>
        </div>
      ) : null}
<div className="border-b border-[#4fd1c5]/30 bg-gradient-to-r from-[#4fd1c5]/10 to-transparent px-4 py-4">
        <h2 className="font-display text-lg text-white">Live Operations</h2>
        <p className="mt-1 font-tech text-[11px] text-gray-400">
          Final decisions only — what each agent actually did to handle the crisis.
        </p>
        <p className="mt-2 font-tech text-[10px] text-[#4fd1c5]">
          {sorted.length} action{sorted.length !== 1 ? 's' : ''} recorded
        </p>
      </div>

      <div ref={scrollRef} className="scroll-panel flex-1 overflow-y-auto px-4 py-4 pb-24">
        <AnimatePresence mode="popLayout">
          {sorted.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-12 rounded-xl border border-dashed border-[#333] p-8 text-center"
            >
              <Sparkles className="mx-auto mb-3 text-[#4fd1c5]" size={32} />
              <p className="font-display text-sm text-gray-300">No operations yet</p>
              <p className="mt-2 font-tech text-[11px] leading-relaxed text-gray-500">
                Go to <span className="text-[#4fd1c5]">Resources</span> and run a scenario
                (e.g. Simultaneous Crises). Decisions will stream here in real time.
              </p>
            </motion.div>
          ) : (
            <motion.div className="space-y-4">
              {sorted.map((op, i) => (
                <OperationCard key={op.trace_id} op={op} index={i} />
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <DiagnosticsSheet open={diagOpen} onClose={() => setDiagOpen(false)} />
    </div>
  );
}
