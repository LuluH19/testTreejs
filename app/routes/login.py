# Endpoint /login
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from datetime import timedelta
from ..models import User
from ..db import db

login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["POST"])
def login():
	"""
	Authentification utilisateur (JWT)
	---
	tags:
	  - Auth
	requestBody:
	  required: true
	  content:
	    application/json:
	      schema:
	        type: object
	        properties:
	          username:
	            type: string
	          password:
	            type: string
	      example:
	        username: admin
	        password: admin123
	responses:
	  200:
	    description: Token JWT
	    examples:
	      application/json:
	        access_token: "..."
	        token_type: bearer
	  401:
	    description: Identifiants invalides
	"""
	data = request.get_json()
	if not data or "username" not in data or "password" not in data:
		return jsonify({"error": "invalid_request", "message": "username and password required"}), 400
	user = User.query.filter_by(username=data["username"]).first()
	if not user or not check_password_hash(user.password_hash, data["password"]):
		return jsonify({"error": "unauthorized", "message": "Identifiants invalides"}), 401
	access_token = create_access_token(identity=user.username, expires_delta=timedelta(minutes=30))
	return jsonify({"access_token": access_token, "token_type": "bearer"})
