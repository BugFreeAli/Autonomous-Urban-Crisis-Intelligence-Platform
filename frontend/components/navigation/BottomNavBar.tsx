'use client';

import React from 'react';
import { Map, Radio, Asterisk, TerminalSquare, Zap, type LucideIcon } from 'lucide-react';
import type { MobileTab } from '@/app/page';

interface BottomNavBarProps {
  activeTab: MobileTab;
  setActiveTab: (tab: MobileTab) => void;
}

const items: { id: MobileTab; label: string; Icon: LucideIcon }[] = [
  { id: 'map', label: 'Map', Icon: Map },
  { id: 'signals', label: 'Signals', Icon: Radio },
  { id: 'actions', label: 'Actions', Icon: Zap },
  { id: 'resources', label: 'Res.', Icon: Asterisk },
  { id: 'terminal', label: 'Term.', Icon: TerminalSquare },
];

export default function BottomNavBar({ activeTab, setActiveTab }: BottomNavBarProps) {
  return (
    <nav className="absolute bottom-0 left-0 w-full z-[60] bg-[#0a0c0d]/95 border-t border-[#2a2a2a] pb-[env(safe-area-inset-bottom)]">
      <div className="flex h-[58px] items-stretch justify-around px-2">
        {items.map(({ id, label, Icon }) => {
          const active = activeTab === id;
          return (
            <button
              key={id}
              type="button"
              onClick={() => setActiveTab(id)}
              className="relative flex flex-1 flex-col items-center justify-center gap-0.5"
            >
              {active ? (
                <div className="mb-0.5 flex h-9 w-9 items-center justify-center rounded-md bg-[#4fd1c5] shadow-[0_0_12px_rgba(79,209,197,0.5)]">
                  <Icon size={18} className="text-[#050708]" strokeWidth={2.5} />
                </div>
              ) : (
                <Icon size={20} className="mb-0.5 text-[#6b7280]" strokeWidth={1.5} />
              )}
              <span
                className={`font-tech text-[8px] uppercase tracking-wider ${
                  active ? 'text-[#4fd1c5] glow-teal' : 'text-[#6b7280]'
                }`}
              >
                {label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
