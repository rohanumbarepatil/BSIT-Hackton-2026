import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

def test_list_assets():
    with TestClient(app) as client:
        response = client.get("/api/v1/ewaste/assets")
        assert response.status_code == 200
        assert len(response.json()) >= 5 # 5 seeded assets

def test_get_asset():
    with TestClient(app) as client:
        response = client.get("/api/v1/ewaste/assets/LAB-PC-001")
        assert response.status_code == 200
        assert response.json()["asset_id"] == "LAB-PC-001"
        assert response.json()["status"] == "REGISTERED"

def test_valid_lifecycle_transition():
    with TestClient(app) as client:
        payload = {
            "new_status": "IN_USE",
            "notes": "Testing deployment"
        }
        response = client.post("/api/v1/ewaste/assets/LAB-PC-001/transition", json=payload)
        assert response.status_code == 200
        assert response.json()["new_status"] == "IN_USE"

def test_invalid_lifecycle_transition():
    with TestClient(app) as client:
        payload = {
            "new_status": "RECYCLED", # Cannot jump straight from IN_USE to RECYCLED
            "notes": "Testing invalid jump"
        }
        response = client.post("/api/v1/ewaste/assets/LAB-PC-001/transition", json=payload)
        assert response.status_code == 400
        assert "Invalid transition" in response.json()["detail"]

def test_audit_trail():
    with TestClient(app) as client:
        response = client.get("/api/v1/ewaste/assets/LAB-PRN-005/audit")
        assert response.status_code == 200
        audits = response.json()
        assert len(audits) >= 5 # We seeded 5 audit trails for this asset
        
def test_dashboard():
    with TestClient(app) as client:
        response = client.get("/api/v1/ewaste/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["total_assets"] >= 5
        assert data["recycled"] >= 1
