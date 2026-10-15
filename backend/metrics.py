"""Lightweight in-process ingest metrics.

Records a bounded ring buffer of recent event timings so the dashboard can show
"events per second, avg write latency, p99 write latency" live. Kept in-memory
on purpose — a production system would export to Prometheus or push to Redis
for cross-worker aggregation; here one gunicorn worker is enough for the demo.
"""
import threading
from collections import deque
from time import monotonic

_LOCK = threading.Lock()
_EVENTS: "deque[tuple[float, float]]" = deque(maxlen=10000)  # (monotonic_ts, latency_ms)
_LIFETIME = 0


def record_ingest(latency_ms: float) -> None:
    global _LIFETIME
    with _LOCK:
        _EVENTS.append((monotonic(), latency_ms))
        _LIFETIME += 1


def snapshot(window_seconds: float = 60.0) -> dict:
    now = monotonic()
    cutoff = now - window_seconds
    with _LOCK:
        recent = [lat for ts, lat in _EVENTS if ts >= cutoff]
        lifetime = _LIFETIME

    if not recent:
        return {
            "window_seconds": window_seconds,
            "events_in_window": 0,
            "events_per_second": 0.0,
            "avg_latency_ms": 0.0,
            "p99_latency_ms": 0.0,
            "lifetime_events": lifetime,
        }

    recent.sort()
    p99_idx = min(len(recent) - 1, int(0.99 * len(recent)))
    return {
        "window_seconds": window_seconds,
        "events_in_window": len(recent),
        "events_per_second": round(len(recent) / window_seconds, 2),
        "avg_latency_ms": round(sum(recent) / len(recent), 2),
        "p99_latency_ms": round(recent[p99_idx], 2),
        "lifetime_events": lifetime,
    }
