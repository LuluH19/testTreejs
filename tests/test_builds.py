# Tests builds

import pytest
from app import create_app
import uuid

@pytest.fixture
def client():
	app = create_app()
	app.config["TESTING"] = True
	with app.test_client() as client:
		yield client

def get_token(client):
	resp = client.post("/login", json={"username": "admin", "password": "admin123"})
	return resp.get_json()["access_token"]

def create_project(client, token):
	unique_name = f"BuildProj_{uuid.uuid4()}"
	resp = client.post("/projects", json={"name": unique_name, "repo": "https://github.com/demo/build"}, headers={"Authorization": f"Bearer {token}"})
	return resp.get_json()["id"]

def test_build_simulation_and_listing(client):
	token = get_token(client)
	pid = create_project(client, token)
	# Simuler un build
	resp = client.post(f"/projects/{pid}/build", headers={"Authorization": f"Bearer {token}"})
	assert resp.status_code == 201
	data = resp.get_json()
	assert data["status"] in ("success", "fail")
	# Lister les builds
	resp = client.get(f"/projects/{pid}/builds", headers={"Authorization": f"Bearer {token}"})
	assert resp.status_code == 200
	items = resp.get_json()["items"]
	assert len(items) >= 1
