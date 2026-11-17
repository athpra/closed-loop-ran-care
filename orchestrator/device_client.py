"""Client side of the A2A-T-shaped exchange with the device agent.

Calls device_agent.a2a_server directly in-process today. Kept as its own
module, rather than inlined into decision.py, so swapping this for a real
network call later touches one file.
"""

from __future__ import annotations

from device_agent.a2a_server import handle_task


class DeviceAgentError(RuntimeError):
    pass


def get_device_signals(scenario: str) -> dict:
    response = handle_task("get_device_signals", {"scenario": scenario})
    if response["status"] != "completed":
        raise DeviceAgentError(response.get("error", "device agent task failed"))
    return response["artifacts"][0]["data"]
