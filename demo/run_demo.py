#!/usr/bin/env python3
"""Standalone CLI demo of the orchestration logic.

Stands in for a live phone call: a scripted "caller complaint" drives the
same path a real call would take through orchestrator/decision.py, with no
dependency on voice-ai-agent or Twilio.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from orchestrator.decision import decide
from orchestrator.device_client import get_device_signals
from orchestrator.noc_client import escalate

_SCENARIOS = {
    "self-resolve": {
        "complaint": "My calls keep dropping near my house.",
        "device_scenario": "pci-confusion",
    },
    "escalate": {
        "complaint": "I had a call drop earlier today, not sure why.",
        "device_scenario": "unexplained",
    },
}


def run(scenario_name: str) -> None:
    scenario = _SCENARIOS[scenario_name]
    complaint = scenario["complaint"]

    print(f"Caller: \"{complaint}\"\n")

    signals = get_device_signals(scenario["device_scenario"])
    print("Device agent returned signals:")
    for key, value in signals.items():
        print(f"  {key}: {value}")
    print()

    decision = decide(signals, complaint)
    print(f"Decision: {decision.outcome}")
    print(f"  {decision.message}\n")

    if decision.outcome == "escalated":
        result = escalate(signals["serving_cell_id"], complaint)
        print("Escalated to NOC agent (stub):")
        for key, value in result.items():
            print(f"  {key}: {value}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=sorted(_SCENARIOS), required=True)
    args = parser.parse_args()
    run(args.scenario)


if __name__ == "__main__":
    main()
