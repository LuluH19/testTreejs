# Tests auth
import pytest
from app import create_app

@pytest.fixture
def client():
	app = create_app()
	app.config["TESTING"] = True
	with app.test_client() as client:
		yield client

def test_login_ok(client):
	resp = client.post("/login", json={"username": "admin", "password": "admin123"})
	assert resp.status_code == 200
	data = resp.get_json()
	assert "access_token" in data
	assert data["token_type"] == "bearer"

def test_login_nok(client):
	resp = client.post("/login", json={"username": "admin", "password": "wrong"})
	assert resp.status_code == 401
	data = resp.get_json()
	assert data["error"] == "unauthorized"
