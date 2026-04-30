from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
from app.core.database import get_db
from app.models.chat_sessions import ChatSession, ChatMessage
from app.models.users import User
from app.models.harvests import Harvest, HarvestAnomaly
from app.services.gemini_service import chat_with_gemini

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class StartSessionRequest(BaseModel):
    farmer_id: int
    harvest_id: Optional[int] = None

class SendMessageRequest(BaseModel):
    session_id: str
    message: str
    image_base64: Optional[str] = None
    message_type: Optional[str] = "text"

@router.post("/start")
async def start_session(
    data: StartSessionRequest,
    db: Session = Depends(get_db)
):
    farmer = db.query(User).filter(
        User.id == data.farmer_id
    ).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    harvest = None
    harvest_context = ""

    if data.harvest_id:
        harvest = db.query(Harvest).filter(
            Harvest.id == data.harvest_id,
            Harvest.farmer_id == data.farmer_id
        ).first()
    else:
        harvest = db.query(Harvest).filter(
            Harvest.farmer_id == data.farmer_id,
            Harvest.status == "active"
        ).order_by(Harvest.created_at.desc()).first()

    if harvest:
        from datetime import datetime
        days_elapsed = (
            datetime.utcnow() -
            harvest.sowing_date.replace(tzinfo=None)
        ).days
        harvest_context = (
            f"Crop: {harvest.crop_name}, "
            f"Field: {harvest.field_name}, "
            f"Size: {harvest.field_size} acres, "
            f"Soil: {harvest.soil_type}, "
            f"Irrigation: {harvest.irrigation}, "
            f"Days since sowing: {days_elapsed}, "
            f"Health: {harvest.health_status}, "
            f"Season: {harvest.season}"
        )

    session_id = str(uuid.uuid4())

    session = ChatSession(
        farmer_id=data.farmer_id,
        session_id=session_id,
        harvest_id=harvest.id if harvest else None,
        status="active"
    )
    db.add(session)

    if harvest:
        welcome = (
            f"नमस्ते! मैं FasalIQ AI हूं। 🌾\n"
            f"मैं देख रहा हूं आपने **{harvest.crop_name}** "
            f"'{harvest.field_name}' खेत में लगाई है।\n"
            f"क्या कोई समस्या है? बताइए, मैं मदद करूंगा।\n\n"
            f"नमस्कार! मी FasalIQ AI आहे. 🌾\n"
            f"तुमच्या **{harvest.crop_name}** पिकाबद्दल "
            f"'{harvest.field_name}' शेतात काही समस्या आहे का?"
        )
    else:
        welcome = (
            "नमस्ते! मैं FasalIQ AI हूं। "
            "आपकी फसल में क्या समस्या है? "
            "मुझे बताएं, मैं आपकी मदद करूंगा। 🌾\n\n"
            "नमस्कार! मी FasalIQ AI आहे. "
            "तुमच्या पिकात काय समस्या आहे? "
            "मला सांगा, मी मदत करेन. 🌾"
        )

    welcome_msg = ChatMessage(
        session_id=session_id,
        role="model",
        content=welcome,
        message_type="text"
    )
    db.add(welcome_msg)
    db.commit()

    return {
        "session_id": session_id,
        "farmer_id": data.farmer_id,
        "harvest_id": harvest.id if harvest else None,
        "crop_name": harvest.crop_name if harvest else None,
        "field_name": harvest.field_name if harvest else None,
        "harvest_context": harvest_context,
        "welcome_message": welcome,
        "status": "active"
    }

@router.post("/message")
async def send_message(
    data: SendMessageRequest,
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter(
        ChatSession.session_id == data.session_id
    ).first()
    if not session:
        raise HTTPException(
            status_code=404, detail="Session not found"
        )

    farmer = db.query(User).filter(
        User.id == session.farmer_id
    ).first()

    harvest = None
    harvest_context = ""
    if session.harvest_id:
        harvest = db.query(Harvest).filter(
            Harvest.id == session.harvest_id
        ).first()
        if harvest:
            from datetime import datetime
            days_elapsed = (
                datetime.utcnow() -
                harvest.sowing_date.replace(tzinfo=None)
            ).days
            harvest_context = (
                f"Active crop: {harvest.crop_name}, "
                f"Field: {harvest.field_name}, "
                f"Size: {harvest.field_size} acres, "
                f"Soil: {harvest.soil_type}, "
                f"Irrigation: {harvest.irrigation}, "
                f"Days since sowing: {days_elapsed}, "
                f"Health status: {harvest.health_status}, "
                f"Season: {harvest.season}"
            )

    farmer_msg = ChatMessage(
        session_id=data.session_id,
        role="user",
        content=data.message,
        message_type=data.message_type
    )
    db.add(farmer_msg)
    db.commit()

    all_messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == data.session_id
    ).order_by(ChatMessage.created_at).all()

    message_history = [
        {"role": msg.role, "content": msg.content}
        for msg in all_messages
    ]

    ai_response = await chat_with_gemini(
        messages=message_history,
        farmer_district=farmer.district,
        harvest_context=harvest_context,
        image_base64=data.image_base64
    )

    ai_msg = ChatMessage(
        session_id=data.session_id,
        role="model",
        content=ai_response["response"],
        message_type="text"
    )
    db.add(ai_msg)

    anomaly_info = ai_response.get("anomaly_detected")
    if anomaly_info and harvest:
        session.anomaly_detected = anomaly_info.get("type")
        session.anomaly_confidence = anomaly_info.get("confidence")

        anomaly = HarvestAnomaly(
            harvest_id=harvest.id,
            farmer_id=session.farmer_id,
            anomaly_type=anomaly_info.get("type", "unknown"),
            description=anomaly_info.get(
                "description", data.message
            ),
            recovery_plan=ai_response["response"]
        )
        db.add(anomaly)

        if anomaly_info.get("confidence") == "high":
            harvest.health_status = "warning"
            db.add(harvest)

    db.commit()

    return {
        "response": ai_response["response"],
        "anomaly_detected": anomaly_info,
        "linked_harvest": {
            "harvest_id": harvest.id,
            "crop_name": harvest.crop_name,
            "field_name": harvest.field_name
        } if harvest else None,
        "session_id": data.session_id
    }

@router.get("/history/{session_id}")
def get_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()

    return {
        "session_id": session_id,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "type": msg.message_type,
                "time": msg.created_at
            }
            for msg in messages
        ]
    }

@router.get("/sessions/{farmer_id}")
def get_farmer_sessions(
    farmer_id: int,
    db: Session = Depends(get_db)
):
    sessions = db.query(ChatSession).filter(
        ChatSession.farmer_id == farmer_id
    ).order_by(ChatSession.created_at.desc()).all()

    return {
        "farmer_id": farmer_id,
        "total_sessions": len(sessions),
        "sessions": [
            {
                "session_id": s.session_id,
                "harvest_id": s.harvest_id,
                "status": s.status,
                "anomaly_detected": s.anomaly_detected,
                "anomaly_confidence": s.anomaly_confidence,
                "created_at": s.created_at
            }
            for s in sessions
        ]
    }
