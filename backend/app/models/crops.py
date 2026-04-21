from sqlalchemy import Column, Integer, String, Float, Boolean
from app.core.database import Base

class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    season = Column(String, nullable=False)
    water_need = Column(String, nullable=False)
    soil_fit = Column(String, nullable=False)
    msp = Column(Float, default=0.0)
    avg_yield = Column(Float, nullable=False)
    has_msp = Column(Boolean, default=False)