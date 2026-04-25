from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.crisp.ml_scorer import score_crops_ml
from app.crisp.scorer import score_crops
from app.crisp.anomaly_advisor import get_recovery_plan
from app.crisp.surplus_checker import check_surplus
from app.crisp.anomaly_classifier import classify_anomaly_text
from app.models.anomalies import Anomaly
from app.models.crops import Crop
from app.models.users import User
from app.core.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
import json

router = APIRouter(prefix="/api/crisp", tags=["CRISP Engine"])

class FarmerInput(BaseModel):
    soil_type: str
    irrigation: str
    last_crop: Optional[str] = None
    field_size: float
    district: str
    season: str
    use_ml: Optional[bool] = True

class AnomalyInput(BaseModel):
    anomaly_type: str

class SurplusInput(BaseModel):
    district: str
    crop_counts: dict

@router.post("/recommend")
async def get_recommendation(data: FarmerInput):
    farmer_profile = {
        "soil_type": data.soil_type,
        "irrigation": data.irrigation,
        "last_crop": data.last_crop,
        "field_size": data.field_size,
        "district": data.district,
        "season": data.season,
    }

    if data.use_ml:
        try:
            recommendations = score_crops_ml(farmer_profile)
            model_used = "Databricks RandomForest ML"
        except Exception as e:
            print(f"ML Scoring Error: {e}")
            recommendations = await score_crops(farmer_profile)
            model_used = "Weighted scoring (fallback)"
    else:
        recommendations = await score_crops(farmer_profile)
        model_used = "Weighted scoring"

    return {
        "district": data.district,
        "season": data.season,
        "model_used": model_used,
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

class ReportAnomalyInput(BaseModel):
    farmer_id: int
    description: str
    weather_condition: Optional[str] = None
    irrigation_status: Optional[str] = None

@router.post("/report-anomaly")
def report_anomaly(data: ReportAnomalyInput, db: Session = Depends(get_db)):
    # 1. AI Classification
    classification = classify_anomaly_text(
        data.description, 
        weather=data.weather_condition, 
        irrigation=data.irrigation_status
    )
    
    # 2. Find Crop ID (if possible)
    crop = db.query(Crop).filter(Crop.name == classification["crop"]).first()
    if not crop:
        # Fallback to a default or first available crop for record-keeping if needed, 
        # but here we'll just use a generic ID or leave it. 
        # Let's assume we need a crop_id as per model constraints.
        crop = db.query(Crop).first() 

    # 3. Get Recovery Plan
    recovery = get_recovery_plan(classification["anomaly_type"])
    
    # 4. Save to DB
    new_anomaly = Anomaly(
        farmer_id=data.farmer_id,
        crop_id=crop.id,
        anomaly_type=classification["anomaly_type"],
        detected_crop=classification["crop"],
        reason=classification["reason"],
        description=data.description,
        recovery_plan=json.dumps(recovery["steps"])
    )

    
    db.add(new_anomaly)
    db.commit()
    db.refresh(new_anomaly)
    
    return {
        "message": "Anomaly reported and classified by FasalIQ AI",
        "classification": classification,
        "recovery_plan": recovery
    }