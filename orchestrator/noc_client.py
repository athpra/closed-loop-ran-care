"""Stub client for escalating to mobile-noc-agent-demo.

That repo doesn't expose an API today -- it's a LangGraph agent wired
directly into its own Streamlit app (see the "API-ify the NOC agent"
scoping from the closed-loop-ran-care concept note). This stub stands in
for that future API so the orchestrator's escalation path has something to
call and a response shape to design against, without touching that repo's
code.
"""

from __future__ import annotations

import uuid


def escalate(serving_cell_id: str, complaint: str) -> dict:
    """Pretend to hand off an investigation to the NOC agent.

    A real implementation would POST to mobile-noc-agent-demo's (not yet
    existing) investigation API and return its actual thread_id/status.
    """
    return {
        "thread_id": f"noc-stub-{uuid.uuid4().hex[:8]}",
        "status": "escalated",
        "cell_id": serving_cell_id,
        "note": (
            f"MOCK escalation for '{complaint}' on {serving_cell_id} -- "
            "mobile-noc-agent-demo has no real API to call yet."
        ),
    }
