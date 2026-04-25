import re

# AI Classification Logic (Keyword-based NLP)
ANOMALY_PATTERNS = {
    "heatstroke": [r"heat", r"hot", r"sun", r"burnt", r"dried up", r"high temperature", r"heatstroke", r"wild weather"],
    "over_rain": [r"rain", r"flood", r"heavy rain", r"waterlogging", r"drowned", r"storm", r"excessive rain"],
    "irrigation_failure": [r"irrigation", r"water pump", r"no water", r"dry canal", r"drip failed", r"poor irrigation", r"pump broken"],
    "pest_attack": [r"pest", r"insect", r"bug", r"worm", r"eaten", r"locust", r"aphids", r"bollworm"],
    "disease": [r"disease", r"fungus", r"yellow", r"spots", r"infection", r"rot", r"mildew", r"blight"],
}

CROP_KEYWORDS = {
    "Strawberry": [r"strawberry", r"strawberries", r"red fruit"],
    "Cotton": [r"cotton", r"kapas", r"white gold"],
    "Soybean": [r"soybean", r"soya"],
    "Wheat": [r"wheat", r"gehu"],
    "Rice": [r"rice", r"paddy", r"dhan"],
    "Sugarcane": [r"sugarcane", r"ganne", r"cane"],
}

def classify_anomaly_text(text: str, weather: str = None, irrigation: str = None):
    text = text.lower()
    
    # 1. Direct inputs take precedence if they indicate a specific failure
    detected_reason = "Unclassified"
    
    if irrigation and ("poor" in irrigation.lower() or "fail" in irrigation.lower() or "none" in irrigation.lower()):
        detected_reason = "Irrigation Failure"
    elif weather and ("heat" in weather.lower() or "hot" in weather.lower()):
        detected_reason = "Heatstroke"
    elif weather and ("rain" in weather.lower() or "flood" in weather.lower() or "storm" in weather.lower()):
        detected_reason = "Over Rain"
    else:
        # Fallback to keyword search in description text
        for reason, patterns in ANOMALY_PATTERNS.items():
            if any(re.search(p, text) for p in patterns):
                detected_reason = reason.replace("_", " ").capitalize()
                break
            
    # 2. Identify Crop
    detected_crop = "Unknown"
    for crop, patterns in CROP_KEYWORDS.items():
        if any(re.search(p, text) for p in patterns):
            detected_crop = crop
            break
            
    # Map to internal anomaly types (used for recovery plan lookup)
    anomaly_type = "general"
    reason_low = detected_reason.lower()
    
    if "pest" in reason_low:
        anomaly_type = "pest_attack"
    elif "rain" in reason_low or "flood" in reason_low:
        anomaly_type = "over_water"
    elif "irrigation" in reason_low:
        anomaly_type = "irrigation_failure"
    elif "disease" in reason_low:
        anomaly_type = "disease"
    elif "heat" in reason_low:
        anomaly_type = "heatstroke"
        
    return {
        "reason": detected_reason,
        "crop": detected_crop,
        "anomaly_type": anomaly_type
    }

