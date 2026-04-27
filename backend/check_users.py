import sys
import os

# Add the backend/app directory to the python path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal
from app.models.users import User

def check_users():
    db = SessionLocal()
    users = db.query(User).all()
    print(f"Total users: {len(users)}")
    for user in users:
        print(f"ID: {user.id}, Name: {user.name}, Phone: '{user.phone}' (len={len(user.phone)}), Email: '{user.email}', Role: {user.role}")
    db.close()

if __name__ == "__main__":
    check_users()
