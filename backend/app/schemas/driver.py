# backend/app/schemas/driver.py
"""
Pydantic schemas for Driver endpoints
"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


class DriverBase(BaseModel):
    """Base driver schema"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str


class DriverCreate(DriverBase):
    """Schema for creating a driver"""
    license_number: str = Field(..., min_length=5, max_length=20)
    license_expiry: datetime
    vehicle_type: Optional[str] = None
    vehicle_plate: Optional[str] = None
    vehicle_capacity_kg: Optional[int] = None


class DriverUpdate(BaseModel):
    """Schema for updating a driver"""
    name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    current_location: Optional[str] = None
    vehicle_type: Optional[str] = None
    vehicle_plate: Optional[str] = None


class DriverResponse(DriverBase):
    """Schema for driver response"""
    id: int
    license_number: str
    license_expiry: datetime
    is_active: bool
    current_location: Optional[str]
    vehicle_type: Optional[str]
    vehicle_plate: Optional[str]
    vehicle_capacity_kg: Optional[int]
    hired_date: datetime
    last_active: datetime
    
    class Config:
        from_attributes = True

