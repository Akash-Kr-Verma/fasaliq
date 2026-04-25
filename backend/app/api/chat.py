from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import uuid
from app.core.database import get_db
from app.models.chat_sessions import ChatSession, ChatMessage
from app.models.users import User
from app.models.anomalies import Anomaly
from app.models.crops import Crop
from app.services.gemini_service import chat_with_gemini

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class StartSessionRequest(BaseModel):
    farmer_id: int

class SendMessageRequest(BaseModel):
    session_id: str
    message: str
    image_base64: Optional[str] = None
    message_type: Optional[str] = "text"

class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: list

@router.post("/start")
def start_session(
    data: StartSessionRequest,
    db: Session = Depends(get_db)
):
    farmer = db.query(User).filter(
        User.id == data.farmer_id
    ).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    session_id = str(uuid.uuid4())

    session = ChatSession(
        farmer_id=data.farmer_id,
        session_id=session_id,
        status="active"
    )
    db.add(session)

    welcome_msg = ChatMessage(
        session_id=session_id,
        role="model",
        content=(
            "नमस्ते! मैं FasalIQ AI हूं। "
            "आपकी फसल में क्या समस्या है? "
            "मुझे बताएं, मैं आपकी मदद करूंगा। 🌾\n\n"
            "नमस्कार! मी FasalIQ AI आहे. "
            "तुमच्या पिकात काय समस्या आहे? "
            "मला सांगा, मी मदत करेन. 🌾"
        ),
        message_type="text"
    )
    db.add(welcome_msg)
    db.commit()

    return {
        "session_id": session_id,
        "farmer_id": data.farmer_id,
        "welcome_message": welcome_msg.content,
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
        raise HTTPException(status_code=404, detail="Session not found")

    farmer = db.query(User).filter(
        User.id == session.farmer_id
    ).first()

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
    if anomaly_info:
        session.anomaly_detected = anomaly_info.get("type")
        session.anomaly_confidence = anomaly_info.get("confidence")

        crop = db.query(Crop).first()
        if crop:
            anomaly = Anomaly(
                farmer_id=session.farmer_id,
                crop_id=crop.id,
                anomaly_type=anomaly_info.get("type", "unknown"),
                description=anomaly_info.get("description", data.message),
                recovery_plan=ai_response["response"]
            )
            db.add(anomaly)

    db.commit()

    return {
        "response": ai_response["response"],
        "anomaly_detected": anomaly_info,
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
                "status": s.status,
                "anomaly_detected": s.anomaly_detected,
                "anomaly_confidence": s.anomaly_confidence,
                "created_at": s.created_at
            }
            for s in sessions
        ]
    }
