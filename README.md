# LogVault

A write-optimized error tracking and issue management system built on Apache
Cassandra. Applications POST their exceptions to a REST API, LogVault groups
identical errors into issues, and a React dashboard lets developers filter,
annotate, and resolve them.

> Mini-Sentry, built as a demonstration of Cassandra's strengths for
> high-volume, time-series, append-mostly workloads.

## Features

- **Ingest API** — any app can POST its errors; auth via per-app API key.
- **Automatic grouping** — SHA-256 fingerprint over `(app, exception_type,
  normalized_deepest_frame)` collapses repeated errors into one issue.
- **Dashboard** — React + Chart.js: trend chart, severity breakdown,
  top-5 noisiest issues, per-issue sparkline, filters, auto-refresh.
- **Spike detection** — issues whose last-hour count is ≥5× the prior
  24-hour average get a `SPIKE` badge.
- **Issue management** — mark resolved/unresolved, add a developer note,
  delete, inspect raw events with stack traces.
- **TTL retention** — raw event rows auto-expire after 30 days (configurable).
- **Live webhook delivery** — on a brand-new issue, POST to a configurable URL
  (set it per app from the dashboard; use webhook.site to see deliveries live).
- **Live performance panel** — events/sec, avg + p99 write latency, and
  lifetime event count on the dashboard, updated every 2 seconds.
- **Demo client** — `crasher.py` script continuously fires varied exceptions.

## Architecture

```
   Sample app / crasher ──POST /api/log──▶  Flask backend ──▶ Cassandra
                                                  ▲             (8 tables)
                                                  │
   React dashboard  ◀── GET /api/* ───────────────┘
   (Vite dev server)
```

Everything runs via Docker Compose:

| Service     | Port | What it is                          |
|-------------|------|-------------------------------------|
| cassandra   | 9042 | Apache Cassandra 4.1                |
| backend     | 5000 | Flask + Gunicorn API                |
| frontend    | 5173 | React + Vite dashboard              |

## Cassandra data model

One table per query pattern — standard Cassandra denormalization.

| Table                        | Purpose                                       |
|------------------------------|-----------------------------------------------|
| `apps`                       | Registered apps and their API keys            |
| `issues`                     | Canonical issue record, keyed by fingerprint  |
| `issues_by_app`              | List issues per app for the dashboard         |
| `events_by_issue`            | Timeline of raw events (TTL'd)                |
| `events_by_app_day`          | Recent events per app/day (TTL'd)             |
| `event_count_by_issue_hour`  | Counter: per-issue sparkline source           |
| `event_count_by_app_hour`    | Counter: trend chart source                   |
| `issue_total_count`          | Counter: lifetime count, top-noisy source     |

See `backend/schema.cql` for the full DDL.

## Running

**Requirements:** Docker Desktop. Nothing else.

```bash
cd ~/logvault
docker compose up -d --build
```

First boot takes ~90 seconds while Cassandra bootstraps. Watch progress:

```bash
docker compose logs -f backend
```

Open the dashboard: http://localhost:5173

### Generate demo data

In another terminal:

```bash
cd ~/logvault
python3 demo-client/crasher.py --rate 5 --duration 30 --spike
```

Refresh the dashboard; you should see three apps populate with issues,
a trend chart, severity breakdown, and a `SPIKE` badge on the ValueError
after the burst.

### Show spike detection firing in a fresh demo

Spike detection compares the current hour's count to the preceding hours'
average, so it needs at least two hours of data. On a fresh install, use the
backfill helper to seed low-volume historical data; the crasher's spike burst
will then light up the `SPIKE` badge immediately.

```bash
pip3 install cassandra-driver   # one-time, on your host
python3 demo-client/seed_history.py --app payments --hours 6 --per-hour 2
python3 demo-client/crasher.py --rate 10 --duration 10 --spike
```

### Demo the live webhook

1. Open https://webhook.site in another tab — it generates a unique URL for you.
2. Copy that URL into the "Webhook" field on the LogVault dashboard, click Save.
3. In a terminal: `python3 demo-client/crasher.py --rate 2 --duration 10`
4. Watch the webhook.site tab — new issues trigger a POST in real time.

### Demo the throughput panel

Simply run the crasher at a decent rate while the dashboard is open:

```bash
python3 demo-client/crasher.py --rate 20 --duration 60
```

The "Live ingest performance" panel shows events/sec climbing, write latency
staying flat under load, and lifetime events ticking up.

### Shut down

```bash
docker compose down         # keep the data
docker compose down -v      # also wipe Cassandra
```

## REST API

All responses are JSON.

### Ingest (requires `X-API-Key` header)

`POST /api/log`
```json
{"app": "payments", "severity": "ERROR",
 "message": "KeyError: 'user_id'", "stack": "Traceback..."}
```
Returns `{"issue_id": "...", "event_id": "...", "is_new_issue": true}`.

### Browse

- `GET /api/apps`
- `GET /api/issues?app=payments&severity=ERROR&status=unresolved&limit=100`
- `GET /api/issues/<issue_id>` — issue + recent events + 24h sparkline
- `PATCH /api/issues/<issue_id>` — body `{"status": "resolved", "note": "..."}`
- `DELETE /api/issues/<issue_id>`

### Analytics

- `GET /api/analytics/trend?app=payments&hours=24`
- `GET /api/analytics/severity?app=payments&hours=24`
- `GET /api/analytics/top-issues?app=payments&n=5`

### Health

- `GET /healthz`

## Using the client library in your own code

```python
from logvault_client import LogVault

lv = LogVault("http://localhost:5000", app="payments", api_key="demo-key-payments")

try:
    do_thing()
except Exception:
    lv.capture_exception()
```

## Configuration

Set these env vars on the `backend` service in `docker-compose.yml`:

| Variable                | Default    | Meaning                                 |
|-------------------------|------------|-----------------------------------------|
| `EVENT_TTL_SECONDS`     | 2592000    | Raw event retention (30 days)           |
| `SPIKE_MULTIPLIER`      | 5.0        | How many × avg to count as a spike      |
| `SPIKE_LOOKBACK_HOURS`  | 24         | Window used to compute the average      |

## Seeded apps and API keys

| App       | API key                 |
|-----------|-------------------------|
| payments  | `demo-key-payments`     |
| checkout  | `demo-key-checkout`     |
| search    | `demo-key-search`       |

To add more apps, insert into the `apps` table or extend
`cassandra-init/seed.cql` and re-run `docker compose up -d`.

## Why Cassandra?

- **Writes are cheap, random reads are rare.** Ingest dominates and
  Cassandra's LSM-tree storage is designed for exactly this.
- **Partitioned by app or issue.** All queries hit one partition, so there
  are no cross-node scans.
- **Native TTL.** Row-level `USING TTL` means retention is automatic — no
  cron job walking the data.
- **Counter columns** fit the aggregate workload without CAS contention.
