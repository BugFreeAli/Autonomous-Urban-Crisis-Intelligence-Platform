'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import ConfigScreen from '@/components/ConfigScreen';
import BottomNavBar from '@/components/navigation/BottomNavBar';
import SignalsView from '@/components/views/SignalsView';
import ResourcesView from '@/components/views/ResourcesView';
import TerminalView from '@/components/views/TerminalView';
import OperationsView from '@/components/views/OperationsView';
import MobileHeader from '@/components/MobileHeader';
import InfrastructurePanel from '@/components/InfrastructurePanel';
import DiagnosticsSheet from '@/components/DiagnosticsSheet';
import { CrisisBackendProvider } from '@/hooks/useCrisisBackend';

const LiveMap = dynamic(() => import('@/components/LiveMap'), { ssr: false });

export type MobileTab = 'map' | 'signals' | 'actions' | 'resources' | 'terminal';

export default function MobileDashboard() {
  const [isConfigured, setIsConfigured] = useState(false);
  const [backendIp, setBackendIp] = useState('');
  const [activeTab, setActiveTab] = useState<MobileTab>('map');

  React.useEffect(() => {
    const saved = localStorage.getItem('backend_ip');
    if (saved) {
      setBackendIp(saved);
      setIsConfigured(true);
    }
  }, []);

  if (!isConfigured) {
    return (
      <ConfigScreen
        onConfigured={(ip) => {
          setBackendIp(ip);
          setIsConfigured(true);
        }}
        onSkip={() => {
          localStorage.removeItem('backend_ip');
          setBackendIp('');
          setIsConfigured(true);
        }}
      />
    );
  }

  return (
    <CrisisBackendProvider baseUrl={backendIp}>
      <DashboardShell activeTab={activeTab} setActiveTab={setActiveTab} />
    </CrisisBackendProvider>
  );
}

function DashboardShell({
  activeTab,
  setActiveTab,
}: {
  activeTab: MobileTab;
  setActiveTab: (t: MobileTab) => void;
}) {
  const [diagOpen, setDiagOpen] = useState(false);
  const isMap = activeTab === 'map';

  return (
    <div className="fixed inset-0 flex h-full w-full flex-col overflow-hidden bg-[#050708]">
      {isMap && (
        <div className="absolute inset-0 z-0">
          <LiveMap />
        </div>
      )}

      <div
        className={`relative z-50 flex h-full w-full flex-col ${
          isMap ? 'pointer-events-none' : 'pointer-events-auto bg-[#050708]'
        }`}
      >
        {isMap ? (
          <>
            <MobileHeader onMatrixTap={() => setDiagOpen(true)} />
            <div className="pointer-events-auto mt-auto mb-[72px] space-y-3 px-4">
              <InfrastructurePanel />
            </div>
          </>
        ) : (
          <div className="flex min-h-0 flex-1 flex-col pb-[58px]">
            {activeTab === 'signals' && <SignalsView />}
            {activeTab === 'actions' && <OperationsView />}
            {activeTab === 'resources' && <ResourcesView />}
            {activeTab === 'terminal' && <TerminalView />}
          </div>
        )}

        <div className={isMap ? 'pointer-events-auto' : ''}>
          <BottomNavBar activeTab={activeTab} setActiveTab={setActiveTab} />
        </div>
      </div>
<div className="pointer-events-none fixed inset-0 z-[100] opacity-[0.08]">
        <div className="animate-scan absolute h-px w-full bg-[#4fd1c5]" />
      </div>

      <DiagnosticsSheet open={diagOpen} onClose={() => setDiagOpen(false)} />
    </div>
  );
}
