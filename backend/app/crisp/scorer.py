import httpx
from app.core.config import settings
from app.crisp.crop_data import CROPS, WATER_SCORE, SWITCH_RISK, SIMILAR_CROPS

# Mappings for Label Encoding (matching training notebook)
MAPPINGS = {
    "crop": {
        "Chickpea": 0, "Cotton": 1, "Maize": 2, "Onion": 3, "Rice": 4,
        "Soybean": 5, "Sugarcane": 6, "Tomato": 7, "Turmeric": 8, "Wheat": 9
    },
    "soil_type": {
        "black": 0, "clay": 1, "loamy": 2, "sandy": 3
    },
    "irrigation": {
        "borewell": 0, "canal": 1, "drip": 2, "rainfed": 3
    },
    "district": {
        "Aurangabad": 0, "Kolhapur": 1, "Latur": 2, "Nagpur": 3,
        "Nashik": 4, "Pune": 5, "Satara": 6, "Solapur": 7
    }
}

async def get_mlflow_scores(feature_list: list) -> list:
    """
    Calls Databricks MLflow Serving endpoint to get predictions.
    """
    if not settings.DATABRICKS_HOST or not settings.DATABRICKS_TOKEN:
        # Fallback to dummy scores if not configured
        return [0.5] * len(feature_list)

    url = f"{settings.DATABRICKS_HOST}/serving-endpoints/{settings.DATABRICKS_MODEL_ENDPOINT}/invocations"
    headers = {"Authorization": f"Bearer {settings.DATABRICKS_TOKEN}"}
    
    # MLflow expects data in 'dataframe_split' or 'dataframe_records' format
    payload = {
        "dataframe_records": feature_list
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            # MLflow returns predictions. We want the probability if available, 
            # but RandomForestClassifier.predict usually returns the class.
            # If the model was logged with 'predict_proba', we'd get that.
            # For now, we assume it returns the class or we use the probability if provided.
            return data.get("predictions", [0] * len(feature_list))
    except Exception as e:
        print(f"Error calling MLflow: {e}")
        return [0.0] * len(feature_list)

def get_soil_fit(crop_soil_fit: list, farmer_soil: str) -> int:
    return 1 if farmer_soil.lower() in [s.lower() for s in crop_soil_fit] else 0

def get_demand_value(crop_name: str, market_prices: list) -> float:
    prices = [
        p["price"] for p in market_prices
        if p.get("crop") == crop_name or p.get("crop_name") == crop_name
    ]
    if not prices: return 0.5
    avg_price = sum(prices) / len(prices)
    return min(avg_price / 10000, 1.0) # Normalized demand proxy

async def score_crops(farmer_profile: dict, market_prices: list = []) -> list:
    candidate_crops = []
    features_to_predict = []

    for crop in CROPS:
        # Filter by season
        if (farmer_profile.get("season") and
                crop["season"] != "annual" and
                crop["season"] != farmer_profile.get("season")):
            continue

        # Prepare features for the model
        # Order: crop, soil_type, irrigation, district, field_size, market_price, 
        # buyer_demand, has_msp, weather_risk, last_crop_same, soil_fit, season_match
        
        soil_fit = get_soil_fit(crop["soil_fit"], farmer_profile["soil_type"])
        # Simplified season match for demo
        season_match = 1 if crop["season"] == farmer_profile.get("season") else 0
        last_crop_same = 1 if farmer_profile.get("last_crop") == crop["name"] else 0
        
        # Mapping categories to codes
        crop_code = MAPPINGS["crop"].get(crop["name"], 0)
        soil_code = MAPPINGS["soil_type"].get(farmer_profile["soil_type"], 2) # default loamy
        irr_code = MAPPINGS["irrigation"].get(farmer_profile["irrigation"], 1) # default canal
        dist_code = MAPPINGS["district"].get(farmer_profile["district"], 5) # default Pune
        
        feat = {
            "crop": crop_code,
            "soil_type": soil_code,
            "irrigation": irr_code,
            "district": dist_code,
            "field_size": float(farmer_profile["field_size"]),
            "market_price": float(get_demand_value(crop["name"], market_prices) * 8000), # Synthetic price
            "buyer_demand": 0.7, # Placeholder or dynamic if available
            "has_msp": 1 if crop["has_msp"] else 0,
            "weather_risk": 0.2, # Placeholder
            "last_crop_same": last_crop_same,
            "soil_fit": soil_fit,
            "season_match": season_match
        }
        
        features_to_predict.append(feat)
        candidate_crops.append(crop)

    if not candidate_crops:
        return []

    # Get scores from MLflow
    scores = await get_mlflow_scores(features_to_predict)
    
    results = []
    for i, crop in enumerate(candidate_crops):
        score = float(scores[i]) if i < len(scores) else 0.0
        
        # Estimate income (same as before or could be model-based)
        income_estimate = (
            crop["avg_yield"] *
            farmer_profile["field_size"] *
            (crop["msp"] if crop["has_msp"] else crop["avg_yield"] * 2000)
        )

        results.append({
            "crop_name": crop["name"],
            "season": crop["season"],
            "score": round(score, 4),
            "income_estimate": round(income_estimate, 2),
            "has_msp": crop["has_msp"],
            "msp": crop["msp"]
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:3]