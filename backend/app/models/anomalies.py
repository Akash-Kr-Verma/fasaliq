from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    anomaly_type = Column(String, nullable=False) # e.g., "crop_loss", "pest_attack"
    detected_crop = Column(String, nullable=True) # AI identified crop
    reason = Column(String, nullable=True)       # AI identified reason
    description = Column(Text, nullable=False)
    recovery_plan = Column(Text, nullable=True)
    reported_at = Column(DateTime(timezone=True), server_default=func.now())

    farmer = relationship("User", backref="anomalies")
    crop = relationship("Crop", backref="anomalies")