"""Charts: errors per hour, errors by severity, top noisy issues."""
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request

import metrics
from cassandra_client import get_session, stmt

bp = Blueprint("analytics", __name__)


@bp.get("/api/analytics/throughput")
def throughput():
    """Live ingest performance over the last 60 seconds."""
    return jsonify(metrics.snapshot())


def _hour_bucket(dt: datetime) -> datetime:
    return dt.replace(minute=0, second=0, microsecond=0, tzinfo=None)


@bp.get("/api/analytics/trend")
def trend():
    """Errors per hour for the last N hours, split by severity."""
    app = request.args.get("app", "")
    hours = int(request.args.get("hours", 24))
    if not app:
        return jsonify(error="query param 'app' is required"), 400

    now = datetime.now(timezone.utc)
    end = _hour_bucket(now)
    start = end - timedelta(hours=hours - 1)

    rows = list(get_session().execute(stmt("get_app_hour_range"), (app, start, end)))

    by_hour_sev = defaultdict(lambda: defaultdict(int))
    severities_seen = set()
    for r in rows:
        by_hour_sev[r.hour][r.severity] += int(r.count)
        severities_seen.add(r.severity)

    severity_order = ["DEBUG", "INFO", "WARNING", "ERROR", "FATAL"]
    severities = [s for s in severity_order if s in severities_seen]

    buckets = []
    for i in range(hours):
        hour = start + timedelta(hours=i)
        row = {"hour": hour.isoformat()}
        for sev in severities:
            row[sev] = by_hour_sev[hour].get(sev, 0)
        row["total"] = sum(row[sev] for sev in severities)
        buckets.append(row)

    return jsonify(hours=buckets, severities=severities)


@bp.get("/api/analytics/severity")
def severity_breakdown():
    """Totals by severity for the lookback window."""
    app = request.args.get("app", "")
    hours = int(request.args.get("hours", 24))
    if not app:
        return jsonify(error="query param 'app' is required"), 400

    now = datetime.now(timezone.utc)
    end = _hour_bucket(now)
    start = end - timedelta(hours=hours - 1)
    rows = list(get_session().execute(stmt("get_app_hour_range"), (app, start, end)))

    totals = defaultdict(int)
    for r in rows:
        totals[r.severity] += int(r.count)

    return jsonify(
        [{"severity": sev, "count": count} for sev, count in totals.items()]
    )


@bp.get("/api/analytics/top-issues")
def top_issues():
    """Top-N noisiest issues by lifetime count for a given app."""
    app = request.args.get("app", "")
    n = int(request.args.get("n", 5))
    if not app:
        return jsonify(error="query param 'app' is required"), 400

    totals = list(get_session().execute(stmt("list_issue_totals"), (app,)))
    totals.sort(key=lambda r: int(r.count), reverse=True)

    out = []
    for r in totals[:n]:
        issue = get_session().execute(stmt("get_issue"), (r.issue_id,)).one()
        if issue is None:
            continue
        out.append(
            {
                "issue_id": r.issue_id,
                "count": int(r.count),
                "exception_type": issue.exception_type,
                "message": issue.message,
                "severity": issue.severity,
                "status": issue.status,
            }
        )
    return jsonify(out)
