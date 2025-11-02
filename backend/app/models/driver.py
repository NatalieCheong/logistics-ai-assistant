# backend/app/models/driver.py
"""
Driver database model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Driver(Base):
    """
    Driver model for delivery personnel
    """
    __tablename__ = "drivers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Personal information
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=False)
    
    # License information
    license_number = Column(String, unique=True, nullable=False)
    license_expiry = Column(DateTime, nullable=False)
    
    # Current status
    is_active = Column(Boolean, default=True)
    current_location = Column(String, nullable=True)
    
    # Vehicle information
    vehicle_type = Column(String, nullable=True)
    vehicle_plate = Column(String, nullable=True)
    vehicle_capacity_kg = Column(Integer, nullable=True)
    
    # Timestamps
    hired_date = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    shipments = relationship("Shipment", back_populates="driver")
    
    def __repr__(self):
        return f"<Driver {self.name} - {self.license_number}>"
