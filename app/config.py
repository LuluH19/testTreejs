# Configuration de base Flask
import os

class Config:
    SECRET_KEY = os.environ.get("JWT_SECRET", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DB_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENV = os.environ.get("ENV", "development")
