import os

os.environ["DATABASE_URL"] = "sqlite://"

from app import app, db


def setup_function():
    with app.app_context():
        db.drop_all()
        db.create_all()


def test_health():
    response = app.test_client().get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_create_task():
    client = app.test_client()
    response = client.post(
        "/api/tasks",
        json={"title": "Check application health"}
    )
    assert response.status_code == 201
    assert response.json["title"] == "Check application health"


def test_metrics():
    response = app.test_client().get("/metrics")
    assert response.status_code == 200
    assert b"cloudops_http_requests_total" in response.data