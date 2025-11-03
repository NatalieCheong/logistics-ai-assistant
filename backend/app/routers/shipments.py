# backend/app/routers/shipments.py
"""
Shipment management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.shipment import Shipment, ShipmentStatus
from app.models.user import User
from app.schemas.shipment import (
    ShipmentCreate,
    ShipmentUpdate,
    ShipmentResponse,
    ShipmentListResponse
)
from app.utils.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=ShipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_shipment(
    shipment: ShipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new shipment
    
    - **tracking_number**: Unique alphanumeric tracking number
    - **origin**: Starting location
    - **destination**: Delivery location
    - **weight_kg**: Package weight in kilograms
    - **warehouse_id**: Optional warehouse for pickup
    """
    # Check if tracking number already exists
    existing = db.query(Shipment).filter(
        Shipment.tracking_number == shipment.tracking_number.upper()
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tracking number {shipment.tracking_number} already exists"
        )
    
    # Create new shipment
    shipment_data = shipment.dict()
    shipment_data['tracking_number'] = shipment_data['tracking_number'].upper()
    db_shipment = Shipment(
        **shipment_data,
        customer_id=current_user.id
    )
    
    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)
    
    return db_shipment


@router.get("/", response_model=ShipmentListResponse)
async def list_shipments(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    status: Optional[ShipmentStatus] = Query(None, description="Filter by status"),
    origin: Optional[str] = Query(None, description="Filter by origin"),
    destination: Optional[str] = Query(None, description="Filter by destination"),
    tracking_number: Optional[str] = Query(None, description="Search by tracking number"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List shipments with pagination and filtering
    
    Supports:
    - Pagination (skip/limit)
    - Status filtering
    - Origin/destination filtering
    - Tracking number search
    """
    # Base query
    query = db.query(Shipment)
    
    # Apply filters
    if status:
        query = query.filter(Shipment.status == status)
    
    if origin:
        query = query.filter(Shipment.origin.ilike(f"%{origin}%"))
    
    if destination:
        query = query.filter(Shipment.destination.ilike(f"%{destination}%"))
    
    if tracking_number:
        query = query.filter(Shipment.tracking_number.ilike(f"%{tracking_number}%"))
    
    # Non-admin users only see their own shipments
    if current_user.role.value not in ["admin", "manager"]:
        query = query.filter(Shipment.customer_id == current_user.id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    shipments = query.offset(skip).limit(limit).all()
    
    # Calculate pages
    pages = (total + limit - 1) // limit if total > 0 else 0
    current_page = (skip // limit) + 1 if limit > 0 else 1
    
    return {
        "items": shipments,
        "total": total,
        "page": current_page,
        "size": limit,
        "pages": pages
    }


@router.get("/{shipment_id}", response_model=ShipmentResponse)
async def get_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get shipment by ID
    
    Returns detailed information about a specific shipment
    """
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with ID {shipment_id} not found"
        )
    
    # Check authorization
    if current_user.role.value not in ["admin", "manager"] and shipment.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this shipment"
        )
    
    return shipment


@router.get("/tracking/{tracking_number}", response_model=ShipmentResponse)
async def get_shipment_by_tracking(
    tracking_number: str,
    db: Session = Depends(get_db)
):
    """
    Get shipment by tracking number
    
    Public endpoint - no authentication required for tracking
    """
    shipment = db.query(Shipment).filter(
        Shipment.tracking_number == tracking_number.upper()
    ).first()
    
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with tracking number {tracking_number} not found"
        )
    
    return shipment


@router.patch("/{shipment_id}", response_model=ShipmentResponse)
async def update_shipment(
    shipment_id: int,
    shipment_update: ShipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update shipment information
    
    Allows updating:
    - Status
    - Current location
    - Driver assignment
    - Delivery estimates
    
    Requires admin/manager role
    """
    # Check authorization
    if current_user.role.value not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update shipments"
        )
    
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with ID {shipment_id} not found"
        )
    
    # Update fields
    update_data = shipment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(shipment, field, value)
    
    # If status changed to delivered, record actual delivery time
    if shipment_update.status == ShipmentStatus.DELIVERED and not shipment.actual_delivery:
        shipment.actual_delivery = datetime.utcnow()
    
    db.commit()
    db.refresh(shipment)
    
    return shipment


@router.delete("/{shipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a shipment
    
    Requires admin role
    Soft delete recommended in production
    """
    # Check authorization
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete shipments"
        )
    
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with ID {shipment_id} not found"
        )
    
    db.delete(shipment)
    db.commit()
    
    return {"message": "Shipment deleted successfully"}


@router.get("/statistics/overview")
async def get_shipment_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get shipment statistics overview
    
    Returns counts by status, recent activity, etc.
    """
    # Query based on user role
    query = db.query(Shipment)
    if current_user.role.value not in ["admin", "manager"]:
        query = query.filter(Shipment.customer_id == current_user.id)
    
    # Count by status
    total = query.count()
    pending = query.filter(Shipment.status == ShipmentStatus.PENDING).count()
    in_transit = query.filter(Shipment.status == ShipmentStatus.IN_TRANSIT).count()
    delivered = query.filter(Shipment.status == ShipmentStatus.DELIVERED).count()
    delayed = query.filter(Shipment.status == ShipmentStatus.DELAYED).count()
    
    # Recent shipments (last 7 days)
    from datetime import timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent = query.filter(Shipment.created_at >= week_ago).count()
    
    return {
        "total_shipments": total,
        "by_status": {
            "pending": pending,
            "in_transit": in_transit,
            "delivered": delivered,
            "delayed": delayed
        },
        "recent_shipments_7days": recent
    }
