from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from ..database import Base

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False, unique=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Relationships
    organizations = relationship("Organization", back_populates="building")