'use client';

import { useEffect, useMemo, useState } from 'react';
import { MapContainer, TileLayer, Circle, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useCrisisBackend } from '@/hooks/useCrisisBackend';
import { MAP_CENTER, resolveDistrictCoords, resolveDistrictLabel } from '@/lib/constants';
import type { Incident, Resource } from '@/lib/types';

const MAP_URL = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';

const truckIcon = new L.DivIcon({
  className: 'custom-div-icon',
  html: `
<div style="width:32px;height:32px;border-radius:50%;border:2px solid #4fd1c5;background:rgba(5,7,8,0.9);display:flex;align-items:center;justify-content:center;color:#4fd1c5;font-size:14px;">⬡</div>`,
  iconSize: [32, 32],
  iconAnchor: [16, 16],
});

function incidentColor(status: string) {
  if (status === 'Confirmed' || status === 'Escalating') return '#e53e3e';
  if (status === 'Suspected' || status === 'Emerging') return '#4fd1c5';
  return '#f8a5a5';
}

export default function LiveMap() {
  const [mounted, setMounted] = useState(false);
  const { state } = useCrisisBackend();

  useEffect(() => {
    setMounted(true);
    const t = setTimeout(() => window.dispatchEvent(new Event('resize')), 400);
    return () => clearTimeout(t);
  }, []);

  const incidents = useMemo(() => {
    if (!state?.active_incidents) return [];
    return Object.values(state.active_incidents).filter(
      (i) => !['Resolved', 'Retracted'].includes(i.status)
    );
  }, [state]);

  const resources = useMemo(() => {
    if (!state?.resources) return [];
    return Object.values(state.resources);
  }, [state]);

  if (!mounted) {
    return (
      <div className="absolute inset-0 flex items-center justify-center bg-[#09090b] font-tech text-[#4fd1c5]">
        LOADING MAP...
      </div>
    );
  }

  return (
    <div className="absolute inset-0 z-[1] h-full w-full bg-[#09090b]">
      <MapContainer center={MAP_CENTER} zoom={13} style={{ height: '100%', width: '100%' }} zoomControl={false}>
        <TileLayer
          attribution='&copy; OSM &copy; CARTO'
          url={MAP_URL}
        />
        {incidents.map((inc: Incident) => {
          const coords = resolveDistrictCoords(inc.location);
          const color = incidentColor(inc.status);
          return (
            <Circle
              key={inc.incident_id}
              center={coords}
              radius={inc.radius_meters || 600}
              pathOptions={{
                color,
                fillColor: color,
                fillOpacity: 0.18,
                weight: 2,
              }}
            >
              <Popup>
                <div className="font-tech text-xs">
                  <b>{inc.type}</b>
                  <br />
                  {inc.status} — {Math.round(inc.severity * 100)}%
                </div>
              </Popup>
            </Circle>
          );
        })}
        {resources.map((res: Resource) => {
          const loc = res.location || res.target_location || 'D1';
          const coords = resolveDistrictCoords(loc);
          return (
            <Marker key={res.resource_id} position={coords} icon={truckIcon}>
              <Popup>
<div className="font-tech text-xs">
                  <b>
                    {res.type} ({res.resource_id})
                  </b>
                  <br />
                  {res.status} @ {resolveDistrictLabel(loc)}
                  <br />
                  ETA: {res.eta_seconds ?? 0}s
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
