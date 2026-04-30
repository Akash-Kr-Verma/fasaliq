from google import genai
from google.genai import types
import os
import json
from dotenv import load_dotenv
from app.services.weather_service import get_weather_forecast

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
You are FasalIQ AI — an expert agricultural assistant for Indian farmers.
You speak in Hindi and Marathi based on what the farmer uses.

You will be given the farmer's ACTIVE HARVEST CONTEXT at the start of each message.
This tells you exactly which crop they are growing, which field, soil type,
irrigation, how many days since sowing, and current health status.
USE this context to give specific, accurate advice.

Your job:
1. Listen to the farmer's problem
2. Ask 1-2 focused follow-up questions using the crop/field context
3. Cross-check with weather data provided
4. If photo shared — analyze for disease/pest/deficiency
5. Diagnose the exact problem for their specific crop
6. Give step-by-step recovery plan in Hindi/Marathi
7. At end of response if anomaly identified add on new line:
   ANOMALY_DETECTED: {"type": "anomaly_type", "confidence": "high/medium/low", "description": "brief description"}

Anomaly types: over_nitrogen, over_water, pest_attack,
drought_stress, disease, frost, heat_stress, waterlogging,
nutrient_deficiency, unknown

Keep responses short and practical.
Use simple language. Farmers may be outdoors.
Always respond in the language the farmer uses.
"""

async def chat_with_gemini(
    messages: list,
    farmer_district: str,
    harvest_context: str = "",
    image_base64: str = None
) -> dict:
    try:
        weather_data = await get_weather_forecast(farmer_district)
        weather_context = format_weather_context(weather_data)

        context_block = ""
        if harvest_context:
            context_block = (
                f"\n\n[FARMER'S ACTIVE HARVEST: {harvest_context}]"
            )

        history = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=msg["content"])]
                )
            )

        last_message = messages[-1]["content"]
        full_message = (
            f"{last_message}"
            f"{context_block}"
            f"\n\n[Weather context for {farmer_district}:\n{weather_context}]"
        )

        parts = [types.Part(text=full_message)]

        if image_base64:
            parts.append(types.Part(
                inline_data=types.Blob(
                    mime_type="image/jpeg",
                    data=image_base64
                )
            ))

        history.append(
            types.Content(role="user", parts=parts)
        )

        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
                max_output_tokens=1024,
            )
        )

        response_text = response.text
        anomaly_data = extract_anomaly(response_text)
        clean_response = clean_anomaly_from_text(response_text)

        return {
            "response": clean_response,
            "anomaly_detected": anomaly_data,
            "weather_used": weather_context
        }

    except Exception as e:
        print(f"Gemini Error: {e}")
        return {
            "response": (
                "माफ करें, अभी सेवा उपलब्ध नहीं है। "
                "कृपया थोड़ी देर बाद प्रयास करें।"
            ),
            "anomaly_detected": None,
            "error": str(e)
        }

def format_weather_context(weather_data: dict) -> str:
    forecast = weather_data.get("forecast", [])
    if not forecast:
        return "Weather data unavailable"
    lines = []
    for day in forecast[:3]:
        alert = f" | Alert: {day['alert']}" if day.get('alert') else ""
        lines.append(
            f"{day['date']}: Max {day['max_temp']}°C, "
            f"Rain {day['rainfall_mm']}mm, "
            f"Wind {day['windspeed_kmh']}km/h{alert}"
        )
    return "\n".join(lines)

def extract_anomaly(text: str) -> dict:
    try:
        if "ANOMALY_DETECTED:" in text:
            json_str = text.split("ANOMALY_DETECTED:")[1].strip()
            json_str = json_str.split("\n")[0].strip()
            return json.loads(json_str)
    except:
        pass
    return None

def clean_anomaly_from_text(text: str) -> str:
    if "ANOMALY_DETECTED:" in text:
        return text.split("ANOMALY_DETECTED:")[0].strip()
    return text.strip()
