# Test du endpoint /status
import pytest
from app import create_app

@pytest.fixture
def client():
	app = create_app()
	app.config["TESTING"] = True
	with app.test_client() as client:
		yield client

def test_status_ok(client):
	resp = client.get("/status")
	assert resp.status_code == 200
	data = resp.get_json()
	assert data["status"] == "ok"
	assert "version" in data
	assert "uptime_s" in data
	assert "db_ok" in data
	assert data["db_ok"] is True
