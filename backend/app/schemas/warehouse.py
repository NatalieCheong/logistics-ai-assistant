# backend/app/schemas/warehouse.py
"""
Pydantic schemas for Warehouse endpoints
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class WarehouseBase(BaseModel):
    """Base warehouse schema"""
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=10)
    address: str
    city: str
    state: str
    zip_code: str
    country: str


class WarehouseCreate(WarehouseBase):
    """Schema for creating a warehouse"""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    capacity_sqm: int = Field(..., gt=0)
    manager_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class WarehouseUpdate(BaseModel):
    """Schema for updating a warehouse"""
    name: Optional[str] = None
    manager_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    current_utilization: Optional[int] = None


class WarehouseResponse(WarehouseBase):
    """Schema for warehouse response"""
    id: int
    latitude: Optional[float]
    longitude: Optional[float]
    capacity_sqm: int
    current_utilization: int
    utilization_percentage: float
    manager_name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    
    class Config:
        from_attributes = True
