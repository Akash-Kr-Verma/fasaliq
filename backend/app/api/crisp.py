from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.crisp.ml_scorer import score_crops_ml
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