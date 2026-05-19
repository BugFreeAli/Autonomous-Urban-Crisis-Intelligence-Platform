import React from 'react';

export default function TopBar() {
  return (
    <header className="absolute top-0 left-0 right-0 h-14 bg-black/80 backdrop-blur-md border-b border-primary/20 z-50 flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
          <h1 className="font-mono text-sm font-bold tracking-widest text-primary">URBAN CRISIS INTELLIGENCE</h1>
        </div>
        <div className="h-4 w-px bg-white/20 mx-2" />
        <span className="font-mono text-xs text-muted-foreground">OPERATIONAL MODE: <span className="text-warning">AUTONOMOUS</span></span>
      </div>
      
      <div className="flex items-center gap-6">
        <div className="flex flex-col text-right">
          <span className="font-mono text-[10px] text-muted-foreground">SYSTEM HEALTH</span>
          <span className="font-mono text-xs text-success">NOMINAL 99.9%</span>
        </div>
        <div className="h-4 w-px bg-white/20" />
        <div className="flex flex-col text-right">
          <span className="font-mono text-[10px] text-muted-foreground">SIMULATION CLOCK</span>
          <span className="font-mono text-xs text-white">MAY 17, 2026 // 18:42:04</span>
        </div>
      </div>
    </header>
  );
}
