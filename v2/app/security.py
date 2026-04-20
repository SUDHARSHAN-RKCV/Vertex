# app/security.py
from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = None

def register_security_features(app):
    global limiter

    limits = app.config.get("DEFAULT_RATELIMITS", "200 per day;50 per hour").split(";")

    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=limits,
        storage_uri="memory://"
    )

    endpoints = app.view_functions

    if 'main.home' in endpoints:
        limiter.limit("30 per minute")(endpoints['main.home'])

    if 'main.team_page' in endpoints:
        limiter.limit("30 per minute")(endpoints['main.team_page'])

    if 'main.login' in endpoints:
        limiter.limit("5 per 15 minutes", key_func=_login_key)(endpoints['main.login'])

    _setup_rate_limit_logging(app)

def _login_key():
    return request.form.get('email') or get_remote_address()

def _setup_rate_limit_logging(app):
    @app.errorhandler(429)
    def too_many_requests(error):
        info = getattr(error, "description", "Rate limit exceeded")
        app.logger.warning(
            f"429 Too Many Requests: {info}\n"
            f"Path: {request.path}\n"
            f"Client IP: {request.remote_addr}\n"
            f"User Agent: {request.user_agent}"
        )
        try:
            return (
                app.jinja_env.get_template('errors/429.html').render(error=error),
                429
            )
        except Exception:
            return (
                "Rate limit exceeded. Please wait and try again.",
                429
            )