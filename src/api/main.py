from fastapi.middleware.cors import CORSMiddleware
import json
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any
import asyncio
import logging

from .deps import get_state_manager, get_trace_logger, get_event_bus, get_sim_clock, get_sim_engine, get_intelligence_engine
from .deps import event_bus, sim_clock, orchestrator, sim_engine
from .websocket import ConnectionManager
from ..state.manager import StateManager
from ..traces.logger import TraceLogger, TraceRecord
from ..orchestration.events import BaseEvent, RainfallDetected
from ..simulation.scenarios import CinematicScenarioRunner
from ..simulation.engine import CitySimulationEngine

app = FastAPI(
    title="Urban Crisis Intelligence Platform",
    description="Backend orchestration for multi-agent autonomous crisis management.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ws_manager = ConnectionManager()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Urban Crisis Intelligence Platform...")
    # Initialize Simulation engine city map
    await sim_engine.initialize_city()
    
    # Wire agents
    orchestrator.initialize_agents()
    
    # Start Event Bus
    event_bus.start()
    
    # Simulation engine runs on clock ticks
    sim_clock.register_tick_callback(sim_engine.tick)
    
    # Start Simulation Clock
    sim_clock.start()
    
    # Register a clock tick callback to broadcast state over websockets
    async def broadcast_tick(current_time):
        await ws_manager.broadcast(f'{{"event": "clock_tick", "sim_time": "{current_time}"}}')
        
    sim_clock.register_tick_callback(broadcast_tick)
    
    from ..api.deps import trace_logger
    original_log = trace_logger.log_decision
    def broadcast_trace(*args, **kwargs):
        original_log(*args, **kwargs)
        agent_name = args[1] if len(args) > 1 else kwargs.get("agent_name", "Unknown")
        action_type = args[2] if len(args) > 2 else kwargs.get("action_type", "")
        reasoning = args[3] if len(args) > 3 else kwargs.get("reasoning", "")
        metadata = kwargs.get("metadata") or {}
        is_outcome = action_type == "OperationalOutcome" or metadata.get("display_kind") == "outcome"
        if is_outcome:
            asyncio.create_task(ws_manager.broadcast(json.dumps({
                "event": "operation",
                "agent": agent_name,
                "headline": metadata.get("headline", reasoning.split("\n")[0][:120]),
                "detail": reasoning,
                "outcome_type": metadata.get("outcome_type", "action"),
                "confidence": args[4] if len(args) > 4 else kwargs.get("confidence_score", 0),
            })))
        else:
            asyncio.create_task(ws_manager.broadcast(json.dumps({
                "event": "trace",
                "agent": agent_name,
                "reasoning": reasoning,
            })))
    trace_logger.log_decision = broadcast_trace

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    await event_bus.stop()
    await sim_clock.stop()

@app.get("/api/system/status")
async def get_system_status():
    """Health check endpoint for mobile configuration validation."""
    return {"status": "online", "system": "Crisis OS", "version": "0.1.0"}

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous Urban Crisis Intelligence Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        background: '#09090b',
                        card: '#18181b',
                        primary: '#00a2ff',
                        warning: '#ffaa00',
                        destructive: '#ff0044',
                        success: '#00ff66',
                        muted: '#71717a',
                        border: '#27272a'
                    }
                }
            }
        }
    </script>
    <style>
        body {
            background-color: #09090b;
            color: #f4f4f5;
        }
        .glass-panel {
            background: rgba(24, 24, 27, 0.75);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 4px;
            height: 4px;
        }
        ::-webkit-scrollbar-track {
            background: #09090b;
        }
        ::-webkit-scrollbar-thumb {
            background: #27272a;
            border-radius: 2px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #3f3f46;
        }
        /* Tactical animations */
        @keyframes scan {
            0% { top: -10%; }
            100% { top: 110%; }
        }
        .scan-line {
            animation: scan 8s linear infinite;
        }
        .custom-div-icon {
            background: transparent;
            border: none;
        }
    </style>
