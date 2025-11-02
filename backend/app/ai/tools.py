# backend/app/ai/tools.py
"""
Custom tools for the LangChain agent
These tools allow the agent to interact with the logistics system
"""

from langchain.tools import tool
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@tool
def get_shipment_status(tracking_number: str) -> str:
    """
    Get the current status and location of a shipment by tracking number.
    
    Args:
        tracking_number: The unique tracking number of the shipment
        
    Returns:
        String with shipment status and current location
    """
    try:
        # In real implementation, this would query the database
        # For demo, returning mock data
        
        # Import here to avoid circular imports
        from app.database import SessionLocal
        from app.models.shipment import Shipment
        
        db = SessionLocal()
        shipment = db.query(Shipment).filter(
            Shipment.tracking_number == tracking_number.upper()
        ).first()
        db.close()
        
        if not shipment:
            return f"Shipment with tracking number {tracking_number} not found. Please verify the tracking number and try again."
        
        location = shipment.current_location or "Processing at origin"
        return f"Shipment {tracking_number}: Status is '{shipment.status.value}'. Current location: {location}. Origin: {shipment.origin}, Destination: {shipment.destination}."
        
    except Exception as e:
        logger.error(f"Error getting shipment status: {e}")
        return f"Unable to retrieve status for {tracking_number}. Please try again."


@tool
def calculate_shipping_cost(origin: str, destination: str, weight_kg: float) -> str:
    """
    Calculate the estimated shipping cost based on origin, destination, and package weight.
    
    Args:
        origin: Starting location (city, state or full address)
        destination: Delivery location (city, state or full address)
        weight_kg: Package weight in kilograms
        
    Returns:
        String with estimated shipping cost in USD
    """
    try:
        # Simplified cost calculation
        # Real implementation would use distance APIs and rate tables
        
        base_rate = 10.0  # Base shipping fee
        per_kg_rate = 2.5  # Cost per kg
        
        # Simple distance factor based on string comparison
        # In reality, would use geocoding and distance calculation
        distance_factor = 1.0
        if origin.lower() != destination.lower():
            distance_factor = 1.5
        
        total_cost = (base_rate + (weight_kg * per_kg_rate)) * distance_factor
        
        return f"Estimated shipping cost from {origin} to {destination} for {weight_kg}kg: ${total_cost:.2f} USD. This includes base rate, weight charges, and distance calculation."
        
    except Exception as e:
        logger.error(f"Error calculating shipping cost: {e}")
        return "Unable to calculate shipping cost. Please verify the input parameters."


@tool
def find_nearest_warehouse(location: str) -> str:
    """
    Find the nearest warehouse to a given location.
    
    Args:
        location: City, state, or address to search from
        
    Returns:
        String with nearest warehouse information
    """
    try:
        # In real implementation, would use geocoding and spatial queries
        from app.database import SessionLocal
        from app.models.warehouse import Warehouse
        
        db = SessionLocal()
        
        # Simple text matching for demo
        # Real implementation would use coordinates and distance calculation
        warehouses = db.query(Warehouse).filter(
            Warehouse.city.ilike(f"%{location}%")
        ).limit(3).all()
        
        db.close()
        
        if not warehouses:
            return f"No warehouses found near {location}. Please try a different location or contact support."
        
        result = f"Warehouses near {location}:\n"
        for wh in warehouses:
            result += f"- {wh.name} in {wh.city}, {wh.state}: {wh.utilization_percentage:.1f}% utilized, Contact: {wh.phone}\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error finding warehouse: {e}")
        return "Unable to find nearby warehouses. Please try again."


@tool
def estimate_delivery_time(tracking_number: str) -> str:
    """
    Estimate the delivery time for a shipment.
    
    Args:
        tracking_number: The shipment tracking number
        
    Returns:
        String with estimated delivery date and time
    """
    try:
        from app.database import SessionLocal
        from app.models.shipment import Shipment
        from datetime import datetime, timedelta
        
        db = SessionLocal()
        shipment = db.query(Shipment).filter(
            Shipment.tracking_number == tracking_number.upper()
        ).first()
        db.close()
        
        if not shipment:
            return f"Shipment {tracking_number} not found."
        
        if shipment.actual_delivery:
            return f"Shipment {tracking_number} was already delivered on {shipment.actual_delivery.strftime('%Y-%m-%d %H:%M')}."
        
        if shipment.estimated_delivery:
            est_date = shipment.estimated_delivery.strftime('%Y-%m-%d')
            days_remaining = (shipment.estimated_delivery - datetime.utcnow()).days
            return f"Shipment {tracking_number} is estimated to be delivered on {est_date} (approximately {days_remaining} days from now)."
        
        # Default estimate
        est_days = 3
        est_date = (datetime.utcnow() + timedelta(days=est_days)).strftime('%Y-%m-%d')
        return f"Shipment {tracking_number} is estimated to be delivered by {est_date} (approximately {est_days} business days)."
        
    except Exception as e:
        logger.error(f"Error estimating delivery: {e}")
        return "Unable to estimate delivery time. Please try again."


@tool
def search_shipments(status: Optional[str] = None, origin: Optional[str] = None, destination: Optional[str] = None) -> str:
    """
    Search for shipments based on criteria like status, origin, or destination.
    
    Args:
        status: Filter by shipment status (pending, in_transit, delivered, etc.)
        origin: Filter by origin location
        destination: Filter by destination location
        
    Returns:
        String with matching shipments
    """
    try:
        from app.database import SessionLocal
        from app.models.shipment import Shipment
        
        db = SessionLocal()
        query = db.query(Shipment)
        
        if status:
            query = query.filter(Shipment.status == status)
        if origin:
            query = query.filter(Shipment.origin.ilike(f"%{origin}%"))
        if destination:
            query = query.filter(Shipment.destination.ilike(f"%{destination}%"))
        
        shipments = query.limit(10).all()
        db.close()
        
        if not shipments:
            return "No shipments found matching the criteria."
        
        result = f"Found {len(shipments)} shipment(s):\n"
        for ship in shipments:
            result += f"- {ship.tracking_number}: {ship.status.value}, {ship.origin} → {ship.destination}\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error searching shipments: {e}")
        return "Unable to search shipments. Please try again."
