# create_tables.py

import os
from flask import Flask
from dotenv import load_dotenv
from sqlalchemy import text
import pandas as pd
# Import your models & db
#from .config import Config
from models import db, Team, User, UserTeam, ALL_teams,TEAM_PRESETS

load_dotenv()

schema_name = os.getenv("schema_name", "{{APP_NAME}}")
database_uri = POSTGRES_URI

if not database_uri:
    raise ValueError("POSTGRES_URI not found in .env")


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    return app

def seed_users_from_excel(file_name="seed_users.xlsx"):

    # Get absolute path of THIS script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, file_name)

    print("Looking for seed file at:", file_path)

    if not os.path.exists(file_path):
        print(f"⚠ Seed file not found: {file_path}")
        return

    df = pd.read_excel(file_path)
    df = df.fillna("")

    for _, row in df.iterrows():
        email = str(row.get("email")).strip()
        role = str(row.get("role")).strip()
        password = str(row.get("password")).strip()
        preset = str(row.get("preset")).strip()

        if not email or not password:
            print(f"⚠ Skipping invalid row: {row}")
            continue

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            print(f"⚠ User exists: {email}")
            user = existing_user
        else:
            print(f"➕ Creating user: {email}")
            user = User(
                email=email,
                role=role,
                password=password,
            )
            db.session.add(user)
            db.session.commit()

        team_list = TEAM_PRESETS.get(preset, [])

        for team_name in team_list:
            user.add_team(team_name, commit=False)

        db.session.commit()

    print("✅ Excel user seeding completed.")

    
def bootstrap():
    app = create_app()

    with app.app_context():
        print("🔹 Creating schema if not exists...")
        
        print("schema done")
        print("🔹 Creating tables...")
        db.create_all()

        print("🔹 Seeding default teams...")
        for team_name in ALL_teams:
            existing = Team.query.filter_by(name=team_name).first()
            if not existing:
                db.session.add(Team(name=team_name))
        db.session.commit()

        print("🔹 Seeding users from Excel...")
        seed_users_from_excel("seed_users.xlsx")

        print("🚀 Database fully initialized.")


if __name__ == "__main__":
    bootstrap()