"""Synthetic UE-side radio signals.

A static lookup table of staged scenarios, not a live connection to a real
handset -- see docs/device-log-model.md for what each field is modeled on.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class DeviceSignals:
    device_id: str
    timestamp: str
    serving_cell_id: str
    rsrp_dbm: int
    rsrq_db: float
    recent_handover_attempts: int
    recent_handover_failures: int
    recent_call_drops: int
    recent_retransmissions: int


_SCENARIOS: dict[str, DeviceSignals] = {
    "pci-confusion": DeviceSignals(
        device_id="demo-device-01",
        timestamp=datetime.now(timezone.utc).isoformat(),
        serving_cell_id="SC1188-C1",
        rsrp_dbm=-104,
        rsrq_db=-13.5,
        recent_handover_attempts=9,
        recent_handover_failures=6,
        recent_call_drops=2,
        recent_retransmissions=140,
    ),
    "healthy": DeviceSignals(
        device_id="demo-device-02",
        timestamp=datetime.now(timezone.utc).isoformat(),
        serving_cell_id="GNB1042-C1",
        rsrp_dbm=-82,
        rsrq_db=-7.0,
        recent_handover_attempts=2,
        recent_handover_failures=0,
        recent_call_drops=0,
        recent_retransmissions=12,
    ),
    "unexplained": DeviceSignals(
        device_id="demo-device-03",
        timestamp=datetime.now(timezone.utc).isoformat(),
        serving_cell_id="GNB1050-C2",
        rsrp_dbm=-88,
        rsrq_db=-9.0,
        recent_handover_attempts=3,
        recent_handover_failures=0,
        recent_call_drops=1,
        recent_retransmissions=30,
    ),
}


def get_signals(scenario: str) -> DeviceSignals:
    if scenario not in _SCENARIOS:
        raise KeyError(f"Unknown scenario '{scenario}'. Known: {sorted(_SCENARIOS)}")
    return _SCENARIOS[scenario]
