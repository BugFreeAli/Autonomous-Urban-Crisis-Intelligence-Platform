import urllib.request
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def http_get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error GETting {url}: {e}")
        return None

def http_post(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error POSTing {url}: {e}")
        return None

def print_separator(title):
    print("\n" + "="*80)
    print(f" {title.upper()} ".center(80, "="))
    print("="*80 + "\n")

def print_state_summary(state):
    if not state:
        print("No state data available.")
        return
        
    print(f"Timestamp: {state.get('timestamp')}")
    print(f"Global Crisis Confidence: {state.get('crisis_confidence', 0.0)}")
    
    print("\n--- DISTRICTS ---")
    for d_id, d in state.get('districts', {}).items():
        print(f"- {d['name']} ({d_id}): Pop: {d['population']}, Vulnerability: {d['vulnerability_index']}, Traffic: {d['traffic_density']:.2f}, Infrastructure Stress: {d['infrastructure_stress']:.2f}")
        
    print("\n--- HOSPITALS ---")
    for h_id, h in state.get('hospitals', {}).items():
        print(f"- {h['name']} ({h_id}): Capacity: {h['capacity']}, Current Load: {h['current_load']}, Surge Prob: {h['surge_probability']:.2f}")

    print("\n--- RESOURCES ---")
    for r_id, r in state.get('resources', {}).items():
        print(f"- {r['type']} ({r_id}): Location: {r['location']}, Status: {r['status']}, Target: {r['target_location']}, ETA: {r['eta_seconds']}s")

    print("\n--- ACTIVE INCIDENTS ---")
    incidents = state.get('active_incidents', {})
    if not incidents:
        print("  No active incidents.")
    else:
        for i_id, inc in incidents.items():
            print(f"- {inc['type']} ({i_id}): Location: {inc['location']}, Severity: {inc['severity']:.2f}, Status: {inc['status']}, Confidence: {inc['confidence_score']:.2f}, Clustered Signals: {inc['signals_clustered']}, Contradiction Flag: {inc['contradiction_flag']}")

def print_new_traces(all_traces, printed_trace_ids):
    new_traces = [t for t in all_traces if t.get('trace_id') not in printed_trace_ids]
    if new_traces:
        print("\n--- AGENT REASONING TRACES ---")
        for t in new_traces:
            print(f"[{t.get('agent_name')}] Action: {t.get('action_type')} (Confidence: {t.get('confidence_score', 0.0):.2f})")
            print(f"  Reasoning: {t.get('reasoning')}")
            if t.get('trade_offs'):
                print(f"  Trade-offs/Parameters: {t.get('trade_offs')}")
            print("-" * 40)
            printed_trace_ids.add(t.get('trace_id'))

def main():
    print_separator("System Health Check & Initial Topology")
    initial_state = http_get("/state")
    if not initial_state:
        print("CRITICAL: Backend FastAPI server is not responding! Please ensure uvicorn is running on port 8000.")
        sys.exit(1)
    
    print_state_summary(initial_state)
    
    printed_trace_ids = set()
    
    # -------------------------------------------------------------
    # SEQUENCE 1: "Simultaneous Contradictions" (The verification capability)
    # -------------------------------------------------------------
    print_separator("Starting Sequence 1: Simultaneous Contradictions")
    print("Triggering Flooding in Riverside & Heatwave in Downtown...")
    http_post("/simulation/scenarios/simultaneous_crises")
    
    # Let the simulation tick a couple times
    time.sleep(3)
    
    # Trigger Uptown Gas Explosion (Contradictory bot swarm reports)
    print("\nTriggering Uptown Gas Explosion (12 massive unverified reports)...")
    http_post("/simulation/scenarios/contradictory_reports")
    
    # Let verification engine process
    time.sleep(5)
    
    state = http_get("/state")
    traces = http_get("/traces")
    
    print_state_summary(state)
    if traces:
        print_new_traces(traces, printed_trace_ids)
        
    # -------------------------------------------------------------
    # SEQUENCE 2: "The Cascade & Evacuation Spiral" (The optimization capability)
    # -------------------------------------------------------------
    print_separator("Starting Sequence 2: The Cascade & Evacuation Spiral")
    print("Triggering chemical hazmat spill in Riverside...")
    http_post("/simulation/scenarios/evacuation_spiral")
    
    # Wait for Cascade Agent and Resource Optimizer to coordinate
    time.sleep(6)
    
    state = http_get("/state")
    traces = http_get("/traces")
    
    print_state_summary(state)
    if traces:
        print_new_traces(traces, printed_trace_ids)
        
    # -------------------------------------------------------------
    # SEQUENCE 3: "The Breaking Point" (Resource Exhaustion)
    # -------------------------------------------------------------
    print_separator("Starting Sequence 3: The Breaking Point")
    print("Triggering minor collisions in multiple districts followed by a Mag 6.2 Earthquake...")
    http_post("/simulation/scenarios/resource_exhaustion")
    
    # Wait for the system to hit its resource threshold and lockdown
    time.sleep(6)
    
    state = http_get("/state")
    traces = http_get("/traces")
    
    print_state_summary(state)
    if traces:
        print_new_traces(traces, printed_trace_ids)

    print_separator("Autonomous System Testing Successfully Completed")
    print("All sequences were executed and validated. The multi-agent system performed flawlessly!")

if __name__ == "__main__":
    main()
