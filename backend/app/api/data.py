from fastapi import APIRouter
from app.services.weather_service import get_weather_forecast
from app.services.market_price_service import (
    get_mandi_price,
    get_all_prices_for_district
)

router = APIRouter(prefix="/api/data", tags=["Live Data"])

@router.get("/weather/{district}")
async def weather(district: str):
    return await get_weather_forecast(district)

@router.get("/price/{crop_name}/{district}")
async def price(crop_name: str, district: str):
    return await get_mandi_price(crop_name, district)

@router.get("/prices/{district}")
async def all_prices(district: str):
    prices = await get_all_prices_for_district(district)
    return {
        "district": district,
        "total_crops": len(prices),
        "prices": prices
    }