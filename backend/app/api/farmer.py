from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.models.farmer_profiles import FarmerProfile
from app.models.recommendations import Recommendation
from app.models.crops import Crop
from app.models.users import User
from app.crisp.scorer import score_crops

router = APIRouter(prefix="/api/farmer", tags=["Farmer"])

class FarmerProfileInput(BaseModel):
    user_id: int
    field_size: float
    soil_type: str
    irrigation: str
    last_crop: Optional[str] = None
    economic_tier: Optional[str] = "small"

class CropSelectInput(BaseModel):
    user_id: int
    crop_name: str
    season: str

@router.post("/profile")
def save_profile(data: FarmerProfileInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(FarmerProfile).filter(
        FarmerProfile.user_id == data.user_id
    ).first()

    if existing:
        existing.field_size = data.field_size
        existing.soil_type = data.soil_type
        existing.irrigation = data.irrigation
        existing.last_crop = data.last_crop
        existing.economic_tier = data.economic_tier
        db.commit()
        db.refresh(existing)
        return {"message": "Profile updated", "profile_id": existing.id}

    profile = FarmerProfile(
        user_id=data.user_id,
        field_size=data.field_size,
        soil_type=data.soil_type,
        irrigation=data.irrigation,
        last_crop=data.last_crop,
        economic_tier=data.economic_tier
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return {"message": "Profile created", "profile_id": profile.id}

@router.get("/profile/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(FarmerProfile).filter(
        FarmerProfile.user_id == user_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "user_id": user_id,
        "field_size": profile.field_size,
        "soil_type": profile.soil_type,
        "irrigation": profile.irrigation,
        "last_crop": profile.last_crop,
        "economic_tier": profile.economic_tier
    }

@router.get("/recommend/{user_id}")
async def get_recommendation(
    user_id: int,
    season: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.query(FarmerProfile).filter(
        FarmerProfile.user_id == user_id
    ).first()
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Farmer profile not found. Please complete your profile first."
        )

    farmer_input = {
        "soil_type": profile.soil_type,
        "irrigation": profile.irrigation,
        "last_crop": profile.last_crop,
        "field_size": profile.field_size,
        "district": user.district,
        "season": season
    }

    top_crops = await score_crops(farmer_input)

    saved = []
    for item in top_crops:
        crop = db.query(Crop).filter(
            Crop.name == item["crop_name"]
        ).first()
        if crop:
            rec = Recommendation(
                farmer_id=user_id,
                crop_id=crop.id,
                score=item["score"],
                income_estimate=item["income_estimate"],
                selected=False
            )
            db.add(rec)
            saved.append(item)

    db.commit()

    return {
        "user_id": user_id,
        "district": user.district,
        "season": season,
        "top_3_recommendations": top_crops
    }

@router.post("/select-crop")
def select_crop(data: CropSelectInput, db: Session = Depends(get_db)):
    profile = db.query(FarmerProfile).filter(
        FarmerProfile.user_id == data.user_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile.last_crop = data.crop_name
    db.commit()

    return {
        "message": f"Crop {data.crop_name} selected successfully",
        "user_id": data.user_id,
        "selected_crop": data.crop_name,
        "season": data.season
    }

@router.get("/history/{user_id}")
def get_history(user_id: int, db: Session = Depends(get_db)):
    recs = db.query(Recommendation).filter(
        Recommendation.farmer_id == user_id
    ).order_by(Recommendation.created_at.desc()).limit(10).all()

    return {
        "user_id": user_id,
        "recommendations": [
            {
                "crop_id": r.crop_id,
                "score": r.score,
                "income_estimate": r.income_estimate,
                "selected": r.selected,
                "created_at": r.created_at
            }
            for r in recs
        ]
    }