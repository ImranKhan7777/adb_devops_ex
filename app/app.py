import os

import psycopg
from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello from ADB DevOps Assignment!"


@app.route("/health")
def health():
    return {"status": "healthy"}, 200


@app.route("/db-health")
def db_health():
    try:
        with psycopg.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "adbapp"),
            user=os.getenv("DB_USER", "adbuser"),
            password=os.getenv("DB_PASSWORD", ""),
            connect_timeout=3,
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()

        return {"database": "connected"}, 200

    except psycopg.Error:
        app.logger.exception("Database health check failed")
        return {"database": "unavailable"}, 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
