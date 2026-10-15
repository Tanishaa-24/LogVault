"""Issue management — list, view, resolve, annotate, delete."""
import secrets
from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request

import config
from cassandra_client import get_session, stmt

bp = Blueprint("issues", __name__)


def _row_to_issue(r) -> dict:
    return {
        "issue_id": r.issue_id,
        "app": r.app,
        "exception_type": r.exception_type,
        "message": r.message,
        "severity": r.severity,
        "status": r.status,
        "last_seen": r.last_seen.isoformat() if r.last_seen else None,
    }


def _hour_bucket(dt: datetime) -> datetime:
    return dt.replace(minute=0, second=0, microsecond=0, tzinfo=None)


@bp.get("/api/apps")
def list_apps():
    rows = get_session().execute(stmt("list_apps"))
    return jsonify([
        {
            "app_name": r.app_name,
            "api_key": r.api_key,
            "webhook_url": r.webhook_url or "",
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ])


@bp.patch("/api/apps/<app_name>")
def update_app(app_name):
    """Set the webhook URL that fires when a brand-new issue is seen."""
    body = request.get_json(silent=True) or {}
    row = get_session().execute(stmt("get_app"), (app_name,)).one()
    if row is None:
        return jsonify(error="unknown app"), 404
    webhook_url = (body.get("webhook_url") or "").strip()
    get_session().execute(stmt("update_app_webhook"), (webhook_url, app_name))
    return jsonify(ok=True, app_name=app_name, webhook_url=webhook_url)


@bp.post("/api/apps")
def create_app():
    """Register a new application. Auto-generates an API key if not supplied."""
    body = request.get_json(silent=True) or {}
    app_name = (body.get("app_name") or "").strip().lower()
    if not app_name or not app_name.replace("-", "").replace("_", "").isalnum():
        return jsonify(error="app_name must be alphanumeric (hyphens/underscores allowed)"), 400

    existing = get_session().execute(stmt("get_app"), (app_name,)).one()
    if existing:
        return jsonify(error=f"app '{app_name}' already exists"), 409

    api_key = (body.get("api_key") or f"key-{secrets.token_hex(8)}").strip()
    webhook_url = (body.get("webhook_url") or "").strip()
    now = datetime.now(timezone.utc)

    get_session().execute(
        stmt("upsert_app"), (app_name, api_key, webhook_url, now)
    )
    return jsonify(
        ok=True, app_name=app_name, api_key=api_key,
        webhook_url=webhook_url, created_at=now.isoformat(),
    ), 201


@bp.delete("/api/apps/<app_name>")
def delete_app(app_name):
    """Delete an app and all of its issues + counters.

    Raw events are left to TTL out naturally — deleting them would require
    scanning events_by_app_day across every past day, which isn't worth it
    when they expire on their own.
    """
    s = get_session()
    row = s.execute(stmt("get_app"), (app_name,)).one()
    if row is None:
        return jsonify(error="unknown app"), 404

    issue_rows = list(s.execute(stmt("list_issues_by_app_full"), (app_name,)))
    for ir in issue_rows:
        s.execute(stmt("delete_issue"), (ir.issue_id,))
        s.execute(stmt("delete_issue_by_app"), (app_name, ir.issue_id))
        s.execute(stmt("delete_issue_total"), (app_name, ir.issue_id))

    s.execute(stmt("delete_app"), (app_name,))
    return jsonify(ok=True, app_name=app_name, issues_deleted=len(issue_rows))


@bp.get("/api/issues")
def list_issues():
    """List issues for an app, with optional filters.

    Query params:
      app       — required, the app name
      severity  — optional, filter rows
      status    — optional, 'resolved' or 'unresolved'
      limit     — optional, default 100
    """
    app = request.args.get("app", "")
    if not app:
        return jsonify(error="query param 'app' is required"), 400
    severity = request.args.get("severity")
    status = request.args.get("status")
    limit = int(request.args.get("limit", 100))

    rows = list(get_session().execute(stmt("list_issues_by_app"), (app,)))
    issues = [_row_to_issue(r) for r in rows]

    if severity:
        issues = [i for i in issues if i["severity"] == severity.upper()]
    if status:
        issues = [i for i in issues if i["status"] == status.lower()]

    issues.sort(key=lambda i: i["last_seen"] or "", reverse=True)

    # Attach per-issue total count and spike flag so the dashboard can show them
    # without an extra round-trip per row.
    totals = {
        r.issue_id: int(r.count)
        for r in get_session().execute(stmt("list_issue_totals"), (app,))
    }

    now = datetime.now(timezone.utc)
    last_hour = _hour_bucket(now)
    lookback_start = last_hour - timedelta(hours=config.SPIKE_LOOKBACK_HOURS)

    for issue in issues[:limit]:
        issue["total_count"] = totals.get(issue["issue_id"], 0)
        issue["is_spiking"] = _is_spiking(issue["issue_id"], last_hour, lookback_start)

    return jsonify(issues[:limit])


def _is_spiking(issue_id: str, last_hour: datetime, lookback_start: datetime) -> bool:
    """True if the last hour's count exceeds SPIKE_MULTIPLIER × the prior average."""
    rows = list(
        get_session().execute(
            stmt("get_issue_hour_range"), (issue_id, lookback_start, last_hour)
        )
    )
    if len(rows) < 2:
        return False
    last_hour_count = 0
    prior_sum = 0
    prior_hours = 0
    for r in rows:
        if r.hour == last_hour:
            last_hour_count = int(r.count)
        else:
            prior_sum += int(r.count)
            prior_hours += 1
    if prior_hours == 0 or last_hour_count < 5:
        return False
    avg_prior = prior_sum / prior_hours
    return last_hour_count >= config.SPIKE_MULTIPLIER * max(avg_prior, 1)


@bp.get("/api/issues/<issue_id>")
def get_issue(issue_id):
    row = get_session().execute(stmt("get_issue"), (issue_id,)).one()
    if row is None:
        return jsonify(error="not found"), 404

    events = list(get_session().execute(stmt("list_events_by_issue"), (issue_id, 50)))

    now = datetime.now(timezone.utc)
    last_hour = _hour_bucket(now)
    start = last_hour - timedelta(hours=23)
    sparkline_rows = list(
        get_session().execute(stmt("get_issue_hour_range"), (issue_id, start, last_hour))
    )
    by_hour = {r.hour: int(r.count) for r in sparkline_rows}
    sparkline = []
    for i in range(24):
        hour = start + timedelta(hours=i)
        sparkline.append({"hour": hour.isoformat(), "count": by_hour.get(hour, 0)})

    return jsonify(
        issue={
            "issue_id": row.issue_id,
            "app": row.app,
            "exception_type": row.exception_type,
            "message": row.message,
            "first_frame": row.first_frame,
            "severity": row.severity,
            "status": row.status,
            "note": row.note or "",
            "first_seen": row.first_seen.isoformat() if row.first_seen else None,
            "last_seen": row.last_seen.isoformat() if row.last_seen else None,
        },
        events=[
            {
                "event_id": str(e.event_id),
                "event_time": e.event_time.isoformat(),
                "severity": e.severity,
                "message": e.message,
                "stack": e.stack,
            }
            for e in events
        ],
        sparkline=sparkline,
    )


@bp.patch("/api/issues/<issue_id>")
def update_issue(issue_id):
    body = request.get_json(silent=True) or {}
    row = get_session().execute(stmt("get_issue"), (issue_id,)).one()
    if row is None:
        return jsonify(error="not found"), 404

    new_status = body.get("status", row.status)
    new_note = body.get("note", row.note or "")
    if new_status not in {"resolved", "unresolved"}:
        return jsonify(error="status must be 'resolved' or 'unresolved'"), 400

    get_session().execute(stmt("update_issue_status"), (new_status, new_note, issue_id))
    get_session().execute(
        stmt("update_issue_by_app_status"), (new_status, row.app, issue_id)
    )
    return jsonify(ok=True)


@bp.delete("/api/issues/<issue_id>")
def delete_issue(issue_id):
    row = get_session().execute(stmt("get_issue"), (issue_id,)).one()
    if row is None:
        return jsonify(error="not found"), 404
    s = get_session()
    s.execute(stmt("delete_issue"), (issue_id,))
    s.execute(stmt("delete_issue_by_app"), (row.app, issue_id))
    s.execute(stmt("delete_issue_total"), (row.app, issue_id))
    # events_by_issue / events_by_app_day rows are left to TTL out naturally.
    return jsonify(ok=True)
