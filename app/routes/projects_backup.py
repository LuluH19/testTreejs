# Endpoints projets
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models import Project
from ..db import db
from flask import abort

projects_bp = Blueprint("projects", __name__)

def validate_project(data):
	errors = []
	if "name" not in data or not isinstance(data["name"], str) or not data["name"].strip():
		errors.append("name is required and must be a non-empty string")
	if "repo" not in data or not isinstance(data["repo"], str) or not data["repo"].strip():
		errors.append("repo is required and must be a non-empty string")
	return errors

@projects_bp.route("/projects", methods=["GET"])
@jwt_required()
def list_projects():
	"""
	Liste paginée des projets
	---
	tags:
	  - Projets
	parameters:
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
	    description: Liste paginée
	"""
	page = int(request.args.get("page", 1))
	per_page = int(request.args.get("per_page", 10))
	q = Project.query.order_by(Project.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
	return jsonify({
		"items": [
			{
				"id": p.id,
				"name": p.name,
				"repo": p.repo,
				"last_build_status": p.last_build_status,
				"created_at": p.created_at.isoformat() + "Z"
			} for p in q.items
		],
		"total": q.total,
		"page": q.page,
		"pages": q.pages
	})

@projects_bp.route("/projects", methods=["POST"])
@jwt_required()
def create_project():
		"""
		Créer un projet
		---
		tags:
			- Projets
		requestBody:
			required: true
			content:
				application/json:
					schema:
						type: object
						properties:
							name:
								type: string
							repo:
								type: string
					example:
						name: DemoProj
						repo: https://github.com/demo/repo
		responses:
			201:
				description: Projet créé
		"""
		data = request.get_json()
		errors = validate_project(data)
		if errors:
				return jsonify({"error": "validation_error", "message": ", ".join(errors)}), 400
		if Project.query.filter_by(name=data["name"]).first():
				return jsonify({"error": "conflict", "message": "Project name already exists"}), 409
		project = Project(name=data["name"], repo=data["repo"])
		db.session.add(project)
		db.session.commit()
		return jsonify({
				"id": project.id,
				"name": project.name,
				"repo": project.repo,
				"last_build_status": project.last_build_status,
				"created_at": project.created_at.isoformat() + "Z"
		}), 201

@projects_bp.route("/projects/<int:project_id>", methods=["GET"])
@jwt_required()
def get_project(project_id):
		"""
		Détail d'un projet
		---
		tags:
			- Projets
		parameters:
			- name: project_id
				in: path
				type: integer
				required: true
		responses:
			200:
				description: Projet
		"""
		project = db.session.get(Project, project_id)
		if not project:
			abort(404)
		return jsonify({
				"id": project.id,
				"name": project.name,
				"repo": project.repo,
				"last_build_status": project.last_build_status,
				"created_at": project.created_at.isoformat() + "Z"
		})
