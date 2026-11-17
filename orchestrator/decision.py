"""Self-resolve vs. escalate.

A simple, explicit threshold rule -- not an LLM call -- kept auditable and
self-contained for this repo's first version. The real reasoning step
(likely reusing voice-ai-agent's LLM, or the NOC agent's own LangGraph
reasoning) is a deliberate later swap-in; see docs/architecture.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Outcome = Literal["self_resolved", "escalated", "no_issue_found"]

# A handover failure rate at or above this, combined with at least one
# dropped call, matches the PCI-confusion-like pattern the device signals
# alone are enough to explain -- below it, something is still wrong but the
# device agent's evidence doesn't pin down why, so it needs NOC involvement.
_HANDOVER_FAILURE_RATE_THRESHOLD = 0.5


@dataclass(frozen=True)
class Decision:
    outcome: Outcome
    message: str


def decide(signals: dict, complaint: str) -> Decision:
    attempts = signals["recent_handover_attempts"]
    failures = signals["recent_handover_failures"]
    drops = signals["recent_call_drops"]
    failure_rate = (failures / attempts) if attempts else 0.0

    if drops == 0:
        return Decision(
            outcome="no_issue_found",
            message=(
                f"Device signals on {signals['serving_cell_id']} look healthy "
                f"(RSRP {signals['rsrp_dbm']} dBm, RSRQ {signals['rsrq_db']} dB) -- "
                "no corroborating evidence for the complaint."
            ),
        )

    if failure_rate >= _HANDOVER_FAILURE_RATE_THRESHOLD:
        return Decision(
            outcome="self_resolved",
            message=(
                f"Handover failure rate on {signals['serving_cell_id']} is "
                f"{failure_rate:.0%} ({failures}/{attempts}), consistent with a "
                "PCI-confusion-like pattern -- explains the complaint without "
                "needing a NOC investigation."
            ),
        )

    return Decision(
        outcome="escalated",
        message=(
            f"{drops} dropped call(s) on {signals['serving_cell_id']} but "
            f"handover failure rate is only {failure_rate:.0%} -- device "
            "signals alone don't explain it."
        ),
    )
