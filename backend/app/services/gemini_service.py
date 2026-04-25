import google.generativeai as genai
import os
import json
import base64
from dotenv import load_dotenv
from app.services.weather_service import get_weather_forecast

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
You are FasalIQ AI — an expert agricultural assistant for Indian farmers.
You speak in Hindi and Marathi based on what the farmer uses.
You are helping farmers identify crop problems and get recovery plans.

Your job in this conversation:
1. Listen carefully to the farmer's problem
2. Ask 1-2 smart follow-up questions to understand better
3. Use weather data provided to correlate symptoms
4. If photo is shared, analyze it for disease/pest/deficiency
5. Identify the anomaly type from this list:
   over_nitrogen, over_water, pest_attack, drought_stress, disease, frost, heat_stress
6. Give a step-by-step recovery plan in Hindi/Marathi
7. At the end of your response, if you have identified an anomaly,
   add this JSON on a new line (farmer won't see it):
   ANOMALY_DETECTED: {"type": "anomaly_type", "confidence": "high/medium/low", "description": "brief description"}

Weather data for farmer's district will be provided in each message.
Keep responses concise and practical. Use simple language farmers understand.
Always respond in the same language the farmer uses (Hindi or Marathi).
"""

ANOMALY_TYPES = [
    "over_nitrogen", "over_water", "pest_attack",
    "drought_stress", "disease", "frost", "heat_stress"
]

async def chat_with_gemini(
    messages: list,
    farmer_district: str,
    image_base64: str = None
) -> dict:
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT
        )

        weather_data = await get_weather_forecast(farmer_district)
        weather_context = format_weather_context(weather_data)

        chat_history = []
        for msg in messages[:-1]:
            chat_history.append({
                "role": msg["role"],
                "parts": [msg["content"]]
            })

        chat = model.start_chat(history=chat_history)

        last_message = messages[-1]["content"]
        full_message = f"{last_message}\n\n[Weather context for {farmer_district}:\n{weather_context}]"

        if image_base64:
            image_data = {
                "mime_type": "image/jpeg",
                "data": image_base64
            }
            response = chat.send_message([full_message, image_data])
        else:
            response = chat.send_message(full_message)

        response_text = response.text
        anomaly_data = extract_anomaly(response_text)
        clean_response = clean_anomaly_from_text(response_text)

        return {
            "response": clean_response,
            "anomaly_detected": anomaly_data,
            "weather_used": weather_context
        }

    except Exception as e:
        return {
            "response": "माफ करें, अभी सेवा उपलब्ध नहीं है। कृपया थोड़ी देर बाद प्रयास करें।",
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
