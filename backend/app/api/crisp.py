from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.crisp.scorer import score_crops
from app.crisp.anomaly_advisor import get_recovery_plan
from app.crisp.surplus_checker import check_surplus

router = APIRouter(prefix="/api/crisp", tags=["CRISP Engine"])

class FarmerInput(BaseModel):
    soil_type: str
    irrigation: str
    last_crop: Optional[str] = None
    field_size: float
    district: str
    season: str

class AnomalyInput(BaseModel):
    anomaly_type: str

class SurplusInput(BaseModel):
    district: str
    crop_counts: dict

@router.post("/recommend")
def get_recommendation(data: FarmerInput):
    farmer_profile = {
        "soil_type": data.soil_type,
        "irrigation": data.irrigation,
        "last_crop": data.last_crop,
        "field_size": data.field_size,
        "district": data.district,
        "season": data.season,
    }
    recommendations = score_crops(farmer_profile)
    return {
        "district": data.district,
        "season": data.season,
        "top_3_crops": recommendations
    }

@router.post("/anomaly-recovery")
def anomaly_recovery(data: AnomalyInput):
    plan = get_recovery_plan(data.anomaly_type)
    return {
        "anomaly_type": data.anomaly_type,
        "recovery_plan": plan
    }

@router.post("/surplus-check")
def surplus_check(data: SurplusInput):
    alerts = check_surplus(data.district, data.crop_counts)
    return {
        "district": data.district,
        "alerts": alerts,
        "total_alerts": len(alerts)
    }