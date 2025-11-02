# backend/app/schemas/shipment.py
"""
Pydantic schemas for Shipment endpoints
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from app.models.shipment import ShipmentStatus


class ShipmentBase(BaseModel):
    """Base shipment schema"""
    origin: str = Field(..., min_length=2, max_length=100, description="Origin location")
    destination: str = Field(..., min_length=2, max_length=100, description="Destination location")
    weight_kg: float = Field(..., gt=0, lt=10000, description="Weight in kilograms")
    dimensions: Optional[str] = Field(None, description="Dimensions in LxWxH cm format")
    description: Optional[str] = Field(None, max_length=500)


class ShipmentCreate(ShipmentBase):
    """Schema for creating a new shipment"""
    tracking_number: str = Field(..., min_length=10, max_length=20, description="Unique tracking number")
    warehouse_id: Optional[int] = Field(None, description="Warehouse ID for pickup")
    estimated_delivery: Optional[datetime] = None
    
    @validator('tracking_number')
    def validate_tracking_number(cls, v):
        """Validate tracking number format"""
        if not v.isalnum():
            raise ValueError('Tracking number must be alphanumeric')
        return v.upper()


class ShipmentUpdate(BaseModel):
    """Schema for updating a shipment"""
    status: Optional[ShipmentStatus] = None
    current_location: Optional[str] = None
    driver_id: Optional[int] = None
    estimated_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None


class ShipmentResponse(ShipmentBase):
    """Schema for shipment response"""
    id: int
    tracking_number: str
    status: ShipmentStatus
    current_location: Optional[str]
    created_at: datetime
    updated_at: datetime
    estimated_delivery: Optional[datetime]
    actual_delivery: Optional[datetime]
    warehouse_id: Optional[int]
    driver_id: Optional[int]
    customer_id: int
    
    class Config:
        from_attributes = True


class ShipmentListResponse(BaseModel):
    """Schema for paginated shipment list"""
    items: list[ShipmentResponse]
    total: int
    page: int
    size: int
    pages: int
