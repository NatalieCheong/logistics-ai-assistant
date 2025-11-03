# backend/app/routers/warehouses.py
"""
Warehouse endpoints
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseResponse


router = APIRouter()


@router.get("/", response_model=List[WarehouseResponse], status_code=status.HTTP_200_OK)
def list_warehouses(db: Session = Depends(get_db)):
    """Return all warehouses."""
    return db.query(Warehouse).all()


