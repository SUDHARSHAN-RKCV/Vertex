from app import create_app
from app.models import User

app = create_app()

with app.app_context():
    user = User.query.filter_by(email="admin@vertex.com").first()

    if not user:
        print("User not found.")
    else:
        print("User found:", user.email)
        print("User found:", user.id)
        print("Stored hash:", user.password_hash)
        print("Password matches?:", user.check_password("Admin@123"))