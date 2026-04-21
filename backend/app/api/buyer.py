from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.models.buyer_interests import BuyerInterest
from app.models.market_prices import MarketPrice
from app.models.crops import Crop
from app.models.users import User
from app.models.recommendations import Recommendation

router = APIRouter(prefix="/api/buyer", tags=["Buyer"])

class BuyerInterestInput(BaseModel):
    buyer_id: int
    crop_name: str
    district: str
    quantity: float
    offered_price: float

class UpdateInterestInput(BaseModel):
    status: str

@router.post("/interest")
def place_interest(
    data: BuyerInterestInput,
    db: Session = Depends(get_db)
):
    buyer = db.query(User).filter(User.id == data.buyer_id).first()
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    crop = db.query(Crop).filter(Crop.name == data.crop_name).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    interest = BuyerInterest(
        buyer_id=data.buyer_id,
        crop_id=crop.id,
        district=data.district,
        quantity=data.quantity,
        offered_price=data.offered_price,
        status="open"
    )
    db.add(interest)
    db.commit()
    db.refresh(interest)

    return {
        "message": "Purchase interest placed successfully",
        "interest_id": interest.id,
        "crop": data.crop_name,
        "district": data.district,
        "quantity": data.quantity,
        "offered_price": data.offered_price,
        "status": "open"
    }

@router.get("/interests/{buyer_id}")
def get_my_interests(buyer_id: int, db: Session = Depends(get_db)):
    interests = db.query(BuyerInterest).filter(
        BuyerInterest.buyer_id == buyer_id
    ).all()

    return {
        "buyer_id": buyer_id,
        "total": len(interests),
        "interests": [
            {
                "id": i.id,
                "crop_id": i.crop_id,
                "district": i.district,
                "quantity": i.quantity,
                "offered_price": i.offered_price,
                "status": i.status,
                "created_at": i.created_at
            }
            for i in interests
        ]
    }

@router.get("/availability")
def get_crop_availability(
    district: str,
    season: str,
    db: Session = Depends(get_db)
):
    recs = db.query(Recommendation).join(
        User, Recommendation.farmer_id == User.id
    ).filter(
        User.district == district
    ).all()

    crop_counts = {}
    for rec in recs:
        crop = db.query(Crop).filter(Crop.id == rec.crop_id).first()
        if crop:
            if crop.name not in crop_counts:
                crop_counts[crop.name] = {
                    "crop_name": crop.name,
                    "season": crop.season,
                    "farmer_count": 0,
                    "msp": crop.msp,
                    "has_msp": crop.has_msp
                }
            crop_counts[crop.name]["farmer_count"] += 1

    return {
        "district": district,
        "season": season,
        "available_crops": list(crop_counts.values())
    }

@router.get("/prices")
def get_price_trends(
    crop_name: str,
    district: str,
    db: Session = Depends(get_db)
):
    crop = db.query(Crop).filter(Crop.name == crop_name).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    prices = db.query(MarketPrice).filter(
        MarketPrice.crop_id == crop.id,
        MarketPrice.district == district
    ).order_by(MarketPrice.date.desc()).limit(30).all()

    if not prices:
        return {
            "crop_name": crop_name,
            "district": district,
            "msp": crop.msp,
            "has_msp": crop.has_msp,
            "message": "No market price data available yet",
            "prices": []
        }

    return {
        "crop_name": crop_name,
        "district": district,
        "msp": crop.msp,
        "has_msp": crop.has_msp,
        "prices": [
            {
                "price": p.price,
                "date": p.date,
                "source": p.source
            }
            for p in prices
        ]
    }

@router.put("/interest/{interest_id}")
def update_interest_status(
    interest_id: int,
    data: UpdateInterestInput,
    db: Session = Depends(get_db)
):
    interest = db.query(BuyerInterest).filter(
        BuyerInterest.id == interest_id
    ).first()
    if not interest:
        raise HTTPException(status_code=404, detail="Interest not found")

    valid_statuses = ["open", "negotiating", "closed", "cancelled"]
    if data.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )

    interest.status = data.status
    db.commit()

    return {
        "message": "Status updated",
        "interest_id": interest_id,
        "new_status": data.status
    }