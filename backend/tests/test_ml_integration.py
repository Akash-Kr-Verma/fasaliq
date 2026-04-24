import httpx
import asyncio

async def test_recommendation():
    url = "http://localhost:8000/api/crisp/recommend"
    payload = {
        "soil_type": "loamy",
        "irrigation": "borewell",
        "last_crop": "Wheat",
        "field_size": 2.5,
        "district": "Pune",
        "season": "rabi",
        "use_ml": True
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Note: This requires the server to be running.
    # Since I cannot easily run uvicorn in the background and wait for it in a single command block,
    # I will instead run a direct function test of score_crops_ml.
    from app.crisp.ml_scorer import score_crops_ml
    
    farmer_profile = {
        "soil_type": "loamy",
        "irrigation": "borewell",
        "last_crop": "Wheat",
        "field_size": 2.5,
        "district": "Pune",
        "season": "rabi"
    }
    
    print("Testing score_crops_ml directly...")
    recs = score_crops_ml(farmer_profile)
    print(f"Top 3 Recommendations: {recs}")
