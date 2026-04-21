from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    district = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    date = Column(Date, server_default=func.current_date())
    source = Column(String, default="Agmarknet")

    crop = relationship("Crop", backref="market_prices")