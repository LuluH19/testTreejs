# Endpoints builds
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from ..models import Project, Build
from ..db import db
from flask import abort
from datetime import datetime, UTC
import random

builds_bp = Blueprint("builds", __name__)

@builds_bp.route("/projects/<int:project_id>/build", methods=["POST"])
@jwt_required()
def trigger_build(project_id):
		"""
		Simuler un build pour un projet
		---
		tags:
			- Builds
		parameters:
			- name: project_id
				in: path
				type: integer
				required: true
		responses:
			201:
				description: Build simulé
		"""
		project = db.session.get(Project, project_id)
		if not project:
			abort(404)
		# Simulation d'un build
		duration = round(random.uniform(2, 10), 2)
		status = random.choice(["success", "fail"])
		logs = f"Build simulated at {datetime.now(UTC).isoformat().replace('+00:00','Z')}. Status: {status}"
		build = Build(project_id=project.id, status=status, duration_s=duration, logs=logs)
		project.last_build_status = status
		db.session.add(build)
		db.session.commit()
		return jsonify({
				"id": build.id,
				"project_id": project.id,
				"status": status,
				"duration_s": duration,
				"logs": logs,
				"created_at": build.created_at.isoformat() + "Z"
		}), 201

@builds_bp.route("/projects/<int:project_id>/builds", methods=["GET"])
@jwt_required()
def list_builds(project_id):
		"""
		Liste des builds d'un projet
		---
		tags:
			- Builds
		parameters:
			- name: project_id
				in: path
				type: integer
				required: true
			- name: page
				in: query
				type: integer
				required: false
				default: 1
			- name: per_page
				in: query
				type: integer
				required: false
				default: 10
		responses:
			200:
				description: Liste paginée des builds
		"""
		if not db.session.get(Project, project_id):
			abort(404)
		page = int(request.args.get("page", 1))
		per_page = int(request.args.get("per_page", 10))
		q = Build.query.filter_by(project_id=project_id).order_by(Build.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
		return jsonify({
				"items": [
						{
								"id": b.id,
								"status": b.status,
								"duration_s": b.duration_s,
								"logs": b.logs,
								"created_at": b.created_at.isoformat() + "Z"
						} for b in q.items
				],
				"total": q.total,
				"page": q.page,
				"pages": q.pages
		})
