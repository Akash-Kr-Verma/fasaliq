from app.crisp.crop_data import CROPS, WATER_SCORE, SWITCH_RISK, SIMILAR_CROPS

MONTH_SEASON_MAP = {
    1: "rabi", 2: "rabi", 3: "rabi",
    4: "kharif", 5: "kharif", 6: "kharif",
    7: "kharif", 8: "kharif", 9: "kharif",
    10: "rabi", 11: "rabi", 12: "rabi"
}

INCOME_RISK_TOLERANCE = {
    "poor": 0.3,
    "middle": 0.6,
    "rich": 1.0
}

def get_soil_score(crop_soil_fit, farmer_soil):
    if farmer_soil.lower() in [s.lower() for s in crop_soil_fit]:
        return 1.0
    return 0.3

def get_water_score(crop_water_need, farmer_irrigation):
    farmer_map = {
        "canal": "high",
        "borewell": "medium",
        "rainfed": "low",
        "drip": "medium",
        "sprinkler": "medium",
    }
    farmer_water = farmer_map.get(
        farmer_irrigation.lower(), "medium"
    )
    return WATER_SCORE.get(farmer_water, {}).get(
        crop_water_need, 0.5
    )

def get_switch_risk_score(last_crop, current_crop):
    if not last_crop:
        return 1.0
    if last_crop == current_crop:
        return SWITCH_RISK["same"]
    similar = SIMILAR_CROPS.get(last_crop, [])
    if current_crop in similar:
        return SWITCH_RISK["similar"]
    return SWITCH_RISK["different"]

def get_msp_score(has_msp):
    return 1.0 if has_msp else 0.5

def get_demand_score(crop_name, district, market_prices):
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
    return 0.4

def get_buyer_demand_score(
    crop_name, district, end_month, buyer_interests
):
    if not buyer_interests:
        return 0.5
    matching = [
        b for b in buyer_interests
        if b.get("crop_name", "").lower() == crop_name.lower()
    ]
    if not matching:
        return 0.4
    total_quantity = sum(
        b.get("quantity", 0) for b in matching
    )
    if total_quantity > 1000:
        return 1.0
    elif total_quantity > 500:
        return 0.85
    elif total_quantity > 100:
        return 0.7
    return 0.55

def get_income_fit_score(crop, income_level):
    risk_tolerance = INCOME_RISK_TOLERANCE.get(
        income_level.lower(), 0.6
    )
    if not crop.get("has_msp") and risk_tolerance < 0.5:
        return 0.4
    if crop.get("has_msp"):
        return 1.0
    return 0.7

def calculate_profit_score(crop):
    raw = crop["msp"] if crop["has_msp"] else (
        crop["avg_yield"] * 2000
    )
    return min(raw / 10000, 1.0)

def get_recommendation_reasons(
    crop, f1, f2, f3, f4, f5, f6,
    buyer_interests, end_month
):
    reasons = []

    if f3 >= 0.8:
        reasons.append(
            "High market price in your district"
        )
    if f6 >= 0.7:
        matching_buyers = [
            b for b in (buyer_interests or [])
            if b.get("crop_name", "").lower() ==
            crop["name"].lower()
        ]
        if matching_buyers:
            total_qty = sum(
                b.get("quantity", 0)
                for b in matching_buyers
            )
            reasons.append(
                f"Buyers want {total_qty:.0f} kg "
                f"by your harvest month"
            )
        else:
            reasons.append("Good buyer demand expected")
    if f2 >= 0.8:
        reasons.append(
            "Your soil and irrigation suits this crop well"
        )
    if crop.get("has_msp"):
        reasons.append(
            f"Government MSP of ₹{crop['msp']:.0f} "
            f"guarantees minimum income"
        )
    if f5 >= 0.8:
        reasons.append(
            "Good switch from your last crop"
        )
    if not reasons:
        reasons.append(
            "Balanced score across all factors"
        )
    return reasons

def score_crops(
    farmer_profile: dict,
    market_prices: list = [],
    buyer_interests: list = []
) -> list:
    results = []
    season = farmer_profile.get("season", "")
    end_month = farmer_profile.get("end_month", 8)
    income_level = farmer_profile.get(
        "income_level", "middle"
    )

    for crop in CROPS:
        if (season and
                crop["season"] != "annual" and
                crop["season"] != season):
            continue

        f1 = calculate_profit_score(crop)

        f2_soil = get_soil_score(
            crop["soil_fit"],
            farmer_profile["soil_type"]
        )
        f2_water = get_water_score(
            crop["water_need"],
            farmer_profile["irrigation"]
        )
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

        f6 = get_buyer_demand_score(
            crop["name"],
            farmer_profile["district"],
            end_month,
            buyer_interests
        )

        f7 = get_income_fit_score(crop, income_level)

        total_score = (
            f1 * 0.20 +
            f2 * 0.20 +
            f3 * 0.15 +
            f4 * 0.10 +
            f5 * 0.10 +
            f6 * 0.20 +
            f7 * 0.05
        )

        income_estimate = (
            crop["avg_yield"] *
            farmer_profile["field_size"] *
            (crop["msp"] if crop["has_msp"]
             else crop["avg_yield"] * 2000)
        )

        reasons = get_recommendation_reasons(
            crop, f1, f2, f3, f4, f5, f6,
            buyer_interests, end_month
        )

        results.append({
            "crop_name": crop["name"],
            "season": crop["season"],
            "score": round(total_score, 4),
            "income_estimate": round(income_estimate, 2),
            "has_msp": crop["has_msp"],
            "msp": crop["msp"],
            "reasons": reasons,
            "factors": {
                "profit": round(f1, 3),
                "soil_water_fit": round(f2, 3),
                "market_demand": round(f3, 3),
                "msp_safety": round(f4, 3),
                "switch_risk": round(f5, 3),
                "buyer_demand": round(f6, 3),
                "income_fit": round(f7, 3),
            }
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:3]