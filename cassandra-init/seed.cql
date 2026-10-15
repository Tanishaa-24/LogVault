// Seed a demo app with a known API key so the frontend can show something immediately.
USE logvault;

INSERT INTO apps (app_name, api_key, webhook_url, created_at)
VALUES ('payments', 'demo-key-payments', '', toTimestamp(now()));

INSERT INTO apps (app_name, api_key, webhook_url, created_at)
VALUES ('checkout', 'demo-key-checkout', '', toTimestamp(now()));

INSERT INTO apps (app_name, api_key, webhook_url, created_at)
VALUES ('search', 'demo-key-search', '', toTimestamp(now()));
