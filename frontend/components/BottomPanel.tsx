import React from 'react';
import { Truck, Shield, Navigation } from 'lucide-react';

const mockResources = [
  { id: 'A-7', type: 'Ambulance', status: 'En Route', eta: '5m' },
  { id: 'ENG-2', type: 'Fire/Rescue', status: 'On Scene', eta: '0m' },
  { id: 'DRN-X', type: 'Surveillance Drone', status: 'Deploying', eta: '2m' },
];

export default function BottomPanel() {
  return (
    <div className="absolute bottom-4 left-4 right-4 h-24 glass-panel rounded-lg z-40 flex items-center px-6">
      <div className="flex flex-col border-r border-white/10 pr-6 mr-6">
        <span className="font-mono text-xs text-muted-foreground mb-1">ACTIVE DEPLOYMENTS</span>
        <span className="text-2xl font-mono text-white">124</span>
      </div>
      
      <div className="flex-1 flex gap-4 overflow-x-auto h-full items-center">
        {mockResources.map(res => (
          <div key={res.id} className="min-w-[180px] p-2 border border-white/10 rounded bg-white/5 flex gap-3 items-center">
            <div className="w-8 h-8 rounded bg-primary/20 flex items-center justify-center text-primary">
              <Truck size={16} />
            </div>
            <div className="flex flex-col">
              <span className="font-mono text-[10px] text-white/50">{res.id} - {res.type}</span>
              <span className="text-xs text-white">{res.status}</span>
            </div>
            <div className="ml-auto flex flex-col items-end">
              <span className="font-mono text-[10px] text-muted-foreground">ETA</span>
              <span className="font-mono text-xs text-success">{res.eta}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
