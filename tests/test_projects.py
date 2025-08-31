# Tests projets

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

def test_list_projects_auth_required(client):
	resp = client.get("/projects")
	assert resp.status_code == 401

def test_create_and_get_project(client):
	token = get_token(client)
	unique_name = f"DemoProj_{uuid.uuid4()}"
	# Création
	resp = client.post("/projects", json={"name": unique_name, "repo": "https://github.com/demo/repo"}, headers={"Authorization": f"Bearer {token}"})
	assert resp.status_code == 201
	data = resp.get_json()
	assert data["name"] == unique_name
	# Liste
	resp = client.get("/projects", headers={"Authorization": f"Bearer {token}"})
	assert resp.status_code == 200
	items = resp.get_json()["items"]
	assert any(p["name"] == unique_name for p in items)
	# Détail
	pid = data["id"]
	resp = client.get(f"/projects/{pid}", headers={"Authorization": f"Bearer {token}"})
	assert resp.status_code == 200
	assert resp.get_json()["name"] == unique_name

def test_create_project_conflict(client):
	token = get_token(client)
	unique_name = f"UniqueProj_{uuid.uuid4()}"
	# Premier projet
	client.post("/projects", json={"name": unique_name, "repo": "https://github.com/demo/unique"}, headers={"Authorization": f"Bearer {token}"})
	# Conflit
	resp = client.post("/projects", json={"name": unique_name, "repo": "https://github.com/demo/other"}, headers={"Authorization": f"Bearer {token}"})
	assert resp.status_code == 409
