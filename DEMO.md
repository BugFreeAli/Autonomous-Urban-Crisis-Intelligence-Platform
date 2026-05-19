# Next-Generation Operational Demo Flows

## Cinematic Sequences & Controller Guide
This guide details the exact API endpoints and expected AI behavioral flows to trigger during the live presentation, demonstrating the full autonomous capability of the platform.

### SEQUENCE 1: "Simultaneous Contradictions" (The verification capability)
**Goal:** Show how the AI handles noise, misinformation, and dual-crises without collapsing.
**Trigger:** `POST /simulation/scenarios/simultaneous_crises` followed quickly by `POST /simulation/scenarios/contradictory_reports`
**What the UI will show:**
1. A Heatwave alert in Downtown starts generating power outage nodes on the map.
2. An extreme flood alert triggers in Riverside.
3. Suddenly, 12 massive incident nodes cluster in Uptown reporting a "Gas Explosion".
4. **AI Intervention Moment:** The `CredibilityAgent` queries `FieldReportEvent` drone data. It detects the contradiction, collapses the Uptown confidence score to `0.15`, flashes the UI red with `[False Positive]`, and automatically publishes an `IncidentRetracted` SMS over the EAS stream while the Flood and Heatwave scenarios continue to be managed independently.

### SEQUENCE 2: "The Cascade & Exhaustion" (The optimization capability)
**Goal:** Prove the platform thinks 3 steps ahead and reroutes live resources to protect city stability before humans even realize the risk.
**Trigger:** `POST /simulation/scenarios/evacuation_spiral`
**What the UI will show:**
1. A Chemical Hazmat reported in Riverside. 
2. **AI Intervention Moment:** The `CascadePredictionEngine` graph immediately lights up on the dashboard. It draws a vector from Riverside to Downtown showing predictable `Traffic Collapse` in exactly 12 minutes due to the evacuation spiral.
3. Because ambulances are projected to get stuck, the `ResourceOptimizationEngine` immediately reroutes reserves *away* from the collapse zone, calculating dynamic `ETA penalty: +140s`. 
4. The `StakeholderCommunicationAgent` auto-publishes an `Evacuation Route Update` to the public, proving the AI is optimizing physical crowds in real time to save lives.

### SEQUENCE 3: "The Breaking Point"
**Trigger:** `POST /simulation/scenarios/resource_exhaustion`
**What the UI will show:**
1. You will see 4 distinct, simultaneous incidents pop up in multiple districts.
2. Dispatch UI will show Ambulances and FireEngines dynamically draining.
3. A massive Magnitude 6.2 Earthquake triggers in the UI. 
4. **AI Intervention Moment:** Instead of failing, the `ResourceOptimizationEngine` hits its 20% Hard Reserve Threshold. The AI reasoning trace scrolls: `"CRITICAL: All reserves exhausted. Preserving core assets. Escalating to human command operator."` It gracefully locks down, refusing to drain the final city reserves on low-level requests, exactly as a master commander would. 

These scenarios are optimized for storytelling explainability. Viewers will physically see the confidence percentages decay and the resource nodes traverse the map natively in real time over the WebSocket grid.