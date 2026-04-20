#app.py
from flask import Blueprint, Flask, render_template, redirect, url_for, flash, abort, request,session,current_app
from flask_login import LoginManager, login_required, current_user,UserMixin, login_user, logout_user
import os

from dotenv import load_dotenv
from .helpers import load_excel, prepare_links
from .errors import register_error_handlers
from werkzeug.security import generate_password_hash, check_password_hash
from .security import register_security_features
from .auths import admin_required,admin_panel, create_user, edit_user, delete_user

from .models import db, User, Team, UserTeam, ALL_teams
#import {datadogRum} from '@datadog/browser-rum'

# -----------------------------
# APP SETUP
# -----------------------------
main = Blueprint('main', __name__)


load_dotenv()

team_links=os.getenv("xl_file")
PUBLIC_SHEETS = ["roc","apac","csm"] 

@main.context_processor
def inject_team_context():
    return {
        "is_roc_apac": lambda t: t in {"roc", "apac"}
    }
# -----------------------------
# ROUTES
# -----------------------------
@main.route("/team/admin", methods=['GET'])
@login_required
@admin_required
def admin_dashboard():
    return redirect(url_for("auth.admin_panel"))

@main.route("/", methods=['GET'])
@login_required 
def home():
    try:
        print(session.get("id"))
        filepath = team_links
        links = prepare_links(load_excel(filepath, sheets=PUBLIC_SHEETS))

        return render_template("index.html", links=links)

    except Exception as e:
        current_app.logger.error(f"Home Page Error: {e}")
        return "Server Error", 500

@main.route('/team/<team_name>', methods=['GET'])
@login_required 
def team_page(team_name):

    user_team = [t.lower() for t in current_user.get_team_names()]
    team_name = team_name.lower()

    if team_name not in user_team:
        return render_template('errors/403.html'), 403

    try:
        data = load_excel(team_links, sheets=[team_name])
        links = prepare_links(data)
    except Exception:
        links = []

    return render_template("team.html", team_name=team_name.capitalize(), links=links)

@main.route('/public/<team_name>', methods=['GET'])
@login_required 
def public_team(team_name):
    team_name = team_name.lower()

    if team_name not in PUBLIC_SHEETS:
        abort(404)

    data = load_excel(team_links, sheets=[team_name])
    links = prepare_links(data)

    # Only rows explicitly marked public
    links = [l for l in links if l.get("is_public")]

    return render_template(
        "team.html",
        team_name=team_name,
        links=links,
        is_public_view=True
    )


@main.route('/my-team', methods=['GET'])
@login_required 
def my_team():

    team = current_user.get_team_names()

    if not team:
        flash("No team assigned to your account.", "warning")
        return redirect(url_for('mainhome'))

    if len(team) == 1:
        return redirect(url_for('team_page', team_name=team[0]))

    return render_template('select_team.html', team=team)
landing="main.home"
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Invalid email or password.", "danger")
            return render_template("login.html"), 401

        if not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html"), 401
       
        login_user(user)
        return redirect(url_for("main.home"))
    from flask import session
    print("Session after login:", dict(session))
    return render_template("login.html")


@main.route('/logout', methods=['GET'])
def logout():
    logout_user()
    session.clear()  # Clear all session data on logout
    print(session.get("role"))
    return redirect(url_for('main.login'))


