import sys
import os

# Add the backend/app directory to the python path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal
from app.services.auth_service import register_user
from app.schemas.auth import RegisterRequest
from app.models.users import UserRole

def test_registration():
    db = SessionLocal()
    # Try a very random phone number
    import random
    phone = str(random.randint(1000000000, 9999999999))
    print(f"Testing registration with phone: {phone}")
    
    data = RegisterRequest(
        name="Test User",
        phone=phone,
        password="password123",
        role=UserRole.farmer,
        district="Satara"
    )
    
    try:
        user = register_user(data, db)
        print(f"Registration successful for {user.phone}")
    except Exception as e:
        print(f"Registration failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_registration()
