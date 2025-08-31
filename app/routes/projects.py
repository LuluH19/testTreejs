# Endpoints /projects
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..models import Project
from ..db import db

projects_bp = Blueprint("projects", __name__)

@projects_bp.route("/projects", methods=["GET"])
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
	        name: Mon Projet
	        repo: https://github.com/user/repo.git
	responses:
	  201:
	    description: Projet créé
	  400:
	    description: Données invalides
	"""
	data = request.get_json()
	if not data or "name" not in data or "repo" not in data:
		return jsonify({"error": "invalid_request", "message": "name and repo required"}), 400
	
	existing = Project.query.filter_by(name=data["name"]).first()
	if existing:
		return jsonify({"error": "conflict", "message": "Un projet avec ce nom existe déjà"}), 409
	
	project = Project(
		name=data["name"],
		repo=data["repo"],
		last_build_status="none",
		created_at=datetime.utcnow()
	)
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
def get_project(project_id):
	"""
	Détails d'un projet
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
	    description: Détails du projet
	  404:
	    description: Projet non trouvé
	"""
	project = Project.query.get_or_404(project_id)
	return jsonify({
		"id": project.id,
		"name": project.name,
		"repo": project.repo,
		"last_build_status": project.last_build_status,
		"created_at": project.created_at.isoformat() + "Z"
	})

@projects_bp.route("/projects/<int:project_id>", methods=["DELETE"])
@jwt_required()
def delete_project(project_id):
	"""
	Supprimer un projet
	---
	tags:
	  - Projets
	parameters:
	  - name: project_id
	    in: path
	    type: integer
	    required: true
	responses:
	  204:
	    description: Projet supprimé
	  404:
	    description: Projet non trouvé
	"""
	project = Project.query.get_or_404(project_id)
	db.session.delete(project)
	db.session.commit()
	return "", 204
