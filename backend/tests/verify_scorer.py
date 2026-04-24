import asyncio
import os
from unittest.mock import patch, MagicMock

# Mock settings before importing app components
os.environ["DATABRICKS_HOST"] = "https://adb-test.cloud.databricks.com"
os.environ["DATABRICKS_TOKEN"] = "dapi_mock_token"
os.environ["DATABRICKS_MODEL_ENDPOINT"] = "test_model"

from app.crisp.scorer import score_crops

async def test_scorer():
    farmer_profile = {
        "soil_type": "loamy",
        "irrigation": "borewell",
        "last_crop": "Wheat",
        "field_size": 2.5,
        "district": "Pune",
        "season": "rabi"
    }
    
    # Mock the HTTP call to Databricks
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Return probability 1.0 for the first few crops
        mock_response.json.return_value = {"predictions": [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]}
        mock_post.return_value = mock_response
        
        print("Running score_crops...")
        results = await score_crops(farmer_profile)
        
        print("\nResults:")
        for res in results:
            print(f"Crop: {res['crop_name']}, Score: {res['score']}")
        
        assert len(results) <= 3
        print("\nVerification successful!")

if __name__ == "__main__":
    asyncio.run(test_scorer())
