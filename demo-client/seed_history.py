"""Backfill a few hours of low-volume historical data so spike detection has
something to compare against.

Writes directly to the Cassandra counter tables. Only use for demos; a real
system would accumulate this history naturally over hours of operation.

    python3 demo-client/seed_history.py --app payments --hours 6
"""
import argparse
import random
from datetime import datetime, timedelta

from cassandra.cluster import Cluster


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--app", default="payments")
    parser.add_argument("--issue-id", default="c84a80bf50b44663",
                        help="Which issue to backfill history for (default = KeyError user_id)")
    parser.add_argument("--hours", type=int, default=6, help="How many hours of history")
    parser.add_argument("--per-hour", type=int, default=2,
                        help="Baseline events per hour (small; makes the current spike stand out)")
    args = parser.parse_args()

    cluster = Cluster([args.host])
    session = cluster.connect("logvault")

    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    for h in range(1, args.hours + 1):
        hour = now - timedelta(hours=h)
        n = max(1, args.per_hour + random.randint(-1, 1))
        for _ in range(n):
            session.execute(
                "UPDATE event_count_by_issue_hour SET count = count + 1 "
                "WHERE issue_id=%s AND hour=%s",
                (args.issue_id, hour),
            )
            session.execute(
                "UPDATE event_count_by_app_hour SET count = count + 1 "
                "WHERE app=%s AND hour=%s AND severity=%s",
                (args.app, hour, "ERROR"),
            )
        print(f"  seeded hour {hour.isoformat()}: {n} events")

    print(f"Backfilled {args.hours}h of history for issue {args.issue_id} in app '{args.app}'")
    cluster.shutdown()


if __name__ == "__main__":
    main()
