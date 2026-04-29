from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.harvests import Harvest, HarvestAnomaly
from app.models.users import User
from app.crisp.scorer import score_crops

router = APIRouter(prefix="/api/harvest", tags=["Harvest"])

class StartHarvestRequest(BaseModel):
    farmer_id: int
    field_name: str
    crop_name: str
    season: str
    start_month: int
    end_month: int
    field_size: float
    soil_type: Optional[str] = "loamy"
    irrigation: Optional[str] = "borewell"
    income_level: Optional[str] = "middle"
    expected_days: Optional[int] = 120
    farmer_accepted_recommendation: Optional[bool] = True

class EndHarvestRequest(BaseModel):
    harvest_id: int
    end_feedback: str
    actual_yield: Optional[float] = None
    income_earned: Optional[float] = None
    notes: Optional[str] = None

class AnomalyReportRequest(BaseModel):
    harvest_id: int
    farmer_id: int
    anomaly_type: str
    description: str
    recovery_plan: Optional[str] = None

@router.post("/start")
def start_harvest(
    data: StartHarvestRequest,
    db: Session = Depends(get_db)
):
    farmer = db.query(User).filter(
        User.id == data.farmer_id
    ).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    expected_date = datetime.utcnow() + timedelta(
        days=data.expected_days
    )

    harvest = Harvest(
        farmer_id=data.farmer_id,
        field_name=data.field_name,
        crop_name=data.crop_name,
        season=data.season,
        start_month=data.start_month,
        end_month=data.end_month,
        field_size=data.field_size,
        soil_type=data.soil_type,
        irrigation=data.irrigation,
        income_level=data.income_level,
        expected_harvest_date=expected_date,
        farmer_accepted_recommendation=data.farmer_accepted_recommendation,
        status="active",
        health_status="good"
    )
    db.add(harvest)
    db.commit()
    db.refresh(harvest)

    return {
        "message": "Harvest started successfully",
        "harvest_id": harvest.id,
        "field_name": harvest.field_name,
        "crop_name": harvest.crop_name,
        "season": harvest.season,
        "expected_harvest_date": harvest.expected_harvest_date,
        "status": harvest.status
    }

@router.get("/active/{farmer_id}")
def get_active_harvests(
    farmer_id: int,
    db: Session = Depends(get_db)
):
    harvests = db.query(Harvest).filter(
        Harvest.farmer_id == farmer_id,
        Harvest.status == "active"
    ).all()

    result = []
    for h in harvests:
        days_remaining = None
        progress = 0
        if h.expected_harvest_date:
            total_days = (
                h.expected_harvest_date - h.sowing_date
            ).days
            days_elapsed = (
                datetime.utcnow() - h.sowing_date.replace(tzinfo=None)
            ).days
            days_remaining = max(0, (
                h.expected_harvest_date.replace(tzinfo=None)
                - datetime.utcnow()
            ).days)
            if total_days > 0:
                progress = min(100, int(
                    (days_elapsed / total_days) * 100
                ))

        active_anomalies = db.query(HarvestAnomaly).filter(
            HarvestAnomaly.harvest_id == h.id,
            HarvestAnomaly.status == "active"
        ).count()

        result.append({
            "harvest_id": h.id,
            "field_name": h.field_name,
            "crop_name": h.crop_name,
            "season": h.season,
            "field_size": h.field_size,
            "soil_type": h.soil_type,
            "irrigation": h.irrigation,
            "sowing_date": h.sowing_date,
            "expected_harvest_date": h.expected_harvest_date,
            "days_remaining": days_remaining,
            "progress_percent": progress,
            "health_status": h.health_status,
            "active_anomalies": active_anomalies,
            "status": h.status
        })

    return {
        "farmer_id": farmer_id,
        "active_count": len(result),
        "harvests": result
    }

@router.get("/history/{farmer_id}")
def get_harvest_history(
    farmer_id: int,
    db: Session = Depends(get_db)
):
    harvests = db.query(Harvest).filter(
        Harvest.farmer_id == farmer_id,
        Harvest.status == "completed"
    ).order_by(Harvest.ended_at.desc()).all()

    return {
        "farmer_id": farmer_id,
        "total_seasons": len(harvests),
        "harvests": [
            {
                "harvest_id": h.id,
                "field_name": h.field_name,
                "crop_name": h.crop_name,
                "season": h.season,
                "field_size": h.field_size,
                "sowing_date": h.sowing_date,
                "ended_at": h.ended_at,
                "actual_yield": h.actual_yield,
                "income_earned": h.income_earned,
                "health_status": h.health_status,
                "notes": h.notes
            }
            for h in harvests
        ]
    }

