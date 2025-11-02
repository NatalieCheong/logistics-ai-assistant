#backend/app/models/warehouse.py
"""
Warehouse database model
"""

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from app.database import Base

class Warehouse(Base):
    """
    Warehouse model for storage facilities
    """
    __tablename__ = "warehouses"
  
    id = Column(Integer, primary_key=True, index=True)

    # Warehouse information
    name = Column(String, unique=True, nullable=False, index=True)
    code = Column(String(10), unique=True, nullable=False)
   
    # Location
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    
    # Coordinates for routing
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
  
    # Capacity
    capacity_sqm = Column(Integer, nullable=False)
    current_utilization = Column(Integer, default=0)
    
    # Contact
    manager_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    # Relationships
    shipments = relationship("Shipment", back_populates="warehouse")
    
    def __repr__(self):
        return f"<Warehouse {self.name} - {self.city}>"
    
    @property
    def utilization_percentage(self) -> float:
        """Calculate warehouse utilization percentage"""
        if self.capacity_sqm == 0:
           return 0.0
        return (self.current_utilization / self.capacity_sqm) * 100
