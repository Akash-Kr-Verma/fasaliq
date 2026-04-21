MARKET_CAPACITY = {
    "Pune": {
        "Onion": 500,
        "Tomato": 300,
        "Wheat": 800,
        "Rice": 600,
        "Soybean": 400,
        "Cotton": 350,
        "Sugarcane": 700,
        "Maize": 450,
        "Turmeric": 200,
        "Chickpea": 300,
    }
}

DEFAULT_CAPACITY = 400

def check_surplus(district: str, crop_counts: dict) -> list:
    """
    crop_counts = {"Onion": 420, "Wheat": 200}
    Returns list of surplus alerts
    """
    alerts = []
    district_capacity = MARKET_CAPACITY.get(district, {})

    for crop_name, farmer_count in crop_counts.items():
        capacity = district_capacity.get(crop_name, DEFAULT_CAPACITY)
        ratio = farmer_count / capacity

        if ratio >= 0.75:
            if ratio >= 1.0:
                severity = "critical"
            elif ratio >= 0.90:
                severity = "high"
            else:
                severity = "medium"

            alerts.append({
                "district": district,
                "crop_name": crop_name,
                "farmer_count": farmer_count,
                "market_capacity": capacity,
                "ratio": round(ratio, 2),
                "severity": severity,
                "message": (
                    f"{farmer_count} farmers in {district} have chosen "
                    f"{crop_name} against a market capacity of {capacity}. "
                    f"Oversupply risk is {severity}."
                )
            })

    return alerts