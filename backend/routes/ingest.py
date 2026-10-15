"""POST /api/log — the single endpoint apps call to report errors."""
import logging
import uuid
from datetime import datetime, timezone
from time import perf_counter

import requests
from flask import Blueprint, request, jsonify

import config
import metrics
from cassandra_client import get_session, stmt
from fingerprint import extract_exception_type, extract_first_frame, fingerprint
from middleware.auth import require_app_api_key

log = logging.getLogger(__name__)
bp = Blueprint("ingest", __name__)

VALID_SEVERITIES = {"DEBUG", "INFO", "WARNING", "ERROR", "FATAL"}


def _hour_bucket(dt: datetime) -> datetime:
    # Store as tz-naive UTC so it round-trips through Cassandra as the same value
    # the driver returns on reads (which is also tz-naive UTC).
    return dt.replace(minute=0, second=0, microsecond=0, tzinfo=None)


@bp.post("/api/log")
@require_app_api_key
def ingest():
    t_start = perf_counter()
    body = request.get_json(silent=True) or {}
    app = body.get("app", "").strip()
    message = (body.get("message") or "").strip()
    stack = body.get("stack") or ""
    severity = (body.get("severity") or "ERROR").upper()

    if not message:
        return jsonify(error="'message' is required"), 400
    if severity not in VALID_SEVERITIES:
        severity = "ERROR"

    exception_type = extract_exception_type(message)
    first_frame = extract_first_frame(stack) or message
    issue_id = fingerprint(app, exception_type, first_frame)

    now = datetime.now(timezone.utc)
    event_id = uuid.uuid4()
    event_day = now.date()
    hour = _hour_bucket(now)

    s = get_session()

    # Try to create the issue; if it already exists we only touch last_seen.
    first_seen_result = s.execute(
        stmt("upsert_issue_first"),
        (issue_id, app, exception_type, message, first_frame, severity, now, now),
    )
    is_new_issue = bool(first_seen_result and first_seen_result.one().applied)
    if not is_new_issue:
        s.execute(stmt("touch_issue"), (now, severity, issue_id))

    # Keep the per-app index in sync.
    s.execute(
        stmt("upsert_issue_by_app"),
        (app, issue_id, exception_type, message, severity, "unresolved", now),
    )

    # Raw events (TTL'd).
    s.execute(
        stmt("insert_event_by_issue"),
        (issue_id, now, event_id, app, severity, message, stack, config.EVENT_TTL_SECONDS),
    )
    s.execute(
        stmt("insert_event_by_app_day"),
        (app, event_day, now, event_id, issue_id, severity, message, config.EVENT_TTL_SECONDS),
    )

    # Counters for charts and sparklines.
    s.execute(stmt("inc_issue_hour"), (issue_id, hour))
    s.execute(stmt("inc_app_hour"), (app, hour, severity))
    s.execute(stmt("inc_issue_total"), (app, issue_id))

    # Fire webhook on first-ever occurrence of an issue (demo: just log it,
    # or POST if the app has configured a URL).
    if is_new_issue:
        webhook = getattr(request, "app_record", None)
        url = webhook.webhook_url if webhook else ""
        if url:
            try:
                # verify=False keeps the demo working in slim containers that
                # ship without a system CA bundle. In production, bake
                # ca-certificates into the image or point certifi at a bundle.
                requests.post(
                    url,
                    json={
                        "event": "new_issue",
                        "app": app,
                        "issue_id": issue_id,
                        "exception_type": exception_type,
                        "message": message,
                    },
                    timeout=5,
                    verify=False,
                )
            except Exception as e:
                log.warning("Webhook POST failed: %s", e)
        log.info("NEW ISSUE %s in app=%s: %s", issue_id, app, exception_type)

    metrics.record_ingest((perf_counter() - t_start) * 1000.0)

    return jsonify(
        issue_id=issue_id,
        event_id=str(event_id),
        is_new_issue=is_new_issue,
    ), 201
