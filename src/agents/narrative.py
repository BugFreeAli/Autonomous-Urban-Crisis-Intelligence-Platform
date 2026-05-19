"""Plain-language helpers for agent logs shown in the terminal and Operations tab."""

from typing import List, Optional

SECTOR_NAMES = {
    "D1": "Downtown",
    "D2": "Riverside",
    "D3": "Uptown",
    "Downtown": "Downtown",
    "Riverside": "Riverside",
    "Uptown": "Uptown",
}


def sector(loc: str) -> str:
    return SECTOR_NAMES.get(loc, loc)


def pct(value: float) -> str:
    return f"{round(value * 100)}%"


def signal_cluster_summary(loc: str, crisis_type: str, signal_count: int) -> str:
    where = sector(loc)
    return (
        f"Multiple independent reports are lining up in {where}. "
        f"I am treating this as a possible {crisis_type} based on {signal_count} signals in the last few minutes. "
        f"Next step: send this to verification before we alert the public or move units."
    )


def verification_thinking(trace_lines: List[str], action: str, confidence: float, loc: str, crisis_type: str) -> str:
    bullets = "\n".join(f"  • {line}" for line in trace_lines)
    conf = pct(confidence)
    where = sector(loc)
    if action == "CONFIRM":
        tail = f"I am confident enough ({conf}) to treat the {crisis_type} in {where} as real and move to crisis classification."
    elif action == "RETRACT":
        tail = f"Confidence is only {conf}. I am cancelling this alert — it looks like noise or misinformation."
    elif action == "MERGE":
        tail = f"This looks like the same event we are already tracking in {where}. I will merge duplicate reports instead of opening a second incident."
    elif action == "ESCALATE_HUMAN":
        tail = f"Signals conflict ({conf} confidence). I am pausing auto-response until a human operator confirms."
    else:
        tail = f"Current confidence: {conf}."
    return f"What I checked:\n{bullets}\n\nDecision: {tail}"


def verification_outcome_headline(action: str, loc: str, crisis_type: str) -> str:
    where = sector(loc)
    if action == "CONFIRM":
        return f"Verified — {crisis_type} in {where} is credible"
    if action == "RETRACT":
        return f"Retracted false alarm in {where}"
    if action == "MERGE":
        return f"Merged duplicate reports in {where}"
    if action == "ESCALATE_HUMAN":
        return f"Human review required for {where}"
    return f"Verification complete for {where}"


def verification_outcome_body(action: str, confidence: float, loc: str, crisis_type: str) -> str:
    where = sector(loc)
    conf = pct(confidence)
    if action == "CONFIRM":
        return (
            f"The city will open an official incident for {crisis_type} in {where} "
            f"at {conf} confidence. Resource and communications agents are being notified."
        )
    if action == "RETRACT":
        return (
            f"No public alert will be issued for {where}. "
            f"Any draft warnings are pulled and the situation stays at normal watch level."
        )
    if action == "MERGE":
        return f"All new signals in {where} attach to the existing incident so we do not double-count the crisis."
    if action == "ESCALATE_HUMAN":
        return (
            f"Automatic dispatch is on hold for {where}. "
            f"Command staff must confirm before ambulances or public alerts go out."
        )
    return f"Verification finished with {conf} confidence."
