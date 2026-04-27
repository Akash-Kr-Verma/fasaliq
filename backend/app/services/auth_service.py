from sqlalchemy.orm import Session
from app.models.users import User, UserRole
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException, status

def register_user(data: RegisterRequest, db: Session):
    print(f"DEBUG: Received registration request for data: {data}")
    print(f"DEBUG: Checking if user with phone {data.phone} exists...")
    existing = db.query(User).filter(
        User.phone == data.phone
    ).first()
    print(f"DEBUG: Found existing user: {existing}")
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )

    if data.email:
        existing_email = db.query(User).filter(User.email == data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    user = User(
        name=data.name,
        phone=data.phone,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
        district=data.district,
        state=data.state
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        print(f"DEBUG: Error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed: Possible duplicate phone or email"
        )
    return user

def login_user(data: LoginRequest, db: Session):
    user = db.query(User).filter(
        User.phone == data.phone
    ).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone or password"
        )

    token = create_access_token(data={
        "sub": str(user.id),
        "role": user.role.value
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role.value,
        "user_id": user.id,
        "name": user.name
    }

def get_current_user(token: str, db: Session):
    from app.core.security import decode_token
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    user = db.query(User).filter(
        User.id == int(payload.get("sub"))
    ).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user
