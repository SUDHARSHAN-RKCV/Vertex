# app/errors.py
import logging
import os
import re
from logging.handlers import RotatingFileHandler

from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv

load_dotenv()

errors = Blueprint("errors", __name__)

APP_NAME = os.getenv("APP_NAME", "APP Name")
LOG_FILE = f"{APP_NAME}-error_log.log"


# ---------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------

class InvalidCredentialsError(Exception):
    pass


class CORSViolationError(HTTPException):
    code = 498
    description = "CORS policy violation"


# ---------------------------------------------------------
# Suspicious Input Detection
# ---------------------------------------------------------

@errors.before_request
def detect_sql_injection():
    suspicious_patterns = re.compile(
        r"(\bUNION\b|\bSELECT\b|\bDROP\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|--|;)",
        re.IGNORECASE,
    )

    for param, value in {**request.args, **request.form}.items():
        if isinstance(value, str) and suspicious_patterns.search(value):
            current_app.logger.warning(
                f"SQL-SUSPECT | {param}={value} | Path={request.path}"
            )
            return render_template(
                "errors/400.html",
                error="Invalid request syntax"
            ), 400


# ---------------------------------------------------------
# Standard HTTP Errors
# ---------------------------------------------------------

@errors.app_errorhandler(400)
def bad_request(error):
    return render_template("errors/400.html", error=error), 400


@errors.app_errorhandler(401)
def unauthorized(error):
    return render_template("errors/401.html", error=error), 401


@errors.app_errorhandler(403)
def forbidden(error):
    return render_template("errors/403.html", error=error), 403


@errors.app_errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html", error=error), 404


@errors.app_errorhandler(405)
def method_not_allowed(error):
    return render_template("errors/405.html", error=error), 405


@errors.app_errorhandler(413)
def payload_too_large(error):
    return render_template("errors/413.html", error=error), 413


@errors.app_errorhandler(500)
def internal_server_error(error):
    return render_template("errors/500.html", error=error), 500


@errors.app_errorhandler(CORSViolationError)
def cors_error(error):
    return jsonify({"error": error.description}), 498


@errors.app_errorhandler(InvalidCredentialsError)
def handle_invalid_login(error):
    return render_template(
        "errors/401.html",
        error="Invalid username or password"
    ), 401


# ---------------------------------------------------------
# Logging Setup (called AFTER app creation)
# ---------------------------------------------------------

def register_error_handlers(app):
    if not app.debug:
        if not any(isinstance(h, RotatingFileHandler) for h in app.logger.handlers):
            file_handler = RotatingFileHandler(
                LOG_FILE,
                maxBytes=10_000_000,
                backupCount=5
            )
            file_handler.setLevel(logging.ERROR)
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s"
            )
            file_handler.setFormatter(formatter)
            app.logger.addHandler(file_handler)