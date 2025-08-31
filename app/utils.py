# Fonctions utilitaires
from .models import User
from .db import db
from werkzeug.security import generate_password_hash

def seed_admin():
	if not User.query.filter_by(username="admin").first():
		admin = User(
			username="admin",
			password_hash=generate_password_hash("admin123"),
			is_admin=True
		)
		db.session.add(admin)
		db.session.commit()
