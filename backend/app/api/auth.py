from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, FCMTokenUpdate
from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(data, db)
    return {
        "message": "Registration successful",
        "user_id": user.id,
        "name": user.name,
        "role": user.role.value
    }

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return login_user(data, db)

@router.post("/fcm-token")
def update_fcm_token(data: FCMTokenUpdate, db: Session = Depends(get_db)):
    from app.models.users import User
    from fastapi import HTTPException
    
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.fcm_token = data.fcm_token
    db.commit()
    return {"message": "FCM token updated successfully"}
