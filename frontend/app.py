import os
from datetime import datetime

from flask import Flask, redirect, session, url_for

from api_client import ApiClient
from blueprints.auth import auth_bp
from blueprints.news import news_bp

ROLE_LABELS = {"teacher": "Преподаватель", "student": "Студент"}


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "dev-flask-secret-key"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        ROLE_LABELS=ROLE_LABELS,
    )
    app.extensions["api"] = ApiClient(
        os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(news_bp)

    @app.context_processor
    def inject_globals():
        return {
            "role_labels": ROLE_LABELS,
            "current_role": session.get("role"),
            "current_username": session.get("username"),
        }

    @app.template_filter("newsdate")
    def newsdate(value: str) -> str:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return str(value or "")
        return parsed.strftime("%d.%m.%Y %H:%M")

    @app.get("/")
    def index():
        if session.get("role"):
            return redirect(url_for("news.list_news"))
        return redirect(url_for("auth.login"))

    return app


app = create_app()
