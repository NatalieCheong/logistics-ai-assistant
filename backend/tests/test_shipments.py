import pytest
from fastapi import status
from app.models.shipment import Shipment


@pytest.fixture
def test_shipment(db, test_user):
    """Create a test shipment"""
    shipment = Shipment(
        tracking_number="TEST123456",
        origin="New York",
        destination="Los Angeles",
        weight_kg=25.5,
        customer_id=test_user.id
    )
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    return shipment


def test_create_shipment(client, auth_headers):
    """Test creating a new shipment"""
    response = client.post(
        "/api/shipments/",
        headers=auth_headers,
        json={
            "tracking_number": "SHIP789012",
            "origin": "Chicago",
            "destination": "Miami",
            "weight_kg": 15.0,
            "description": "Electronics"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["tracking_number"] == "SHIP789012"
    assert data["origin"] == "Chicago"
    assert data["status"] == "pending"


def test_create_duplicate_tracking(client, auth_headers, test_shipment):
    """Test creating shipment with duplicate tracking number"""
    response = client.post(
        "/api/shipments/",
        headers=auth_headers,
        json={
            "tracking_number": test_shipment.tracking_number,
            "origin": "Boston",
            "destination": "Seattle",
            "weight_kg": 20.0
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_list_shipments(client, auth_headers, test_shipment):
    """Test listing shipments"""
    response = client.get("/api/shipments/", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1


def test_get_shipment_by_id(client, auth_headers, test_shipment):
    """Test getting shipment by ID"""
    response = client.get(
        f"/api/shipments/{test_shipment.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_shipment.id
    assert data["tracking_number"] == test_shipment.tracking_number


def test_get_shipment_by_tracking(client, test_shipment):
    """Test public tracking endpoint"""
    response = client.get(
        f"/api/shipments/tracking/{test_shipment.tracking_number}"
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["tracking_number"] == test_shipment.tracking_number


def test_filter_shipments_by_status(client, auth_headers, test_shipment):
    """Test filtering shipments by status"""
    response = client.get(
        "/api/shipments/?status=pending",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(item["status"] == "pending" for item in data["items"])


def test_pagination(client, auth_headers, db, test_user):
    """Test shipment pagination"""
    # Create multiple shipments
    for i in range(15):
        shipment = Shipment(
            tracking_number=f"PAGE{i:06d}",
            origin="Test City",
            destination="Dest City",
            weight_kg=10.0,
            customer_id=test_user.id
        )
        db.add(shipment)
    db.commit()
    
    # Test first page
    response = client.get(
        "/api/shipments/?skip=0&limit=10",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 10
    assert data["total"] >= 15
