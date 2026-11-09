# Closed-Loop RAN Care

Concept note for the **AI-RAN Alliance, Working Group 3 (AI-on-RAN)**: a single agent that hears a customer's problem, reads it against live RAN signals, and proposes the fix a NOC engineer would — with a person still deciding what touches the network.

This repo is the shared home for a concept that spans two working prototypes:

- **[voice-ai-agent](https://github.com/athpra/voice-ai)** — real-time phone calls over Twilio Media Streams, LLM reasoning grounded in account context, served by Cloudera AI Inference Service.
- **[mobile-noc-agent-demo](https://github.com/athpra/mobile-noc-agent-demo)** — a LangGraph agent that investigates a staged PCI-confusion fault on a synthetic radio network, proposes a fix, and pauses for human approval.

Neither of those repos owns this concept on its own, so it lives here instead.

## What's in this repo

- [`docs/concept-note.md`](docs/concept-note.md) — the full write-up: the gap today, the proposed architecture, a certified-ontology layer for grounding the network agent's reasoning, a worked example, and an honest proven-vs-proposed breakdown.
- [`deck/Closed-Loop-RAN-Care.pptx`](deck/Closed-Loop-RAN-Care.pptx) — the slide deck for the WG3 face-to-face presentation.

## Status

Both prototypes exist today and run independently. A first slice of the correlation between them — a caller's home cell checked against a known-issue lookup — now runs end to end inside `voice-ai-agent`. The two agents' reasoning and data planes have not yet been joined; see the concept note's "What's proven today, and what's proposed" section for the full breakdown.
