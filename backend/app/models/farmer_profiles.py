from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    field_size = Column(Float, nullable=False)
    soil_type = Column(String, nullable=False)
    irrigation = Column(String, nullable=False)
    last_crop = Column(String, nullable=True)
    economic_tier = Column(String, default="small")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="farmer_profile")