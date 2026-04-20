from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user
from werkzeug.security import check_password_hash
from .models import db, User, Team, UserTeam

auth = Blueprint("auth", __name__, url_prefix="/admin")

from functools import wraps
from flask import abort

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.lower() != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated
# ----------------------------
# Admin Dashboard
# ----------------------------
@auth.route("/pane", methods=["GET", "POST"])
@login_required
@admin_required
def admin_panel():
    users = User.query.all()
    teams = Team.query.all()
    return render_template("admin_panel.html", users=users, team=teams)


# ----------------------------
# Create User
# ----------------------------
@auth.route("/create_user", methods=["GET", "POST"])
@login_required
@admin_required
def create_user():


    teams = Team.query.all()

    if request.method == "POST":
        email = request.form.get("email").strip()
        role = request.form.get("role")
        password = request.form.get("password")
        selected_team = request.form.getlist("team")

        if User.query.filter_by(email=email).first():
            flash("User already exists.", "danger")
            return redirect(url_for("auth.create_user"))

        user = User(email=email, role=role, password=password)
        db.session.add(user)
        db.session.flush()

        for t_name in selected_team:
            user.add_team(t_name, commit=False)

        db.session.commit()
        flash("User created successfully!", "success")
        return redirect(url_for("auth.admin_panel"))

    return render_template("create_user.html", team=teams)


# ----------------------------
# Edit User
# ----------------------------
@auth.route("/edit_user/<user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id):


    user = db.session.get(User, user_id)
    teams = Team.query.all()

    if request.method == "POST":
        user.email = request.form.get("email").strip()
        user.role = request.form.get("role")
        selected_team = request.form.getlist("team")

        current_team = user.get_team_names()

        # Remove teams
        for t_name in current_team:
            if t_name not in selected_team:
                ut = UserTeam.query.filter_by(
                    user_id=user.id, team_name=t_name
                ).first()
                if ut:
                    db.session.delete(ut)

        # Add new teams
        for t_name in selected_team:
            if t_name not in current_team:
                user.add_team(t_name, commit=False)

        db.session.commit()
        flash("User updated successfully!", "success")
        return redirect(url_for("auth.admin_panel"))

    return render_template("edit_user.html", user=user, ALL_teams=teams)


# ----------------------------
# Delete User
# ----------------------------
@auth.route("/delete_user/<user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def delete_user(user_id):


    user = db.session.get(User, user_id)
    db.session.delete(user)
    db.session.commit()

    flash("User deleted.", "warning")
    return redirect(url_for("auth.admin_panel"))