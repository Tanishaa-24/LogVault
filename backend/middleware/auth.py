"""API-key auth for the /api/log ingest endpoint.

Dashboard endpoints are intentionally open in this demo so the frontend can
browse freely. In production you'd gate those behind a session login.
"""
from functools import wraps
from flask import request, jsonify

from cassandra_client import get_session, stmt


def require_app_api_key(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-Key", "")
        payload = request.get_json(silent=True) or {}
        app_name = payload.get("app", "")

        if not api_key or not app_name:
            return jsonify(error="Missing X-API-Key or 'app' field"), 401

        row = get_session().execute(stmt("get_app"), (app_name,)).one()
        if row is None:
            return jsonify(error=f"Unknown app '{app_name}'"), 401
        if row.api_key != api_key:
            return jsonify(error="Invalid API key"), 401

        request.app_record = row  # stash for the route to use
        return f(*args, **kwargs)

    return wrapper
