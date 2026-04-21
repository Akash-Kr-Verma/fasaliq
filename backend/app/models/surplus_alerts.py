from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class SurplusAlert(Base):
    __tablename__ = "surplus_alerts"

    id = Column(Integer, primary_key=True, index=True)
    district = Column(String, nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    farmer_count = Column(Integer, nullable=False)
    market_capacity = Column(Integer, nullable=False)
    ratio = Column(Float, nullable=False)
    severity = Column(String, nullable=False)
    alerted_at = Column(DateTime(timezone=True), server_default=func.now())

    crop = relationship("Crop", backref="surplus_alerts")
    