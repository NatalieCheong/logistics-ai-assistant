# backend/app/models/shipment.py
"""
Shipment database model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base

class ShipmentStatus(str, enum.Enum):
   """Shipment status enumeration"""
   PENDING = "pending"
   PICKED_UP = "picked_up"
   IN_TRANSIT = "in_transit"
   OUT_FOR_DELIVERY = "out_for_delivery"
   DELIVERED = "delivered"
   DELAYED = "delayed"
   CANCELLED = "cancelled"

class Shipment(Base):
   """
   Shipment model representing a package/cargo shipment
   """
   __tablename__ = "shipments"
  
   # Primary key
   id = Column(Integer, primary_key=True, index=True)
 
   # Tracking information
   tracking_number = Column(String, unique=True, index=True, nullable=False)

   # Location information
   origin = Column(String, nullable=False)
   destination = Column(String, nullable=False)
   current_location = Column(String, nullable=True)

   # Package details
   weight_kg = Column(Float, nullable=False)
   dimensions = Column(String, nullable=True)  # Format: "LxWxH cm"
   description = Column(String, nullable=True)

   # Status
   status = Column(
       Enum(ShipmentStatus),
       default=ShipmentStatus.PENDING,
       nullable=False,
       index=True
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    stimated_delivery = Column(DateTime, nullable=True)
    actual_delivery = Column(DateTime, nullable=True)

    # Foreign keys
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    warehouse = relationship("Warehouse", back_populates="shipments")
    driver = relationship("Driver", back_populates="shipments")
    customer = relationship("User", back_populates="shipments")

    def __repr__(self):
        return f"<Shipment {self.tracking_number} - {self.status}>"
