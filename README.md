# Mini API d’Usine Logicielle – Guide Complet

## 🚀 Objectif

Ce projet est une API REST pédagogique simulant des services d’usine logicielle (CI/CD) : gestion de projets, builds simulés, monitoring, authentification JWT, documentation Swagger, tests, CI, Docker, et PostgreSQL.

---

## 🗂️ Structure du projet

```
app/
	__init__.py         # Factory Flask, enregistrement blueprints, config, erreurs
	config.py           # Configuration centralisée (env, DB, JWT)
	db.py               # Instance SQLAlchemy
	models.py           # Modèles ORM (User, Project, Build)
	schemas.py          # Schémas de validation (TypedDict)
	auth.py             # (à compléter pour extensions JWT)
	security.py         # Fonctions de hash (Werkzeug)
	utils.py            # Fonctions utilitaires (seed admin)
	routes/
		__init__.py
		status.py         # /status (health check)
		login.py          # /login (JWT)
		projects.py       # /projects (CRUD)
		builds.py         # /projects/<id>/build(s)
tests/
	test_auth.py
	test_projects.py
	test_builds.py
	test_status.py
requirements.txt
.env.example
Dockerfile
docker-compose.yml
.github/workflows/ci.yml
README.md
```

---

## 🧩 Fonctionnalités principales

### 1. Authentification JWT

- **/login** : POST, prend `{username, password}` et retourne un JWT si OK.
- Utilise `flask-jwt-extended` pour la gestion des tokens.
- User admin seedé automatiquement (admin/admin123, mot de passe hashé).

**Extrait :**
```python
@login_bp.route("/login", methods=["POST"])
def login():
		data = request.get_json()
		user = User.query.filter_by(username=data["username"]).first()
		if not user or not check_password_hash(user.password_hash, data["password"]):
				return jsonify({"error": "unauthorized"}), 401
		access_token = create_access_token(identity=user.username, expires_delta=timedelta(minutes=30))
		return jsonify({"access_token": access_token, "token_type": "bearer"})
```

---

### 2. Projets (CRUD minimal)

- **GET /projects** : liste paginée, protégée JWT.
- **POST /projects** : création, unicité du nom, validation d’entrée.
- **GET /projects/<id>** : détail d’un projet.

**Extrait :**
```python
@projects_bp.route("/projects", methods=["POST"])
@jwt_required()
def create_project():
		data = request.get_json()
		if Project.query.filter_by(name=data["name"]).first():
				return jsonify({"error": "conflict"}), 409
		project = Project(name=data["name"], repo=data["repo"])
		db.session.add(project)
		db.session.commit()
		return jsonify({...}), 201
```

---

### 3. Builds & artefacts (simulation)

- **POST /projects/<id>/build** : simule un build (durée random, status, logs courts).
- **GET /projects/<id>/builds** : liste paginée des builds d’un projet.

**Extrait :**
```python
@builds_bp.route("/projects/<int:project_id>/build", methods=["POST"])
@jwt_required()
def trigger_build(project_id):
		project = db.session.get(Project, project_id)
		if not project:
				abort(404)
		duration = round(random.uniform(2, 10), 2)
		status = random.choice(["success", "fail"])
		logs = f"Build simulated at {datetime.now(UTC).isoformat().replace('+00:00','Z')}. Status: {status}"
		build = Build(project_id=project.id, status=status, duration_s=duration, logs=logs)
		project.last_build_status = status
		db.session.add(build)
		db.session.commit()
		return jsonify({...}), 201
```

---

### 4. Monitoring

- **GET /status** : health check, version, uptime, DB OK, horodatage UTC.

---

### 5. Documentation Swagger

- **Swagger UI** auto-généré via flasgger, accessible sur `/apidocs`.
- Docstring YAML pour chaque endpoint, exemples inclus.

---

### 6. Sécurité

- Mot de passe hashé (Werkzeug).
- JWT avec expiration.
- Variables sensibles via `.env`.
- CORS et rate limiting : à ajouter selon besoin.

---

### 7. Tests

- **pytest** pour tous les endpoints (auth, projets, builds, status).
- Génération de noms uniques pour éviter les conflits en base.
- Couverture complète du flux métier.

---

### 8. Docker & CI

#### Dockerfile (multi-stage, image slim, gunicorn) :
```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH="/root/.local/bin:$PATH"
COPY . .
ENV FLASK_APP=app FLASK_ENV=production DB_URL=sqlite:///app.db
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:create_app()"]
```

#### docker-compose.yml (PostgreSQL + API) :
```yaml
version: '3.9'
services:
	db:
		image: postgres:16-alpine
		environment:
			POSTGRES_DB: usine
			POSTGRES_USER: usine
			POSTGRES_PASSWORD: usine
		ports:
			- "5432:5432"
		volumes:
			- pgdata:/var/lib/postgresql/data
	api:
		build: .
		environment:
			DB_URL: postgresql+psycopg2://usine:usine@db:5432/usine
			JWT_SECRET: change-me
			FLASK_ENV: production
		ports:
			- "5000:5000"
		depends_on:
			- db
volumes:
	pgdata:
```

#### CI GitHub Actions

- `.github/workflows/ci.yml` : setup Python, install, pytest, (optionnel build Docker).
- Badge de statut dans le README.

---

## 🧪 Exemples d’utilisation (curl)

```bash
# Authentification
curl -X POST http://localhost:5000/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}'

# Lister les projets
curl -H "Authorization: Bearer <token>" http://localhost:5000/projects

# Créer un projet
curl -X POST http://localhost:5000/projects -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"name":"DemoProj","repo":"https://github.com/demo/repo"}'

# Simuler un build
curl -X POST http://localhost:5000/projects/1/build -H "Authorization: Bearer <token>"

# Lister les builds
curl -H "Authorization: Bearer <token>" http://localhost:5000/projects/1/builds

# Monitoring
curl http://localhost:5000/status
```

---

## 🏗️ Bonnes pratiques et points PRO

- **Factory pattern** pour Flask (`create_app()`), facilite les tests et la config.
- **Gestion centralisée des erreurs** (JSON unifié).
- **Validation d’entrée** manuelle, typée, claire.
- **Séparation claire** des responsabilités (routes, modèles, utilitaires).
- **Tests robustes** et idempotents (noms uniques).
- **Compatibilité SQLite/PostgreSQL** sans modification du code métier.
- **Conteneurisation** et CI/CD prêtes à l’emploi.

---

## 💡 Pour aller plus loin

- Ajout de refresh token JWT, CORS, rate limiting.
- Ajout de rôles utilisateurs, gestion fine des droits.
- Intégration d’un vrai système de logs (structurés).
- Déploiement cloud (Heroku, Azure, AWS…).

