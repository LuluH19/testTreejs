"""Initialisation de l’application Flask."""
from flask import Flask

from .config import Config
from .db import db

from flask_jwt_extended import JWTManager
from flasgger import Swagger

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Swagger
    swagger = Swagger(app)

    # Gestion centralisée des erreurs (JSON)
    @app.errorhandler(Exception)
    def handle_error(e):
        from flask import jsonify
        code = getattr(e, 'code', 500)
        name = getattr(e, 'name', 'internal_error')
        return jsonify({
            "error": name,
            "message": str(e),
        }), code


    # JWT
    jwt = JWTManager(app)

    # Import et enregistrement des blueprints
    from .routes.status import status_bp
    from .routes.login import login_bp
    from .routes.projects import projects_bp
    from .routes.builds import builds_bp
    app.register_blueprint(status_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(builds_bp)




    # Seed admin si besoin
    with app.app_context():
        from .utils import seed_admin
        db.create_all()
        seed_admin()
    return app
