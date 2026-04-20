# app/__init__.py

import os
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv

from .models import db, User
from .config import Config
from .errors import errors, register_error_handlers
from .security import register_security_features


login_manager = LoginManager()


def create_app():
    """
    Application factory.
    Responsible only for assembling components.
    """

    # Load environment variables once
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    # -------------------------------
    # Extensions
    # -------------------------------
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message = "Please sign in to continue."
    login_manager.login_message_category = "info"

    # -------------------------------
    # Blueprints
    # -------------------------------
    from .app import main
    from .auths import auth

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(errors)

    # -------------------------------
    # Security + Error Systems
    # -------------------------------
    register_error_handlers(app)
    register_security_features(app)

    # -------------------------------
    # Template Context
    # -------------------------------
    @app.context_processor
    def inject_app_metadata():
        return {
            "app_name": app.config.get("APP_NAME"),
            "app_version": app.config.get("APP_VERSION"),
            "support_email": app.config.get("SUPPORT_EMAIL"),
        }

    return app


# -------------------------------------------------
# User Loader
# -------------------------------------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)