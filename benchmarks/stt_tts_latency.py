#!/usr/bin/env python3
"""Latency benchmark for the STT/TTS providers voice-ai-agent uses.

Mirrors the exact wire protocols in that repo's app/stt/*.py and
app/tts/cartesia_provider.py (same URLs, same auth headers, same audio
format), reimplemented here rather than imported, to keep this repo free of
a dependency on voice-ai-agent's codebase.

Two things are measured, since they need real credentials and this isn't a
conversation loop:

  - Connect latency: time to open the STT websocket (Deepgram, Cartesia).
    Always measured; needs no audio.
  - TTS time-to-first-byte and total synthesis time: time from sending a
    sample line of text to Cartesia to the first audio chunk, and to the
    "done" message.

Pass --audio-file to also measure STT time-to-first-transcript, streaming a
mulaw/8000/mono file to each STT provider and timing the first result.

Usage:
    export DEEPGRAM_API_KEY=...
    export CARTESIA_API_KEY=...
    python benchmarks/stt_tts_latency.py [--runs 5] [--audio-file sample.raw]
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import time
import uuid

import websockets

DEEPGRAM_URL = (
    "wss://api.deepgram.com/v1/listen"
    "?encoding=mulaw&sample_rate=8000&channels=1"
    "&punctuate=true&interim_results=true&endpointing=300&smart_format=true"
)
CARTESIA_STT_URL = (
    "wss://api.cartesia.ai/stt/websocket"
    "?model={model}&encoding=pcm_mulaw&sample_rate=8000&cartesia_version=2026-03-01"
)
CARTESIA_TTS_URL = "wss://api.cartesia.ai/tts/websocket?cartesia_version=2026-03-01"

CARTESIA_STT_MODEL = os.environ.get("CARTESIA_STT_MODEL", "ink-whisper")
CARTESIA_TTS_MODEL_ID = os.environ.get("CARTESIA_TTS_MODEL_ID", "sonic-3")
CARTESIA_TTS_VOICE_ID = os.environ.get("CARTESIA_TTS_VOICE_ID", "e07c00bc-4134-4eae-9ea4-1a55fb45746b")
SAMPLE_TTS_TEXT = "Hello, I understand your calls have been dropping. Let me check that for you."


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"{name} is not set -- export it before running this benchmark.")
    return value


def percentile(values: list[float], p: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round(p / 100 * (len(ordered) - 1))))
    return ordered[index]


def report(label: str, values_ms: list[float]) -> None:
    print(f"{label}: p50={percentile(values_ms, 50):.1f}ms  p95={percentile(values_ms, 95):.1f}ms  n={len(values_ms)}")


async def measure_deepgram_connect(api_key: str) -> float:
    start = time.perf_counter()
    async with websockets.connect(DEEPGRAM_URL, additional_headers={"Authorization": f"Token {api_key}"}):
        return (time.perf_counter() - start) * 1000


async def measure_cartesia_stt_connect(api_key: str) -> float:
    url = CARTESIA_STT_URL.format(model=CARTESIA_STT_MODEL)
    start = time.perf_counter()
    async with websockets.connect(url, additional_headers={"X-API-Key": api_key}):
        return (time.perf_counter() - start) * 1000


async def measure_cartesia_tts(api_key: str) -> tuple[float, float]:
    """Returns (time_to_first_byte_ms, total_synthesis_ms)."""
    start = time.perf_counter()
    first_byte_at: float | None = None
    async with websockets.connect(CARTESIA_TTS_URL, additional_headers={"X-Api-Key": api_key}) as ws:
        await ws.send(
            json.dumps(
                {
                    "model_id": CARTESIA_TTS_MODEL_ID,
                    "transcript": SAMPLE_TTS_TEXT,
                    "voice": {"mode": "id", "id": CARTESIA_TTS_VOICE_ID},
                    "output_format": {"container": "raw", "encoding": "pcm_mulaw", "sample_rate": 8000},
                    "context_id": str(uuid.uuid4()),
                }
            )
        )
        async for raw in ws:
            message = json.loads(raw)
            msg_type = message.get("type")
            if msg_type == "chunk":
                if first_byte_at is None:
                    first_byte_at = time.perf_counter()
            elif msg_type == "error":
                raise RuntimeError(f"Cartesia TTS error: {message}")
            elif msg_type == "done":
                break
    total_at = time.perf_counter()
    if first_byte_at is None:
        raise RuntimeError("Cartesia TTS returned no audio chunks")
    return (first_byte_at - start) * 1000, (total_at - start) * 1000


async def measure_deepgram_roundtrip(api_key: str, audio: bytes) -> float:
    start = time.perf_counter()
    async with websockets.connect(DEEPGRAM_URL, additional_headers={"Authorization": f"Token {api_key}"}) as ws:
        await ws.send(audio)
        async for raw in ws:
            message = json.loads(raw)
            if message.get("type") != "Results":
                continue
            alternatives = message.get("channel", {}).get("alternatives", [])
            if alternatives and alternatives[0].get("transcript"):
                return (time.perf_counter() - start) * 1000
    raise RuntimeError("Deepgram returned no transcript")


async def measure_cartesia_stt_roundtrip(api_key: str, audio: bytes) -> float:
    url = CARTESIA_STT_URL.format(model=CARTESIA_STT_MODEL)
    start = time.perf_counter()
    async with websockets.connect(url, additional_headers={"X-API-Key": api_key}) as ws:
        await ws.send(audio)
        async for raw in ws:
            message = json.loads(raw)
            if message.get("type") == "transcript" and message.get("text"):
                return (time.perf_counter() - start) * 1000
    raise RuntimeError("Cartesia STT returned no transcript")


async def main_async(runs: int, audio_file: str | None) -> None:
    deepgram_key = _require_env("DEEPGRAM_API_KEY")
    cartesia_key = _require_env("CARTESIA_API_KEY")

    print(f"Running {runs} iterations per measurement...\n")

    deepgram_connect = [await measure_deepgram_connect(deepgram_key) for _ in range(runs)]
    report("Deepgram STT connect", deepgram_connect)

    cartesia_connect = [await measure_cartesia_stt_connect(cartesia_key) for _ in range(runs)]
    report("Cartesia STT connect", cartesia_connect)

    ttfb, total = [], []
    for _ in range(runs):
        f, t = await measure_cartesia_tts(cartesia_key)
        ttfb.append(f)
        total.append(t)
    report("Cartesia TTS time-to-first-byte", ttfb)
    report("Cartesia TTS total synthesis", total)

    if audio_file:
        with open(audio_file, "rb") as fh:
            audio = fh.read()
        deepgram_rt = [await measure_deepgram_roundtrip(deepgram_key, audio) for _ in range(runs)]
        report("Deepgram STT time-to-first-transcript", deepgram_rt)
        cartesia_rt = [await measure_cartesia_stt_roundtrip(cartesia_key, audio) for _ in range(runs)]
        report("Cartesia STT time-to-first-transcript", cartesia_rt)
    else:
        print("\n(Pass --audio-file <mulaw/8000/mono raw file> to also measure time-to-first-transcript.)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--audio-file", default=None, help="Raw mulaw/8000/mono audio file for STT round-trip timing")
    args = parser.parse_args()
    asyncio.run(main_async(args.runs, args.audio_file))


if __name__ == "__main__":
    main()
