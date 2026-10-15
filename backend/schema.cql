// LogVault schema
// Design principle: one table per query pattern (classic Cassandra data modeling).
// Counters live in their own tables because Cassandra does not allow counter
// columns to coexist with regular columns.

CREATE KEYSPACE IF NOT EXISTS logvault
  WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE logvault;

// 1. Registered applications and their API keys.
CREATE TABLE IF NOT EXISTS apps (
    app_name    text PRIMARY KEY,
    api_key     text,
    webhook_url text,
    created_at  timestamp
);

// 2. Canonical issue record. One row per fingerprint (grouped error).
CREATE TABLE IF NOT EXISTS issues (
    issue_id       text PRIMARY KEY,
    app            text,
    exception_type text,
    message        text,
    first_frame    text,
    severity       text,
    first_seen     timestamp,
    last_seen      timestamp,
    status         text,
    note           text
);

// 3. All issues of an app, used by the dashboard list view.
CREATE TABLE IF NOT EXISTS issues_by_app (
    app            text,
    issue_id       text,
    exception_type text,
    message        text,
    severity       text,
    status         text,
    last_seen      timestamp,
    PRIMARY KEY ((app), issue_id)
);

// 4. Full timeline of raw events for a single issue (detail / stack trace view).
// TTL is set per-insert (default 30 days) so old events auto-expire.
CREATE TABLE IF NOT EXISTS events_by_issue (
    issue_id   text,
    event_time timestamp,
    event_id   uuid,
    app        text,
    severity   text,
    message    text,
    stack      text,
    PRIMARY KEY ((issue_id), event_time, event_id)
) WITH CLUSTERING ORDER BY (event_time DESC, event_id ASC);

// 5. Recent events of an app on a given day (bucketed to keep partitions small).
// Powers the "recent errors" feed with filters.
CREATE TABLE IF NOT EXISTS events_by_app_day (
    app        text,
    day        date,
    event_time timestamp,
    event_id   uuid,
    issue_id   text,
    severity   text,
    message    text,
    PRIMARY KEY ((app, day), event_time, event_id)
) WITH CLUSTERING ORDER BY (event_time DESC, event_id ASC);

// 6. Counter: events per issue per hour. Powers the per-issue sparkline.
CREATE TABLE IF NOT EXISTS event_count_by_issue_hour (
    issue_id text,
    hour     timestamp,
    count    counter,
    PRIMARY KEY ((issue_id), hour)
) WITH CLUSTERING ORDER BY (hour DESC);

// 7. Counter: events per app per hour per severity. Powers trend + severity charts.
CREATE TABLE IF NOT EXISTS event_count_by_app_hour (
    app      text,
    hour     timestamp,
    severity text,
    count    counter,
    PRIMARY KEY ((app), hour, severity)
) WITH CLUSTERING ORDER BY (hour DESC, severity ASC);

// 8. Counter: lifetime occurrence count per issue. Powers the "noisy issues" top-N.
CREATE TABLE IF NOT EXISTS issue_total_count (
    app      text,
    issue_id text,
    count    counter,
    PRIMARY KEY ((app), issue_id)
);
