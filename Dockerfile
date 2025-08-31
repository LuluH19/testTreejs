# Dockerfile production-ready pour Mini API Usine Logicielle
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH="/root/.local/bin:$PATH"
COPY . .
# Sécurité : forcer l'installation de gunicorn dans l'image finale
RUN pip install --upgrade pip && pip install gunicorn

# Variables d'environnement (à surcharger)
ENV FLASK_APP=app \
    FLASK_ENV=production \
    DB_URL=sqlite:///app.db

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "--timeout", "120", "--workers", "1", "--worker-class", "sync", "app:create_app()"]
