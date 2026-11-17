"""An in-process stand-in for an A2A-T message exchange.

IMPORTANT CAVEAT (see docs/architecture.md): this envelope shape is a
simplified, illustrative approximation built from public descriptions of
A2A-T / A2A (agent cards, tasks, artifacts) -- it has not been checked
against the normative TM Forum IG1453 text. Treat it as a placeholder to
replace once that spec is reviewed directly, not as a conformant
implementation.

It's an in-process function call rather than a real network service because
this repo's device agent is an emulation, not something deployed to a
handset. Swapping this for an HTTP/A2A-T transport later should only mean
changing how the envelope travels, not its shape.
"""

from __future__ import annotations

import uuid
from dataclasses import asdict
from typing import Any

from device_agent.signals import get_signals

AGENT_ID = "device-agent-emulated-v1"


def handle_task(skill: str, params: dict[str, Any]) -> dict[str, Any]:
    """Handle one A2A-T-shaped task request and return a task response envelope."""
    task_id = str(uuid.uuid4())

    if skill != "get_device_signals":
        return {
            "task_id": task_id,
            "agent_id": AGENT_ID,
            "status": "failed",
            "error": f"Unknown skill '{skill}'",
        }

    scenario = params.get("scenario")
    if not scenario:
        return {
            "task_id": task_id,
            "agent_id": AGENT_ID,
            "status": "failed",
            "error": "Missing required param 'scenario'",
        }

    signals = get_signals(scenario)
    return {
        "task_id": task_id,
        "agent_id": AGENT_ID,
        "status": "completed",
        "artifacts": [
            {
                "type": "device_signals",
                "data": asdict(signals),
            }
        ],
    }
