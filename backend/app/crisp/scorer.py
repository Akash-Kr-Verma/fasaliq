from app.crisp.crop_data import CROPS, WATER_SCORE, SWITCH_RISK, SIMILAR_CROPS

def get_soil_score(crop_soil_fit: list, farmer_soil: str) -> float:
    if farmer_soil.lower() in [s.lower() for s in crop_soil_fit]:
        return 1.0
    return 0.3

def get_water_score(crop_water_need: str, farmer_irrigation: str) -> float:
    farmer_map = {
        "canal": "high",
        "borewell": "medium",
        "rainfed": "low",
        "drip": "medium",
        "sprinkler": "medium",
    }
    farmer_water = farmer_map.get(farmer_irrigation.lower(), "medium")
    return WATER_SCORE.get(farmer_water, {}).get(crop_water_need, 0.5)

def get_switch_risk_score(last_crop: str, current_crop: str) -> float:
    if not last_crop:
        return 1.0
    if last_crop == current_crop:
        return SWITCH_RISK["same"]
    similar = SIMILAR_CROPS.get(last_crop, [])
    if current_crop in similar:
        return SWITCH_RISK["similar"]
    return SWITCH_RISK["different"]

def get_msp_score(has_msp: bool) -> float:
    return 1.0 if has_msp else 0.5

def get_demand_score(crop_name: str, district: str,
                     market_prices: list) -> float:
    prices = [
        p["price"] for p in market_prices
        if p["crop_name"] == crop_name
    ]
    if not prices:
        return 0.5
    avg_price = sum(prices) / len(prices)
    if avg_price > 5000:
        return 1.0
    elif avg_price > 3000:
        return 0.8
    elif avg_price > 1500:
        return 0.6
    else:
        return 0.4

def calculate_profit_score(crop: dict, field_size: float) -> float:
    raw = crop["msp"] if crop["has_msp"] else crop["avg_yield"] * 2000
    normalized = min(raw / 10000, 1.0)
    return normalized

def score_crops(farmer_profile: dict, market_prices: list = []) -> list:
    """
    farmer_profile = {
        "soil_type": "loamy",
        "irrigation": "borewell",
        "last_crop": "Wheat",
        "field_size": 2.5,
        "district": "Pune",
        "season": "rabi"
    }
    """
    results = []

    for crop in CROPS:
        if (farmer_profile.get("season") and
                crop["season"] != "annual" and
                crop["season"] != farmer_profile.get("season")):
            continue

        f1 = calculate_profit_score(crop, farmer_profile["field_size"])
        f2_soil = get_soil_score(crop["soil_fit"], farmer_profile["soil_type"])
        f2_water = get_water_score(crop["water_need"], farmer_profile["irrigation"])
        f2 = (f2_soil + f2_water) / 2
        f3 = get_demand_score(
            crop["name"],
            farmer_profile["district"],
            market_prices
        )
        f4 = get_msp_score(crop["has_msp"])
        f5 = get_switch_risk_score(
            farmer_profile.get("last_crop"),
            crop["name"]
        )

        total_score = (
            f1 * 0.30 +
            f2 * 0.25 +
            f3 * 0.20 +
            f4 * 0.15 +
            f5 * 0.10
        )

        income_estimate = (
            crop["avg_yield"] *
            farmer_profile["field_size"] *
            (crop["msp"] if crop["has_msp"] else crop["avg_yield"] * 2000)
        )

        results.append({
            "crop_name": crop["name"],
            "season": crop["season"],
            "score": round(total_score, 4),
            "income_estimate": round(income_estimate, 2),
            "has_msp": crop["has_msp"],
            "msp": crop["msp"],
            "factors": {
                "profit": round(f1, 3),
                "soil_water_fit": round(f2, 3),
                "market_demand": round(f3, 3),
                "msp_safety": round(f4, 3),
                "switch_risk": round(f5, 3),
            }
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:3]