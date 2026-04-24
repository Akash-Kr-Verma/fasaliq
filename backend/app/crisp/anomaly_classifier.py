import re

# AI Classification Logic (Keyword-based NLP)
ANOMALY_PATTERNS = {
    "heatstroke": [r"heat", r"hot", r"sun", r"burnt", r"dried up", r"high temperature"],
    "over_rain": [r"rain", r"flood", r"heavy rain", r"waterlogging", r"drowned"],
    "irrigation_failure": [r"irrigation", r"water pump", r"no water", r"dry canal", r"drip failed"],
    "pest_attack": [r"pest", r"insect", r"bug", r"worm", r"eaten", r"locust"],
    "disease": [r"disease", r"fungus", r"yellow", r"spots", r"infection", r"rot"],
}

CROP_KEYWORDS = {
    "Strawberry": [r"strawberry", r"strawberries", r"red fruit"],
    "Cotton": [r"cotton", r"kapas", r"white gold"],
    "Soybean": [r"soybean", r"soya"],
    "Wheat": [r"wheat", r"gehu"],
    "Rice": [r"rice", r"paddy", r"dhan"],
}

def classify_anomaly_text(text: str):
    text = text.lower()
    
    # Identify Reason
    detected_reason = "Unclassified"
    for reason, patterns in ANOMALY_PATTERNS.items():
        if any(re.search(p, text) for p in patterns):
            detected_reason = reason.replace("_", " ").capitalize()
            break
            
    # Identify Crop
    detected_crop = "Unknown"
    for crop, patterns in CROP_KEYWORDS.items():
        if any(re.search(p, text) for p in patterns):
            detected_crop = crop
            break
            
    # Map to internal anomaly types
    anomaly_type = "general"
    if "pest" in detected_reason.lower():
        anomaly_type = "pest_attack"
    elif "rain" in detected_reason.lower() or "flood" in detected_reason.lower():
        anomaly_type = "over_water"
    elif "irrigation" in detected_reason.lower():
        anomaly_type = "drought_stress"
    elif "disease" in detected_reason.lower():
        anomaly_type = "disease"
    elif "heat" in detected_reason.lower():
        anomaly_type = "drought_stress"
        
    return {
        "reason": detected_reason,
        "crop": detected_crop,
        "anomaly_type": anomaly_type
    }
