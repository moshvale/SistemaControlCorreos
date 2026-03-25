import sys
import os
from app import app
from app.models.user import User
from app.models.database import db

def delete_user_by_email(email):
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"No se encontró usuario con email: {email}")
            return
        try:
            db.session.delete(user)
            db.session.commit()
            print(f"Usuario con email {email} eliminado correctamente.")
        except Exception as e:
            print(f"Error eliminando usuario: {e}")
            db.session.rollback()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python delete_user_by_email.py <correo>")
        sys.exit(1)
    email = sys.argv[1]
    delete_user_by_email(email)