import httpx
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY", "")

CROP_NAME_MAP = {
    "Wheat": "Wheat",
    "Rice": "Rice",
    "Onion": "Onion",
    "Tomato": "Tomato",
    "Soybean": "Soybean",
    "Cotton": "Cotton",
    "Maize": "Maize",
    "Chickpea": "Gram",
    "Sugarcane": "Sugarcane",
    "Turmeric": "Turmeric",
}

FALLBACK_PRICES = {
    "Wheat": 2275.0,
    "Rice": 2183.0,
    "Onion": 1500.0,
    "Tomato": 2000.0,
    "Soybean": 4600.0,
    "Cotton": 7121.0,
    "Maize": 2090.0,
    "Chickpea": 5440.0,
    "Sugarcane": 340.0,
    "Turmeric": 8000.0,
}

async def get_mandi_price(crop_name: str, district: str) -> dict:
    api_crop = CROP_NAME_MAP.get(crop_name, crop_name)

    if not DATA_GOV_API_KEY:
        return {
            "crop": crop_name,
            "district": district,
            "price": FALLBACK_PRICES.get(crop_name, 2000.0),
            "source": "fallback",
            "date": datetime.now().strftime("%Y-%m-%d")
        }

    try:
        url = (
            f"https://api.data.gov.in/resource/"
            f"9ef84268-d588-465a-a308-a864a43d0070"
            f"?api-key={DATA_GOV_API_KEY}"
            f"&format=json"
            f"&filters[State]=Maharashtra"
            f"&filters[District]={district}"
            f"&filters[Commodity]={api_crop}"
            f"&limit=5"
        )

        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            data = response.json()

        records = data.get("records", [])
        if not records:
            return {
                "crop": crop_name,
                "district": district,
                "price": FALLBACK_PRICES.get(crop_name, 2000.0),
                "source": "fallback — no records found",
                "date": datetime.now().strftime("%Y-%m-%d")
            }

        latest = records[0]
        modal_price = float(latest.get("Modal_Price", 0))

        return {
            "crop": crop_name,
            "district": district,
            "price": modal_price,
            "market": latest.get("Market", ""),
            "source": "Agmarknet via data.gov.in",
            "date": latest.get("Arrival_Date", "")
        }

    except Exception as e:
        return {
            "crop": crop_name,
            "district": district,
            "price": FALLBACK_PRICES.get(crop_name, 2000.0),
            "source": "fallback — API error",
            "date": datetime.now().strftime("%Y-%m-%d")
        }

async def get_all_prices_for_district(district: str) -> list:
    prices = []
    for crop_name in CROP_NAME_MAP.keys():
        price_data = await get_mandi_price(crop_name, district)
        prices.append(price_data)
    return prices