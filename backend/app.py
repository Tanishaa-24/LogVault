"""LogVault Flask entry point."""
import logging
import os

from flask import Flask, jsonify
from flask_cors import CORS

from cassandra_client import get_session, prepare_all
from routes.ingest import bp as ingest_bp
from routes.issues import bp as issues_bp
from routes.analytics import bp as analytics_bp

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    get_session()
    prepare_all()

    app.register_blueprint(ingest_bp)
    app.register_blueprint(issues_bp)
    app.register_blueprint(analytics_bp)

    @app.get("/healthz")
    def healthz():
        try:
            get_session().execute("SELECT release_version FROM system.local").one()
            return jsonify(ok=True)
        except Exception as e:
            return jsonify(ok=False, error=str(e)), 503

    @app.get("/")
    def root():
        return jsonify(
            name="LogVault API",
            endpoints=[
                "POST /api/log",
                "GET  /api/apps",
                "POST /api/apps",
                "PATCH /api/apps/<name>",
                "DELETE /api/apps/<name>",
                "GET  /api/issues?app=<name>",
                "GET  /api/issues/<issue_id>",
                "PATCH /api/issues/<issue_id>",
                "DELETE /api/issues/<issue_id>",
                "GET  /api/analytics/trend?app=<name>&hours=24",
                "GET  /api/analytics/severity?app=<name>&hours=24",
                "GET  /api/analytics/top-issues?app=<name>&n=5",
                "GET  /api/analytics/throughput",
                "GET  /healthz",
            ],
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
