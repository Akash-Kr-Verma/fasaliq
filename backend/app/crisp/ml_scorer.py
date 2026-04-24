import pickle
import os
import numpy as np
from pathlib import Path

MODEL_DIR = Path(__file__).parent / "models"

def load_models():
    with open(MODEL_DIR / "clf.pkl", "rb") as f:
        clf = pickle.load(f)
    with open(MODEL_DIR / "reg.pkl", "rb") as f:
        reg = pickle.load(f)
    with open(MODEL_DIR / "encoders.pkl", "rb") as f:
        encoders = pickle.load(f)
    return clf, reg, encoders

def predict_crop_score(
    crop: str,
    soil_type: str,
    irrigation: str,
    district: str,
    field_size: float,
    market_price: float,
    buyer_demand: float,
    has_msp: int,
    weather_risk: float,
    last_crop_same: int,
    soil_fit: int,
    season_match: int
) -> dict:
    try:
        clf, reg, encoders = load_models()

        crop_enc = encoders["crop"].transform([crop])[0]
        soil_enc = encoders["soil"].transform([soil_type])[0]
        irr_enc = encoders["irrigation"].transform([irrigation])[0]
        dist_enc = encoders["district"].transform([district])[0]

        features = np.array([[
            crop_enc, soil_enc, irr_enc, dist_enc,
            field_size, market_price, buyer_demand,
            has_msp, weather_risk, last_crop_same,
            soil_fit, season_match
        ]])

        success_prob = clf.predict_proba(features)[0][1]
        income_est = reg.predict(features)[0]

        return {
            "success_probability": round(float(success_prob), 4),
            "income_estimate": round(float(income_est), 2),
            "model": "RandomForest_v1",
            "source": "databricks_mlflow"
        }

    except Exception as e:
        return {
            "success_probability": 0.5,
            "income_estimate": 0.0,
            "model": "fallback",
            "error": str(e)
        }

def score_crops_ml(farmer_profile: dict) -> list:
    from app.crisp.crop_data import CROPS

    results = []

    for crop in CROPS:
        if (farmer_profile.get("season") and
                crop["season"] != "annual" and
                crop["season"] != farmer_profile.get("season")):
            continue

        soil_fit = 1 if farmer_profile["soil_type"].lower() in [
            s.lower() for s in crop.get("soil_fit", [])
        ] else 0

        season_match = 1 if crop["season"] == farmer_profile.get(
            "season", "") else 0

        last_crop_same = 1 if farmer_profile.get(
            "last_crop") == crop["name"] else 0

        prediction = predict_crop_score(
            crop=crop["name"],
            soil_type=farmer_profile["soil_type"],
            irrigation=farmer_profile["irrigation"],
            district=farmer_profile["district"],
            field_size=farmer_profile["field_size"],
            market_price=crop.get("msp", 2000.0),
            buyer_demand=0.7,
            has_msp=1 if crop.get("has_msp") else 0,
            weather_risk=0.2,
            last_crop_same=last_crop_same,
            soil_fit=soil_fit,
            season_match=season_match
        )

        results.append({
            "crop_name": crop["name"],
            "season": crop["season"],
            "score": prediction["success_probability"],
            "income_estimate": prediction["income_estimate"],
            "has_msp": crop.get("has_msp", False),
            "msp": crop.get("msp", 0),
            "model_used": prediction["model"],
            "factors": {
                "soil_fit": soil_fit,
                "season_match": season_match,
                "last_crop_same": last_crop_same,
            }
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:3]
