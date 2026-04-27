from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Harvest(Base):
    __tablename__ = "harvests"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    field_name = Column(String, nullable=False)
    crop_name = Column(String, nullable=False)
    season = Column(String, nullable=False)
    field_size = Column(Float, nullable=False)
    soil_type = Column(String, nullable=True)
    irrigation = Column(String, nullable=True)
    sowing_date = Column(DateTime(timezone=True), server_default=func.now())
    expected_harvest_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="active")
    health_status = Column(String, default="good")
    notes = Column(Text, nullable=True)
    actual_yield = Column(Float, nullable=True)
    income_earned = Column(Float, nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    farmer = relationship("User", backref="harvests")
    anomalies = relationship("HarvestAnomaly", backref="harvest")

class HarvestAnomaly(Base):
    __tablename__ = "harvest_anomalies"

    id = Column(Integer, primary_key=True, index=True)
    harvest_id = Column(Integer, ForeignKey("harvests.id"), nullable=False)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    anomaly_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    recovery_plan = Column(Text, nullable=True)
    status = Column(String, default="active")
    reported_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