</head>
<body class="w-screen h-screen overflow-hidden flex flex-col font-sans select-none relative">

    <!-- Global scanning line overlay -->
    <div class="pointer-events-none absolute inset-0 z-50 overflow-hidden opacity-5">
        <div class="h-[2px] w-full bg-primary absolute shadow-[0_0_10px_2px_#00a2ff] scan-line"></div>
    </div>

    <!-- HEADER -->
    <header class="h-16 border-b border-white/10 bg-black/60 backdrop-blur-md px-6 flex items-center justify-between z-40 shrink-0">
        <div class="flex items-center gap-4">
            <div class="flex items-center gap-2">
                <div class="w-2.5 h-2.5 rounded-full bg-success animate-pulse"></div>
                <h1 class="font-mono text-sm font-black tracking-[0.25em] text-primary">URBAN CRISIS INTELLIGENCE</h1>
            </div>
            <div class="h-4 w-px bg-white/20"></div>
            <span id="ai-status" class="font-mono text-[10px] text-muted uppercase">AI ENGINE: <span class="text-warning">CHECKING...</span></span>
            <div class="h-4 w-px bg-white/20"></div>
            <span class="font-mono text-[10px] text-muted uppercase">SYSTEM STATUS: <span class="text-success font-bold">NOMINAL 99.9%</span></span>
        </div>
        
        <div class="flex items-center gap-8">
            <div class="flex flex-col text-right font-mono">
                <span class="text-[9px] text-muted">CRISIS THREAT MATRIX</span>
                <span id="threat-indicator" class="text-xs text-primary font-bold">0.00 (LOW)</span>
            </div>
            <div class="h-4 w-px bg-white/20"></div>
            <div class="flex flex-col text-right font-mono">
                <span class="text-[9px] text-muted">SIMULATION CLOCK</span>
                <span id="sim-clock" class="text-xs text-white">MAY 17, 2026 // 18:42:04</span>
            </div>
        </div>
    </header>

    <!-- MAIN BODY -->
    <div class="flex-1 w-full flex overflow-hidden relative">

        <!-- Leaflet Map Layer (Absolute Background) -->
        <div id="map" class="absolute inset-0 z-0 bg-background"></div>

        <!-- LEFT PANEL: Signals and Reports -->
        <div class="w-80 h-full p-4 flex flex-col gap-4 z-10 pointer-events-none relative shrink-0">
            <!-- Feed Card -->
            <div class="flex-1 flex flex-col glass-panel rounded-lg overflow-hidden pointer-events-auto">
                <div class="p-3 border-b border-white/10 bg-primary/5 flex items-center justify-between">
                    <h2 class="font-mono text-[11px] font-bold text-white flex items-center gap-1.5">
                        <i data-lucide="radio" class="w-3.5 h-3.5 text-primary"></i>
                        LIVE SIGNAL FEED
                    </h2>
                    <span id="feed-count" class="text-[9px] font-mono text-primary bg-primary/10 px-1.5 py-0.5 rounded">0 REPORTS</span>
                </div>
                <div id="feed-container" class="flex-1 overflow-y-auto p-3 flex flex-col gap-2.5">
                    <div class="text-center py-8 text-xs text-muted font-mono">Awaiting sensor signals...</div>
                </div>
            </div>
        </div>

        <!-- RIGHT PANEL: AI Reasoning & Cascades -->
        <div class="w-[450px] h-full p-4 flex flex-col gap-4 ml-auto z-10 pointer-events-none shrink-0">
            <!-- AI Console -->
            <div class="flex-1 flex flex-col glass-panel rounded-lg overflow-hidden pointer-events-auto">
                <div class="p-3 border-b border-white/10 bg-warning/5 flex items-center justify-between">
                    <h2 class="font-mono text-[11px] font-bold text-white flex items-center gap-1.5">
                        <i data-lucide="brain-circuit" class="w-3.5 h-3.5 text-warning"></i>
                        AGENT REASONING TERMINAL
                    </h2>
                    <button onclick="document.getElementById('terminal').innerHTML=''" class="text-[9px] font-mono text-muted hover:text-white uppercase transition">CLEAR</button>
                </div>
                <div id="terminal" class="flex-1 overflow-y-auto p-4 flex flex-col gap-3 font-mono text-xs bg-black/40">
                    <div class="text-center py-12 text-xs text-muted">Awaiting autonomous agent decisions...</div>
                </div>
            </div>

            <!-- Urban Infrastructure Stress -->
            <div class="h-60 flex flex-col glass-panel rounded-lg overflow-hidden pointer-events-auto shrink-0">
                <div class="p-3 border-b border-white/10 bg-destructive/5">
                    <h2 class="font-mono text-[11px] font-bold text-white flex items-center gap-1.5">
                        <i data-lucide="activity" class="w-3.5 h-3.5 text-destructive"></i>
                        INFRASTRUCTURE CAPACITY METRICS
                    </h2>
                </div>
                <div class="flex-1 p-4 flex flex-col gap-3 overflow-y-auto">
                    <!-- Districts -->
                    <div class="flex flex-col gap-2">
                        <span class="text-[10px] font-mono text-muted">DISTRICT TRAFFIC DENSITY</span>
                        <div id="traffic-meters" class="grid grid-cols-3 gap-2"></div>
                    </div>
                    <div class="h-px bg-white/10 my-1"></div>
                    <!-- Hospitals -->
                    <div class="flex flex-col gap-2">
                        <span class="text-[10px] font-mono text-muted">HOSPITAL SURGE PATIENT LOAD</span>
                        <div id="hospital-bars" class="flex flex-col gap-2.5"></div>
                    </div>
                </div>
            </div>
        </div>

    </div>

    <!-- BOTTOM CONTROL BAR -->
    <div class="h-28 border-t border-white/10 bg-black/80 backdrop-blur-md px-6 py-3 flex gap-6 z-40 shrink-0 relative pointer-events-auto">
        <!-- Resource Status Container -->
        <div class="w-[500px] flex flex-col">
            <span class="font-mono text-[10px] text-muted mb-1 flex items-center gap-1">
                <i data-lucide="shield" class="w-3.5 h-3.5"></i>
                ACTIVE EMERGENCY RESOURCES
            </span>
            <div id="resources-scroller" class="flex-1 flex gap-3 overflow-x-auto items-center py-1">
                <div class="text-xs text-muted font-mono">Initializing resources...</div>
            </div>
        </div>

        <div class="h-full w-px bg-white/10"></div>

        <!-- Scenario Control Center -->
        <div class="flex-1 flex flex-col">
            <span class="font-mono text-[10px] text-muted mb-1.5 flex items-center gap-1">
                <i data-lucide="play" class="w-3.5 h-3.5"></i>
                MANUAL SCENARIO STRESS CONTROL
            </span>
            <div class="flex-1 grid grid-cols-5 gap-3 items-center">
                <button id="btn-seq1-1" onclick="triggerScenario('/simulation/scenarios/simultaneous_crises', 'btn-seq1-1')" class="h-10 text-[11px] font-mono font-bold tracking-wider rounded border border-primary/30 bg-primary/10 hover:bg-primary/20 text-primary transition-all duration-200 uppercase flex items-center justify-center">
                    Simultaneous Crises
                </button>
                <button id="btn-seq1-2" onclick="triggerScenario('/simulation/scenarios/contradictory_reports', 'btn-seq1-2')" class="h-10 text-[11px] font-mono font-bold tracking-wider rounded border border-warning/30 bg-warning/10 hover:bg-warning/20 text-warning transition-all duration-200 uppercase flex items-center justify-center">
                    Contradict Uptown
                </button>
                <button id="btn-seq2" onclick="triggerScenario('/simulation/scenarios/evacuation_spiral', 'btn-seq2')" class="h-10 text-[11px] font-mono font-bold tracking-wider rounded border border-purple-500/30 bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 transition-all duration-200 uppercase flex items-center justify-center">
                    Evacuation Spiral
                </button>
                <button id="btn-seq3" onclick="triggerScenario('/simulation/scenarios/resource_exhaustion', 'btn-seq3')" class="h-10 text-[11px] font-mono font-bold tracking-wider rounded border border-destructive/30 bg-destructive/10 hover:bg-destructive/20 text-destructive transition-all duration-200 uppercase flex items-center justify-center">
                    Resource Exhaustion
                </button>
                <div class="h-full flex gap-1.5">
                    <button id="btn-pause" onclick="triggerScenario('/simulation/clock/pause', 'btn-pause')" class="flex-1 h-10 border border-white/10 bg-white/5 hover:bg-white/10 rounded flex items-center justify-center transition">
                        <i data-lucide="pause" class="w-4 h-4"></i>
                    </button>
                    <button id="btn-resume" onclick="triggerScenario('/simulation/clock/resume', 'btn-resume')" class="flex-1 h-10 border border-success/30 bg-success/10 hover:bg-success/20 rounded flex items-center justify-center text-success transition">
                        <i data-lucide="play" class="w-4 h-4"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- TOAST POPUPS -->
    <div id="toast-container" class="absolute bottom-32 right-6 z-50 flex flex-col gap-2.5 max-w-sm pointer-events-none"></div>

    <script>
        // Coords match backend district models
        const districtCoords = {
            "D1": [32.1617, 74.1883], // Downtown
            "D2": [32.1717, 74.1983], // Riverside
            "D3": [32.1517, 74.1783]  // Uptown
        };

        const districtColors = {
            "D1": "#00a2ff",
            "D2": "#00ff66",
            "D3": "#ffaa00"
        };

        // Initialize Leaflet map centered on Downtown
        const map = L.map('map', { zoomControl: false, attributionControl: false }).setView([32.1617, 74.1883], 13);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            maxZoom: 19
        }).addTo(map);

        let incidentCircles = [];
        let resourceMarkers = [];
        let districtCircles = [];
        let hospitalMarkers = [];

        // Seed initial static nodes on map
        function seedStaticNodes(state) {
            // Draw District radius circles
            for (const [id, d] of Object.entries(state.districts)) {
                const circle = L.circle(districtCoords[id], {
                    radius: 1200,
                    color: districtColors[id],
                    fill: false,
                    weight: 1,
                    opacity: 0.15
                }).addTo(map);
                circle.bindTooltip(d.name, { permanent: true, direction: 'center', className: 'font-mono text-[9px] text-muted border-none bg-transparent shadow-none' });
                districtCircles.push(circle);
            }

            // Draw Hospital markers
            for (const [id, h] of Object.entries(state.hospitals)) {
                const coords = districtCoords[h.district_id];
                const markerCoords = [coords[0] - 0.003, coords[1] + 0.003]; // Offset slightly
                const icon = L.divIcon({
                    className: 'custom-div-icon',
                    html: `<div class="w-7 h-7 rounded border border-white/20 bg-card/90 flex items-center justify-center text-rose-500 shadow-xl"><i data-lucide="activity" class="w-3.5 h-3.5"></i></div>`,
                    iconSize: [28, 28]
                });
                const marker = L.marker(markerCoords, { icon: icon }).addTo(map);
                marker.bindPopup(`<div class="font-mono text-xs text-white"><b>${h.name}</b><br/>Capacity: ${h.capacity} beds</div>`);
                hospitalMarkers.push(marker);
            }
            lucide.createIcons();
        }

        // Periodically poll /state
        async function fetchState() {
            try {
                const res = await fetch('/state');
                const state = await res.json();
                
                if (districtCircles.length === 0 && Object.keys(state.districts).length > 0) {
                    seedStaticNodes(state);
                }

                updateDashboard(state);

                // Update AI Status
                const aiRes = await fetch('/config/ai');
                const ai = await aiRes.json();
                const aiStatusEl = document.getElementById('ai-status');
                if (ai.enabled) {
                    aiStatusEl.innerHTML = `AI ENGINE: <span class="text-success font-bold">${ai.provider} ONLINE</span>`;
                } else {
                    aiStatusEl.innerHTML = `AI ENGINE: <span class="text-destructive font-bold">BYPASSED (NO KEY)</span>`;
                }
            } catch (err) {
                console.error("Error fetching state:", err);
            }
        }

        function updateDashboard(state) {
            // Global Matrix
            document.getElementById('threat-indicator').innerText = `${state.crisis_confidence.toFixed(2)} (${state.crisis_confidence > 0.8 ? 'CRITICAL' : state.crisis_confidence > 0.4 ? 'ELEVATED' : 'LOW'})`;
            
            // Render Incidents and draw pulsing circles on map
            incidentCircles.forEach(c => map.removeLayer(c));
            incidentCircles = [];
            
            const feed = document.getElementById('feed-container');
            const incidents = Object.values(state.active_incidents);
            
            if (incidents.length === 0) {
                feed.innerHTML = `<div class="text-center py-8 text-xs text-muted font-mono">No active incidents. City is stable.</div>`;
                document.getElementById('feed-count').innerText = "0 ACTIVE";
            } else {
                document.getElementById('feed-count').innerText = `${incidents.length} ACTIVE`;
                feed.innerHTML = incidents.map(inc => {
                    const locCoords = districtCoords[inc.location] || [32.1617, 74.1883];
                    const color = inc.status === "Confirmed" ? "#ff0044" : "#ffaa00";
                    
                    // Draw map alert circle
                    const circle = L.circle(locCoords, {
                        radius: inc.radius_meters || 600,
                        color: color,
                        fillColor: color,
                        fillOpacity: 0.15,
                        weight: 2,
                        className: 'animate-pulse'
                    }).addTo(map);
                    
                    circle.bindPopup(`<div class="font-mono text-xs text-white"><b>${inc.type}</b><br/>Status: ${inc.status}<br/>Severity: ${Math.round(inc.severity*100)}%</div>`);
                    incidentCircles.push(circle);

                    return `
                        <div class="p-3 bg-white/5 border border-white/10 rounded-md relative overflow-hidden">
                            <div class="absolute left-0 top-0 bottom-0 w-1 bg-destructive" style="background-color: ${color}"></div>
                            <div class="flex justify-between items-center mb-1 pl-2">
                                <span class="text-[10px] font-mono text-white/50 font-bold uppercase">${inc.status}</span>
                                <span class="text-[10px] font-mono text-white/40">${Math.round(inc.severity*100)}% SEVERITY</span>
                            </div>
                            <p class="text-xs text-white font-bold pl-2">${inc.type}</p>
                            <p class="text-[10px] text-muted pl-2 mt-1 font-mono">Sector: ${inc.location} | Signals: ${inc.signals_clustered}</p>
                        </div>
                    `;
                }).join('');
            }

            // Draw Resources moving on map and update resources dock
            resourceMarkers.forEach(m => map.removeLayer(m));
            resourceMarkers = [];
            
            const resourcesDock = document.getElementById('resources-scroller');
            const resources = Object.values(state.resources);
            
            if (resources.length === 0) {
                resourcesDock.innerHTML = `<div class="text-xs text-muted font-mono">No resources configured.</div>`;
            } else {
                resourcesDock.innerHTML = resources.map(r => {
                    const locCoords = districtCoords[r.location] || [32.1617, 74.1883];
                    
                    // Draw Resource truck marker
                    const icon = L.divIcon({
                        className: 'custom-div-icon',
                        html: `<div class="w-8 h-8 rounded-full border-2 border-primary bg-background/90 flex items-center justify-center text-primary shadow-lg"><i data-lucide="truck" class="w-4 h-4"></i></div>`,
                        iconSize: [32, 32]
                    });
                    const marker = L.marker(locCoords, { icon: icon }).addTo(map);
                    marker.bindPopup(`<div class="font-mono text-xs text-white"><b>${r.type} (${r.resource_id})</b><br/>Status: ${r.status}<br/>Location: ${r.location}<br/>ETA: ${r.eta_seconds}s</div>`);
                    resourceMarkers.push(marker);

                    const statusColor = r.status === "Available" ? "text-success" : r.status === "Dispatched" ? "text-warning" : "text-primary";
                    return `
                        <div class="min-w-[190px] p-2 border border-white/10 rounded bg-white/5 flex gap-3 items-center shrink-0">
                            <div class="w-8 h-8 rounded bg-primary/10 flex items-center justify-center text-primary">
                                <i data-lucide="truck" class="w-4 h-4"></i>
                            </div>
                            <div class="flex flex-col">
                                <span class="font-mono text-[9px] text-white/50">${r.resource_id} // ${r.type}</span>
                                <span class="text-xs ${statusColor} font-bold">${r.status}</span>
                            </div>
                            <div class="ml-auto flex flex-col items-end font-mono">
                                <span class="text-[8px] text-muted">ETA</span>
                                <span class="text-[11px] text-success">${r.eta_seconds}s</span>
                            </div>
                        </div>
                    `;
                }).join('');
            }

            // Update traffic density meters
            const trafficContainer = document.getElementById('traffic-meters');
            trafficContainer.innerHTML = Object.values(state.districts).map(d => {
                const density = d.traffic_density;
                const color = density > 0.8 ? 'text-destructive' : density > 0.4 ? 'text-warning' : 'text-success';
                return `
                    <div class="p-2 border border-white/5 bg-white/5 rounded text-center">
                        <span class="text-[9px] font-mono text-muted block truncate">${d.name.toUpperCase()}</span>
                        <span class="text-xs font-mono font-bold ${color}">${Math.round(density*100)}%</span>
                    </div>
                `;
            }).join('');

            // Update Hospital progress bars
            const hospitalContainer = document.getElementById('hospital-bars');
            hospitalContainer.innerHTML = Object.values(state.hospitals).map(h => {
                const pct = (h.current_load / h.capacity) * 100;
                const colorClass = pct > 80 ? 'bg-destructive shadow-[0_0_8px_#ff0044]' : pct > 50 ? 'bg-warning shadow-[0_0_8px_#ffaa00]' : 'bg-success shadow-[0_0_8px_#00ff66]';
                return `
                    <div class="flex flex-col gap-1">
                        <div class="flex justify-between font-mono text-[10px]">
                            <span class="text-white/80">${h.name}</span>
                            <span class="text-muted">${h.current_load} / ${h.capacity} (${Math.round(pct)}%)</span>
                        </div>
                        <div class="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                            <div class="h-full ${colorClass} transition-all duration-300" style="width: ${pct}%"></div>
                        </div>
                    </div>
                `;
            }).join('');

            lucide.createIcons();
        }

        // Initialize WebSocket connection for real-time trace events
        function initWebSocket() {
            const ws = new WebSocket(`ws://${window.location.host}/ws/stream`);
            const term = document.getElementById('terminal');
            
            ws.onopen = () => {
                console.log("WebSocket connected.");
                term.innerHTML = `<div class="text-[10px] text-success font-mono animate-pulse">[SYSTEM] Socket connected. Monitoring agent network...</div>`;
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.event === "clock_tick") {
                    document.getElementById('sim-clock').innerText = new Date(data.sim_time).toLocaleString();
                } else if (data.event === "trace") {
                    const record = document.createElement('div');
                    record.className = 'border-b border-white/5 pb-2 mb-2 hover:bg-white/5 p-1 rounded transition duration-150';
                    
                    const agentColors = {
                        "SignalIntelligenceAgent": "text-primary shadow-[0_0_4px_rgba(0,162,255,0.4)]",
                        "CredibilityAgent": "text-warning",
                        "CrisisClassificationAgent": "text-success",
                        "CascadePredictionAgent": "text-purple-400",
                        "ResourceOptimizationAgent": "text-rose-400",
                        "StakeholderCommunicationAgent": "text-emerald-400"
                    };
                    const agentColor = agentColors[data.agent] || "text-white";
                    
                    record.innerHTML = `
                        <div class="flex justify-between text-[10px] font-mono mb-1">
                            <span class="${agentColor} font-bold">${data.agent}</span>
                            <span class="text-white/40">${new Date().toLocaleTimeString()}</span>
                        </div>
                        <p class="text-white/95 text-xs leading-relaxed font-mono whitespace-pre-line">${data.reasoning}</p>
                    `;
                    
                    // Remove initial placeholder if first trace
                    if (term.innerHTML.includes("Awaiting autonomous agent")) {
                        term.innerHTML = '';
                    }
                    
                    term.appendChild(record);
                    term.scrollTop = term.scrollHeight;
                }
            };

            ws.onclose = () => {
                console.warn("WebSocket disconnected. Retrying in 3s...");
                setTimeout(initWebSocket, 3000);
            };
        }

        // REST Control handler
        async function triggerScenario(endpoint, btnId) {
            const btn = document.getElementById(btnId);
            const originalText = btn.innerHTML;
            btn.innerHTML = `<span class="animate-spin inline-block w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full mr-2 shrink-0"></span>`;
            btn.disabled = true;
            
            try {
                const res = await fetch(endpoint, { method: 'POST' });
                const data = await res.json();
                showToast(data.status || "Scenario triggered successfully!", "success");
            } catch (err) {
                showToast("Error: " + err, "error");
            } finally {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        }

        // Clean Toast alerts
        function showToast(message, type = "success") {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            const colorClass = type === "success" ? "border-success bg-success/10 text-success" : "border-destructive bg-destructive/10 text-destructive";
            
            toast.className = `p-3 rounded border text-xs font-mono shadow-2xl flex items-center gap-2 transform translate-y-2 opacity-0 transition-all duration-300 pointer-events-auto ${colorClass}`;
            toast.innerHTML = `<i data-lucide="${type === 'success' ? 'check' : 'alert-circle'}" class="w-4 h-4 shrink-0"></i> <span>${message}</span>`;
            
            container.appendChild(toast);
            lucide.createIcons();
            
            // Animate in
            setTimeout(() => {
                toast.classList.remove('translate-y-2', 'opacity-0');
            }, 10);
            
            // Remove after 4s
            setTimeout(() => {
                toast.classList.add('opacity-0', 'translate-y-[-2px]');
                setTimeout(() => toast.remove(), 300);
            }, 4000);
        }

        // Initialize Polling & WebSockets
        fetchState().then(() => {
            setInterval(fetchState, 1000);
        });
        initWebSocket();
        lucide.createIcons();
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

# --- Rest Endpoints ---

@app.get("/state")
async def get_global_state(state: StateManager = Depends(get_state_manager)):
    """Retrieve the authoritative current global state."""
    return await state.get_state()

@app.get("/state/incidents")
async def get_active_incidents(state: StateManager = Depends(get_state_manager)):
    """Retrieve all active incidents."""
    current_state = await state.get_state()
    return current_state.active_incidents

@app.get("/state/resources")
async def get_resources(state: StateManager = Depends(get_state_manager)):
    """Retrieve all tracked resources."""
    current_state = await state.get_state()
    return current_state.resources

@app.get("/state/timeline")
async def get_state_timeline(state: StateManager = Depends(get_state_manager)):
    """Retrieve the historical timeline of global states."""
    return state.get_timeline()

@app.get("/traces")
async def get_system_traces(traces: TraceLogger = Depends(get_trace_logger)):
    """Retrieve structured agent reasoning logs."""
    return traces.get_all_traces()

@app.get("/operations")
async def get_operational_outcomes(traces: TraceLogger = Depends(get_trace_logger)):
    """Final agent decisions and actions (dispatch, alerts, retractions, etc.)."""
    return traces.get_operational_outcomes()

@app.get("/config/ai")
async def get_ai_config(intel = Depends(get_intelligence_engine)):
    """Check if the AI (Gemini) integration is active."""
    return {
        "enabled": intel.enabled,
        "provider": "Google Gemini",
        "status": "Ready" if intel.enabled else "Bypassed (API Key Missing)"
    }

@app.post("/test/emit_rainfall")
async def emit_test_event(bus=Depends(get_event_bus)):
    """Test endpoint to inject an event into the system."""
    import uuid
    from datetime import datetime
    
    event = RainfallDetected(
        event_id=f"evt-{uuid.uuid4()}",
        source="ExternalSensorAPI",
        payload={"sensor_id": "rain-01", "mm_per_hour": 15.5}
    )
    await bus.publish(event)
    return {"status": "published", "event_id": event.event_id}

# --- Simulation & Control Endpoints ---

@app.post("/simulation/scenarios/simultaneous_crises")
async def trigger_simultaneous(engine: CitySimulationEngine = Depends(get_sim_engine), clock = Depends(get_sim_clock), bus = Depends(get_event_bus)):
    runner = CinematicScenarioRunner(engine, bus)
    asyncio.create_task(runner.run_simultaneous_flood_heatwave(clock.current_time))
    return {"status": "Cinematic Scenario Started: Simultaneous Crises"}

@app.post("/simulation/scenarios/contradictory_reports")
async def trigger_contradiction(engine: CitySimulationEngine = Depends(get_sim_engine), clock = Depends(get_sim_clock), bus = Depends(get_event_bus)):
    runner = CinematicScenarioRunner(engine, bus)
    asyncio.create_task(runner.run_contradictory_reports(clock.current_time))
    return {"status": "Cinematic Scenario Started: Misinformation & Contradiction"}

@app.post("/simulation/scenarios/hospital_overload")
async def trigger_hospital_overload(engine: CitySimulationEngine = Depends(get_sim_engine), clock = Depends(get_sim_clock), bus = Depends(get_event_bus)):
    runner = CinematicScenarioRunner(engine, bus)
    asyncio.create_task(runner.run_hospital_overload_escalation(clock.current_time))
    return {"status": "Cinematic Scenario Started: Hospital Overload"}

@app.post("/simulation/scenarios/evacuation_spiral")
async def trigger_evacuation(engine: CitySimulationEngine = Depends(get_sim_engine), clock = Depends(get_sim_clock), bus = Depends(get_event_bus)):
    runner = CinematicScenarioRunner(engine, bus)
    asyncio.create_task(runner.run_evacuation_spiral(clock.current_time))
    return {"status": "Cinematic Scenario Started: Evacuation Congestion Spiral"}

@app.post("/simulation/scenarios/resource_exhaustion")
async def trigger_exhaustion(engine: CitySimulationEngine = Depends(get_sim_engine), clock = Depends(get_sim_clock), bus = Depends(get_event_bus)):
    runner = CinematicScenarioRunner(engine, bus)
    asyncio.create_task(runner.run_resource_exhaustion(clock.current_time))
    return {"status": "Cinematic Scenario Started: Resource Exhaustion"}

@app.post("/simulation/scenario/flood")
async def trigger_flood(engine: CitySimulationEngine = Depends(get_sim_engine), clock = Depends(get_sim_clock)):
    """Inject a dynamic flooding scenario to kick off cascade failures."""
    await engine.trigger_flood_scenario(clock.current_time)
    return {"status": "Scenario triggered: Flood"}

@app.post("/simulation/clock/speed")
async def set_clock_speed(scale: float, clock = Depends(get_sim_clock)):
    """Accelerate or slow the simulation (e.g., scale 60.0 = 1 hr per real min)."""
    clock.time_scale_factor = scale
    return {"status": "success", "scale": scale}

@app.post("/simulation/clock/pause")
async def pause_clock(clock = Depends(get_sim_clock)):
    """Pause the simulation progression."""
    await clock.stop()
    return {"status": "Simulation Paused"}

@app.post("/simulation/clock/resume")
async def resume_clock(clock = Depends(get_sim_clock)):
    """Resume the simulation progression."""
    clock.start()
    return {"status": "Simulation Resumed"}

# --- WebSocket Endpoints ---

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    Real-time streaming endpoint for dashboards.
    Pushes clock ticks, agent trace events, and critical state updates.
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            # Client can send commands here if needed, we just ping-pong for now
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
