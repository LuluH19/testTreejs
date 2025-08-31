# Modèles SQLAlchemy

from .db import db
from datetime import datetime

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password_hash = db.Column(db.String(255), nullable=False)
	is_admin = db.Column(db.Boolean, default=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return f"<User {self.username}>"


class Project(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), unique=True, nullable=False)
	repo = db.Column(db.String(255), nullable=False)
	last_build_status = db.Column(db.String(20))
	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	builds = db.relationship('Build', backref='project', lazy=True)

class Build(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
	status = db.Column(db.String(20), nullable=False)
	duration_s = db.Column(db.Float, nullable=False)
	logs = db.Column(db.String(255))
	created_at = db.Column(db.DateTime, default=datetime.utcnow)
