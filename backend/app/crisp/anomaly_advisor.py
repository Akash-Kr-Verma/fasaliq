ANOMALY_RECOVERY = {
    "over_nitrogen": {
        "title": "Excess nitrogen detected",
        "steps": [
            "Stop all nitrogen-based fertilizer immediately",
            "Irrigate heavily to leach excess nitrogen from root zone",
            "Apply potassium-rich fertilizer to balance nutrients",
            "Monitor leaf color — yellowing should reduce in 7-10 days",
            "Avoid further fertilization for at least 3 weeks",
        ],
        "severity": "medium",
    },
    "over_water": {
        "title": "Waterlogging detected",
        "steps": [
            "Create drainage channels immediately to remove standing water",
            "Stop all irrigation for minimum 5-7 days",
            "Apply fungicide to prevent root rot",
            "Loosen topsoil carefully to improve aeration",
            "Monitor for yellowing leaves as a sign of root damage",
        ],
        "severity": "high",
    },
    "pest_attack": {
        "title": "Pest infestation reported",
        "steps": [
            "Identify pest type before applying any pesticide",
            "Apply neem-based organic spray as first response",
            "Set up sticky traps around the field boundary",
            "Contact your local Krishi Kendra for specific pesticide advice",
            "Document affected area and report to insurance if over 30% damage",
        ],
        "severity": "high",
    },
    "drought_stress": {
        "title": "Drought stress detected",
        "steps": [
            "Switch to drip irrigation immediately to conserve water",
            "Apply mulch around plants to reduce soil moisture loss",
            "Apply anti-transpirant spray to reduce leaf water loss",
            "Prioritize water for youngest and most productive plants",
            "Consider early harvest if stress continues beyond 2 weeks",
        ],
        "severity": "high",
    },
    "disease": {
        "title": "Crop disease reported",
        "steps": [
            "Remove and destroy visibly infected plants immediately",
            "Apply appropriate fungicide or bactericide",
            "Avoid overhead irrigation — switch to drip or furrow",
            "Increase spacing between plants for better air circulation",
            "Report to Krishi Vigyan Kendra for disease identification",
        ],
        "severity": "medium",
    },
    "frost": {
        "title": "Frost damage reported",
        "steps": [
            "Irrigate lightly — moist soil retains heat better than dry",
            "Apply potassium spray to improve frost tolerance",
            "Cover young plants with cloth or plastic overnight",
            "Avoid pruning frost-damaged parts for at least 2 weeks",
            "Assess full damage after temperatures normalise",
        ],
        "severity": "medium",
    },
}

def get_recovery_plan(anomaly_type: str) -> dict:
    plan = ANOMALY_RECOVERY.get(anomaly_type.lower())
    if not plan:
        return {
            "title": "Unknown anomaly reported",
            "steps": [
                "Document the issue with photos",
                "Contact your local Krishi Kendra immediately",
                "Do not apply any chemicals without expert advice",
            ],
            "severity": "unknown",
        }
    return plan