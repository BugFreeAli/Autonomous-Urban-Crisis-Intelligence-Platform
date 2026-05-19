'use client';

import React, { useState, useEffect } from 'react';
import { Settings, Server, CheckCircle2, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import { checkBackendReachable } from '@/lib/api';

export default function ConfigScreen({
  onConfigured,
  onSkip,
}: {
  onConfigured: (ip: string) => void;
  onSkip: () => void;
}) {
  const [ipAddress, setIpAddress] = useState('');
  const [tested, setTested] = useState<'idle' | 'testing' | 'success' | 'failed'>('idle');
  const [errorDetail, setErrorDetail] = useState('');

  useEffect(() => {
    const savedIp = localStorage.getItem('backend_ip');
    if (savedIp) {
      setIpAddress(savedIp);
    }
  }, []);

  const handleTestAndSave = async () => {
    if (!ipAddress) return;
    setTested('testing');
    setErrorDetail('');
    const result = await checkBackendReachable(ipAddress);
    if (result.ok) {
      setTested('success');
      localStorage.setItem('backend_ip', result.baseUrl);
      setTimeout(() => onConfigured(result.baseUrl), 800);
    } else {
      setTested('failed');
      setErrorDetail(result.error);
    }
  };

  return (
    <motion.div
      className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-[#0a0a0a] text-white p-6 font-mono"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <motion.div className="w-full max-w-sm">
        <motion.div className="flex items-center justify-center mb-8 text-[#4fd1c5]">
          <Server size={48} className="mr-3" />
          <h1 className="text-3xl font-bold tracking-widest uppercase">CRISIS OS</h1>
        </motion.div>

        <motion.div className="bg-[#111] border border-[#333] p-6 rounded-xl shadow-lg relative overflow-hidden">
          <motion.div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[#4fd1c5] to-transparent opacity-50" />

          <h2 className="text-lg text-gray-300 mb-6 flex items-center">
            <Settings size={20} className="mr-2" />
            Neural Link Configuration
          </h2>

          <motion.div className="space-y-4">
            <motion.div>
              <label className="block text-xs uppercase tracking-wider text-gray-500 mb-2">
                Backend Address (IP:Port)
              </label>
              <input
                type="text"
                value={ipAddress}
                onChange={(e) => {
                  setIpAddress(e.target.value);
                  setTested('idle');
                  setErrorDetail('');
                }}
                placeholder="192.168.100.120:8000"
                className="w-full bg-black border border-[#333] focus:border-[#4fd1c5] rounded-lg px-4 py-3 text-[#4fd1c5] outline-none transition-colors"
                autoComplete="off"
                autoCapitalize="off"
                spellCheck="false"
              />
            </motion.div>

            <button
              type="button"
              onClick={handleTestAndSave}
              disabled={tested === 'testing' || !ipAddress}
              className={`w-full py-3 rounded-lg font-bold tracking-widest text-sm transition-all flex justify-center items-center ${
                tested === 'success'
                  ? 'bg-green-500/20 text-green-400 border border-green-500/50'
                  : tested === 'failed'
                    ? 'bg-red-500/20 text-red-400 border border-red-500/50 hover:bg-red-500/30'
                    : 'bg-[#4fd1c5]/10 text-[#4fd1c5] border border-[#4fd1c5]/30 hover:bg-[#4fd1c5]/20'
              }`}
            >
              {tested === 'idle' && 'INITIALIZE LINK'}
              {tested === 'testing' && 'CONNECTING...'}
              {tested === 'success' && (
                <>
                  <CheckCircle2 size={18} className="mr-2" /> LINK ESTABLISHED
                </>
              )}
              {tested === 'failed' && 'CONNECTION FAILED - RETRY'}
            </button>

            <button
              type="button"
              onClick={onSkip}
              className="w-full py-3 rounded-lg font-bold tracking-widest text-sm transition-all border border-[#666] text-gray-300 hover:bg-[#1b1b1b]"
            >
              SKIP BACKEND CONNECTION
            </button>

            {tested === 'failed' && errorDetail ? (
              <p className="text-left text-[11px] text-red-300/90">{errorDetail}</p>
            ) : null}

            <motion.div className="rounded-lg border border-yellow-500/40 bg-yellow-500/10 p-3">
              <p className="flex items-start gap-2 text-left text-[11px] text-yellow-300">
                <AlertTriangle size={14} className="mt-0.5 shrink-0" />
                If you skip backend connection, the system will open but live simulation will not work as
                planned. No backend means no real data, no live decisions, and no real dispatch actions.
              </p>
            </motion.div>
          </motion.div>

          <p className="mt-6 text-xs text-gray-600 text-center">
            Use only IP and port (e.g. 192.168.100.120:8000). Run the backend with{' '}
            <span className="text-gray-500">uvicorn src.api.main:app --host 0.0.0.0 --port 8000</span>
            . Rebuild the APK in Android Studio after updating the app.
          </p>
        </motion.div>
      </motion.div>
    </motion.div>
  );
}
