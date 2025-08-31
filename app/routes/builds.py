# Endpoints /builds
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required
from datetime import datetime
from ..models import Build, Project
from ..db import db

builds_bp = Blueprint("builds", __name__)

@builds_bp.route("/projects/<int:project_id>/builds", methods=["POST"])
@jwt_required()
def trigger_build(project_id):
	"""
	Déclencher un build
	---
	tags:
	  - Builds
	parameters:
	  - name: project_id
	    in: path
	    type: integer
	    required: true
	requestBody:
	  content:
	    application/json:
	      schema:
	        type: object
	        properties:
	          branch:
	            type: string
	      example:
	        branch: main
	responses:
	  201:
	    description: Build déclenché
	  404:
	    description: Projet non trouvé
	"""
	project = Project.query.get(project_id)
	if not project:
		abort(404)
	
	data = request.get_json()
	branch = data.get("branch", "main") if data else "main"
	
	build = Build(
		project_id=project_id,
		status="pending",
		branch=branch,
		created_at=datetime.utcnow()
	)
	db.session.add(build)
	project.last_build_status = "pending"
	db.session.commit()
	
	return jsonify({
		"id": build.id,
		"status": build.status,
		"branch": build.branch,
		"created_at": build.created_at.isoformat() + "Z"
	}), 201

@builds_bp.route("/projects/<int:project_id>/builds", methods=["GET"])
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
				"branch": b.branch,
				"created_at": b.created_at.isoformat() + "Z"
			} for b in q.items
		],
		"total": q.total,
		"page": q.page,
		"pages": q.pages
	})
