# backend/app/routers/drivers.py
"""
Driver endpoints
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.driver import Driver
from app.schemas.driver import DriverResponse


router = APIRouter()


@router.get("/", response_model=List[DriverResponse], status_code=status.HTTP_200_OK)
def list_drivers(db: Session = Depends(get_db)):
    """Return all drivers."""
    return db.query(Driver).all()


