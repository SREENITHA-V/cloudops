import os
import time
import logging
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql://cloudops:cloudops@db:5432/cloudops"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cloudops")

REQUEST_COUNT = Counter(
    "cloudops_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_DURATION = Histogram(
    "cloudops_http_request_duration_seconds",
    "HTTP request duration",
    ["endpoint"]
)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


@app.before_request
def before_request():
    request.start_time = time.perf_counter()


@app.after_request
def after_request(response):
    endpoint = request.endpoint or "unknown"
    duration = time.perf_counter() - getattr(
        request, "start_time", time.perf_counter()
    )

    REQUEST_COUNT.labels(
        request.method, endpoint, str(response.status_code)
    ).inc()

    REQUEST_DURATION.labels(endpoint).observe(duration)
    return response


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200
    except Exception:
        logger.exception("Health check failed")
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected"
        }), 503


@app.get("/api/overview")
def overview():
    total = Task.query.count()
    completed = Task.query.filter_by(completed=True).count()

    return jsonify({
        "service": "CloudOps Web",
        "status": "healthy",
        "tasks_total": total,
        "tasks_completed": completed,
        "tasks_open": total - completed,
        "version": os.getenv("APP_VERSION", "local"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


@app.route("/api/tasks", methods=["GET", "POST"])
def tasks():
    if request.method == "GET":
        rows = Task.query.order_by(Task.id.desc()).all()
        return jsonify([
            {
                "id": task.id,
                "title": task.title,
                "completed": task.completed
            }
            for task in rows
        ])

    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()

    if not title or len(title) > 200:
        return jsonify({
            "error": "Enter a task title between 1 and 200 characters"
        }), 400

    task = Task(title=title)
    db.session.add(task)
    db.session.commit()

    logger.info("Created task %s", task.id)

    return jsonify({
        "id": task.id,
        "title": task.title,
        "completed": task.completed
    }), 201


@app.patch("/api/tasks/<int:task_id>")
def update_task(task_id):
    task = db.session.get(Task, task_id)

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json(silent=True) or {}
    task.completed = bool(data.get("completed", not task.completed))
    db.session.commit()

    return jsonify({
        "id": task.id,
        "completed": task.completed
    })


@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    task = db.session.get(Task, task_id)

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({"deleted": True})


@app.get("/api/deployments")
def deployments():
    return jsonify([{
        "version": os.getenv("APP_VERSION", "local"),
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }])


@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {
        "Content-Type": CONTENT_TYPE_LATEST
    }


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.exception("Internal server error")
    return jsonify({"error": "Internal server error"}), 500


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)