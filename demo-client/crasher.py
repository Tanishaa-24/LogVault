"""Fire a steady stream of varied exceptions at LogVault.

Great for a demo: run it in one terminal, watch the dashboard fill up.

    python demo-client/crasher.py
    python demo-client/crasher.py --rate 5 --duration 60
"""
import argparse
import random
import time

from logvault_client import LogVault


APPS = [
    ("payments", "demo-key-payments"),
    ("checkout", "demo-key-checkout"),
    ("search", "demo-key-search"),
]


# ---- Fake failure modes. Each one, when called, raises a distinct exception.
# Fingerprinting should collapse repeat calls into one issue each.

def missing_key():
    data = {"amount": 100}
    return data["user_id"]  # noqa: F841

def bad_divide():
    totals = [10, 0, 20]
    return 1 / random.choice(totals)

def null_lookup():
    user = None
    return user.email  # noqa: F841

def bad_cast():
    val = "oops-not-a-number"
    return int(val)

def index_oob():
    arr = [1, 2, 3]
    return arr[random.randint(5, 10)]

def connection_timeout():
    raise ConnectionError("Connection to db-replica-3 timed out after 30s")

def permission_denied():
    raise PermissionError("User lacks role 'billing:write' for /api/charge")

def rate_limited():
    raise RuntimeError("Upstream rate limit hit (429 from stripe)")


# A warning-level event doesn't raise; emit it directly.
def slow_query_warning(client: LogVault):
    client.capture(
        message="Slow query: SELECT * FROM transactions took 4200ms",
        severity="WARNING",
    )


FAILURES = [missing_key, bad_divide, null_lookup, bad_cast, index_oob,
            connection_timeout, permission_denied, rate_limited]


def run(url: str, rate: float, duration: float, spike_issue: bool):
    clients = {app: LogVault(url, app, key) for app, key in APPS}
    interval = 1.0 / rate
    end = time.time() + duration
    sent = 0

    while time.time() < end:
        app, _ = random.choice(APPS)
        lv = clients[app]
        choice = random.random()

        if choice < 0.08:
            slow_query_warning(lv)
        else:
            fn = random.choice(FAILURES)
            try:
                fn()
            except Exception:
                sev = "FATAL" if fn is connection_timeout and random.random() < 0.3 else "ERROR"
                lv.capture_exception(severity=sev)

        sent += 1
        if sent % 10 == 0:
            print(f"sent {sent} events")

        time.sleep(interval)

    if spike_issue:
        print("Firing a spike burst (same KeyError 60x in one hour)")
        lv = clients["payments"]
        for _ in range(60):
            try:
                missing_key()
            except Exception:
                lv.capture_exception(severity="ERROR")
            time.sleep(0.05)

    print(f"Done. Total events: {sent}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate fake errors for LogVault")
    parser.add_argument("--url", default="http://localhost:5000")
    parser.add_argument("--rate", type=float, default=4.0, help="events per second")
    parser.add_argument("--duration", type=float, default=20.0, help="seconds")
    parser.add_argument("--spike", action="store_true", help="also fire a spike burst")
    args = parser.parse_args()
    run(args.url, args.rate, args.duration, args.spike)
