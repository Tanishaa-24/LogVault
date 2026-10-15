import os

CASSANDRA_HOSTS = os.getenv("CASSANDRA_HOSTS", "cassandra").split(",")
CASSANDRA_PORT = int(os.getenv("CASSANDRA_PORT", "9042"))
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "logvault")

# Event rows auto-expire after this many seconds (default 30 days).
EVENT_TTL_SECONDS = int(os.getenv("EVENT_TTL_SECONDS", str(60 * 60 * 24 * 30)))

# A spike is flagged when an issue's last-hour count is >= this multiple of
# its average hourly count over the preceding window.
SPIKE_MULTIPLIER = float(os.getenv("SPIKE_MULTIPLIER", "5.0"))
SPIKE_LOOKBACK_HOURS = int(os.getenv("SPIKE_LOOKBACK_HOURS", "24"))
