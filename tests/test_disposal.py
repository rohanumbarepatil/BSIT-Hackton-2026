import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

def test_disposal_flow():
    with TestClient(app) as client:
        # 1. Start Disposal Session (Valid High Confidence)
        start_payload = {
            "user_id": "test_user_1",
            "classification": {
                "class_name": "plastic",
                "category_group": "Dry Recyclable",
                "confidence": 0.85
            },
            "image_hash": "abc123hash"
        }
        
        response = client.post("/api/v1/disposal/start", json=start_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["points_available"] == 5
        assert data["verification_required"] is True
        session_id = data["session_id"]
        
        # 2. Verify Session
        verify_resp = client.post(f"/api/v1/disposal/{session_id}/verify")
        assert verify_resp.status_code == 200
        v_data = verify_resp.json()
        assert v_data["earned_this_session"] == 5
        assert v_data["transaction_id"] is not None
        
        # 3. Duplicate Verify (Should Fail)
        dup_resp = client.post(f"/api/v1/disposal/{session_id}/verify")
        assert dup_resp.status_code == 400
        assert "already" in dup_resp.json()["detail"].lower()
        
        # 4. Check Balance
        bal_resp = client.get("/api/v1/users/test_user_1/credits")
        assert bal_resp.status_code == 200
        assert bal_resp.json()["total_credits"] >= 5
        
        # 5. Check History
        hist_resp = client.get("/api/v1/users/test_user_1/credit-history")
        assert hist_resp.status_code == 200
        history = hist_resp.json()["history"]
        assert len(history) > 0
        assert history[0]["points"] == 5
        
def test_low_confidence_disposal():
    with TestClient(app) as client:
        start_payload = {
            "user_id": "test_user_1",
            "classification": {
                "class_name": "plastic",
                "category_group": "Dry Recyclable",
                "confidence": 0.55 # Below 0.65 threshold
            }
        }
        
        response = client.post("/api/v1/disposal/start", json=start_payload)
        assert response.status_code == 200
        assert response.json()["points_available"] == 0
        
        # Try to verify anyway (backend logic should catch it)
        session_id = response.json()["session_id"]
        verify_resp = client.post(f"/api/v1/disposal/{session_id}/verify")
        assert verify_resp.status_code == 400
        assert "low-confidence" in verify_resp.json()["detail"].lower()

def test_mixed_waste_disposal():
    with TestClient(app) as client:
        start_payload = {
            "user_id": "test_user_1",
            "classification": {
                "class_name": "mixed",
                "category_group": "Mixed/Uncertain",
                "confidence": 0.99
            }
        }
        
        response = client.post("/api/v1/disposal/start", json=start_payload)
        assert response.status_code == 200
        assert response.json()["points_available"] == 0
        
        session_id = response.json()["session_id"]
        verify_resp = client.post(f"/api/v1/disposal/{session_id}/verify")
        assert verify_resp.status_code == 400
        assert "mixed waste" in verify_resp.json()["detail"].lower()

def test_invalid_user_start():
    with TestClient(app) as client:
        start_payload = {
            "user_id": "invalid_user_999",
            "classification": {
                "class_name": "plastic",
                "category_group": "Dry Recyclable",
                "confidence": 0.99
            }
        }
        
        response = client.post("/api/v1/disposal/start", json=start_payload)
        assert response.status_code == 404

def test_invalid_session_verify():
    with TestClient(app) as client:
        response = client.post("/api/v1/disposal/invalid_sess_123/verify")
        assert response.status_code == 404