@router.post("/end")
def end_harvest(
    data: EndHarvestRequest,
    db: Session = Depends(get_db)
):
    harvest = db.query(Harvest).filter(
        Harvest.id == data.harvest_id
    ).first()
    if not harvest:
        raise HTTPException(status_code=404, detail="Harvest not found")

    harvest.status = "completed"
    harvest.ended_at = datetime.utcnow()
    harvest.end_feedback = data.end_feedback
    harvest.actual_yield = data.actual_yield
    harvest.income_earned = data.income_earned
    harvest.notes = data.notes
    db.commit()

    return {
        "message": "Harvest ended successfully",
        "harvest_id": harvest.id,
        "crop_name": harvest.crop_name,
        "field_name": harvest.field_name,
        "income_earned": data.income_earned
    }

@router.post("/anomaly")
def report_anomaly(
    data: AnomalyReportRequest,
    db: Session = Depends(get_db)
):
    anomaly = HarvestAnomaly(
        harvest_id=data.harvest_id,
        farmer_id=data.farmer_id,
        anomaly_type=data.anomaly_type,
        description=data.description,
        recovery_plan=data.recovery_plan
    )
    db.add(anomaly)
    db.commit()
    db.refresh(anomaly)

    return {
        "message": "Anomaly reported",
        "anomaly_id": anomaly.id,
        "type": anomaly.anomaly_type
    }

@router.get("/anomalies/{harvest_id}")
def get_harvest_anomalies(
    harvest_id: int,
    db: Session = Depends(get_db)
):
    anomalies = db.query(HarvestAnomaly).filter(
        HarvestAnomaly.harvest_id == harvest_id
    ).order_by(HarvestAnomaly.reported_at.desc()).all()

    return {
        "harvest_id": harvest_id,
        "total": len(anomalies),
        "anomalies": [
            {
                "id": a.id,
                "type": a.anomaly_type,
                "description": a.description,
                "recovery_plan": a.recovery_plan,
                "status": a.status,
                "reported_at": a.reported_at
            }
            for a in anomalies
        ]
    }

@router.get("/recommend/{farmer_id}")
def get_recommendation_for_harvest(
    farmer_id: int,
    season: str,
    start_month: int,
    end_month: int,
    field_size: float = 1.0,
    soil_type: str = "loamy",
    irrigation: str = "borewell",
    income_level: str = "middle",
    district: str = "Pune",
    db: Session = Depends(get_db)
):
    from app.models.buyer_interests import BuyerInterest
    from app.models.crops import Crop

    farmer_profile = {
        "soil_type": soil_type,
        "irrigation": irrigation,
        "last_crop": None,
        "field_size": field_size,
        "district": district,
        "season": season,
        "start_month": start_month,
        "end_month": end_month,
        "income_level": income_level
    }

    last_harvest = db.query(Harvest).filter(
        Harvest.farmer_id == farmer_id,
        Harvest.status == "completed"
    ).order_by(Harvest.ended_at.desc()).first()

    if last_harvest:
        farmer_profile["last_crop"] = last_harvest.crop_name

    buyer_interests_raw = db.query(BuyerInterest).filter(
        BuyerInterest.district == district,
        BuyerInterest.status == "open"
    ).all()

    buyer_interests = []
    for b in buyer_interests_raw:
        crop = db.query(Crop).filter(
            Crop.id == b.crop_id
        ).first()
        if crop:
            buyer_interests.append({
                "crop_name": crop.name,
                "quantity": b.quantity,
                "offered_price": b.offered_price,
                "district": b.district
            })

    recommendations = score_crops(
        farmer_profile,
        buyer_interests=buyer_interests
    )

    return {
        "farmer_id": farmer_id,
        "district": district,
        "season": season,
        "start_month": start_month,
        "end_month": end_month,
        "income_level": income_level,
        "recommendations": recommendations,
        "buyer_demand_active": len(buyer_interests)
    }
