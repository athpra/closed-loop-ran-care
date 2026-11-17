# Closed-Loop RAN Care

Concept note for the **AI-RAN Alliance, Working Group 3 (AI-on-RAN)**: a single agent that hears a customer's problem, reads it against live RAN signals, and proposes the fix a NOC engineer would — with a person still deciding what touches the network.

This repo is the shared home for a concept that spans two working prototypes:

- **[voice-ai-agent](https://github.com/athpra/voice-ai)** — real-time phone calls over Twilio Media Streams, LLM reasoning grounded in account context, served by Cloudera AI Inference Service.
- **[mobile-noc-agent-demo](https://github.com/athpra/mobile-noc-agent-demo)** — a LangGraph agent that investigates a staged PCI-confusion fault on a synthetic radio network, proposes a fix, and pauses for human approval.

Neither of those repos owns this concept on its own, so it lives here instead — along with the follow-up work scoped out of WG3's feedback on it (see Section 08 of the concept note).

## What's in this repo

**Concept and deck:**
- [`docs/concept-note.md`](docs/concept-note.md) — the full write-up: the gap today, the proposed architecture, a certified-ontology layer for grounding the network agent's reasoning, a worked example, an honest proven-vs-proposed breakdown, and (Section 08) the WG3 feedback and what it scopes next.
- [`deck/Closed-Loop-RAN-Care.pptx`](deck/Closed-Loop-RAN-Care.pptx) — the slide deck for the WG3 face-to-face presentation.

**Edge-inferencing and on-device agent follow-up work**, scoped from that feedback:
- [`device_agent/`](device_agent/) — an emulated on-device agent: synthetic UE-side radio signals, served over a simplified, illustrative approximation of TM Forum's A2A-T (`IG1453`/`IG1453A`) message shape. See the caveat in [`docs/architecture.md`](docs/architecture.md) — not verified against the published spec text.
- [`orchestrator/`](orchestrator/) — queries the device agent, decides whether its signals resolve the complaint outright or need NOC escalation, and (for escalation) calls a stub toward `mobile-noc-agent-demo`.
- [`demo/run_demo.py`](demo/run_demo.py) — a standalone CLI that drives the orchestration logic against a scripted caller complaint, with no dependency on a live phone call.
- [`benchmarks/stt_tts_latency.py`](benchmarks/stt_tts_latency.py) — times each leg of the STT/TTS providers `voice-ai-agent` uses (Deepgram, Cartesia), to put real numbers behind the edge-inferencing latency argument.
- [`docs/architecture.md`](docs/architecture.md) and [`docs/device-log-model.md`](docs/device-log-model.md) — the orchestration design, the A2A-T caveat, and the synthetic device-signal schema (modeled on 3GPP's UE-side mechanisms, since no TM Forum spec covers device-log content).

## Running the new code

```bash
pip install -r requirements.txt
python demo/run_demo.py --scenario self-resolve
python demo/run_demo.py --scenario escalate
```

Both scenarios run entirely in-process, synthetic, no API keys needed. The STT/TTS benchmark needs real credentials (`DEEPGRAM_API_KEY`, `CARTESIA_API_KEY`) since it makes live calls — see `benchmarks/stt_tts_latency.py`'s docstring.

## Status

Both prototypes exist today and run independently. A first slice of the correlation between them — a caller's home cell checked against a known-issue lookup — now runs end to end inside `voice-ai-agent`. The two agents' reasoning and data planes have not yet been joined; see the concept note's "What's proven today, and what's proposed" section for the full breakdown.

The device agent, orchestrator, and benchmark harness here are newer still: the device agent is synthetic, the A2A-T message shape is illustrative pending a check against the real spec, and the NOC client is a mock. None of it is "proven" in the sense the concept note's table uses that word.
