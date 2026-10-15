import logging
import time

from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy

import config

log = logging.getLogger(__name__)

_session = None
_prepared: dict = {}


def _connect():
    cluster = Cluster(
        contact_points=config.CASSANDRA_HOSTS,
        port=config.CASSANDRA_PORT,
        load_balancing_policy=DCAwareRoundRobinPolicy(),
        protocol_version=5,
    )
    session = cluster.connect()
    session.set_keyspace(config.CASSANDRA_KEYSPACE)
    return session


def get_session():
    """Return a shared Cassandra session, retrying while the cluster warms up."""
    global _session
    if _session is not None:
        return _session

    last_err = None
    for attempt in range(1, 31):
        try:
            _session = _connect()
            log.info("Connected to Cassandra on attempt %d", attempt)
            return _session
        except Exception as e:
            last_err = e
            log.warning("Cassandra not ready (attempt %d): %s", attempt, e)
            time.sleep(2)
    raise RuntimeError(f"Could not connect to Cassandra: {last_err}")


# ---- Prepared statements -----------------------------------------------------
# Prepared once per process, reused everywhere. Keeps query strings in one place.

STATEMENTS = {
    # apps / auth
    "get_app": "SELECT app_name, api_key, webhook_url FROM apps WHERE app_name = ?",
    "list_apps": "SELECT app_name, api_key, webhook_url, created_at FROM apps",
    "upsert_app": (
        "INSERT INTO apps (app_name, api_key, webhook_url, created_at) "
        "VALUES (?, ?, ?, ?)"
    ),
    "update_app_webhook": (
        "UPDATE apps SET webhook_url = ? WHERE app_name = ?"
    ),
    "delete_app": "DELETE FROM apps WHERE app_name = ?",
    "list_issues_by_app_full": (
        "SELECT issue_id FROM issues_by_app WHERE app = ?"
    ),
    # issues
    "get_issue": (
        "SELECT issue_id, app, exception_type, message, first_frame, severity, "
        "first_seen, last_seen, status, note FROM issues WHERE issue_id = ?"
    ),
    "upsert_issue_first": (
        "INSERT INTO issues (issue_id, app, exception_type, message, first_frame, "
        "severity, first_seen, last_seen, status, note) VALUES "
        "(?, ?, ?, ?, ?, ?, ?, ?, 'unresolved', '') IF NOT EXISTS"
    ),
    "touch_issue": "UPDATE issues SET last_seen = ?, severity = ? WHERE issue_id = ?",
    "update_issue_status": "UPDATE issues SET status = ?, note = ? WHERE issue_id = ?",
    "delete_issue": "DELETE FROM issues WHERE issue_id = ?",
    # issues_by_app index
    "upsert_issue_by_app": (
        "INSERT INTO issues_by_app (app, issue_id, exception_type, message, severity, "
        "status, last_seen) VALUES (?, ?, ?, ?, ?, ?, ?)"
    ),
    "list_issues_by_app": (
        "SELECT app, issue_id, exception_type, message, severity, status, last_seen "
        "FROM issues_by_app WHERE app = ?"
    ),
    "update_issue_by_app_status": (
        "UPDATE issues_by_app SET status = ? WHERE app = ? AND issue_id = ?"
    ),
    "delete_issue_by_app": "DELETE FROM issues_by_app WHERE app = ? AND issue_id = ?",
    # events_by_issue (TTL applied in route code)
    "insert_event_by_issue": (
        "INSERT INTO events_by_issue (issue_id, event_time, event_id, app, severity, "
        "message, stack) VALUES (?, ?, ?, ?, ?, ?, ?) USING TTL ?"
    ),
    "list_events_by_issue": (
        "SELECT issue_id, event_time, event_id, app, severity, message, stack "
        "FROM events_by_issue WHERE issue_id = ? LIMIT ?"
    ),
    # events_by_app_day
    "insert_event_by_app_day": (
        "INSERT INTO events_by_app_day (app, day, event_time, event_id, issue_id, "
        "severity, message) VALUES (?, ?, ?, ?, ?, ?, ?) USING TTL ?"
    ),
    "list_events_by_app_day": (
        "SELECT app, day, event_time, event_id, issue_id, severity, message "
        "FROM events_by_app_day WHERE app = ? AND day = ? LIMIT ?"
    ),
    # counters
    "inc_issue_hour": (
        "UPDATE event_count_by_issue_hour SET count = count + 1 "
        "WHERE issue_id = ? AND hour = ?"
    ),
    "get_issue_hour_range": (
        "SELECT hour, count FROM event_count_by_issue_hour "
        "WHERE issue_id = ? AND hour >= ? AND hour <= ?"
    ),
    "inc_app_hour": (
        "UPDATE event_count_by_app_hour SET count = count + 1 "
        "WHERE app = ? AND hour = ? AND severity = ?"
    ),
    "get_app_hour_range": (
        "SELECT hour, severity, count FROM event_count_by_app_hour "
        "WHERE app = ? AND hour >= ? AND hour <= ?"
    ),
    "inc_issue_total": (
        "UPDATE issue_total_count SET count = count + 1 "
        "WHERE app = ? AND issue_id = ?"
    ),
    "list_issue_totals": (
        "SELECT app, issue_id, count FROM issue_total_count WHERE app = ?"
    ),
    "delete_issue_total": (
        "DELETE FROM issue_total_count WHERE app = ? AND issue_id = ?"
    ),
}


def prepare_all():
    """Prepare every statement in STATEMENTS. Called once at startup."""
    s = get_session()
    for name, cql in STATEMENTS.items():
        _prepared[name] = s.prepare(cql)
    log.info("Prepared %d statements", len(_prepared))


def stmt(name: str):
    if not _prepared:
        prepare_all()
    return _prepared[name]
