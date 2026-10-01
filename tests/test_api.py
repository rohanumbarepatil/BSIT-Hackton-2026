import pytest
from fastapi.testclient import TestClient
from PIL import Image
import io
import os
import sys

# Add root directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

client = TestClient(app)

def create_test_image(format="jpeg", size=(100, 100), corrupt=False):
    if corrupt:
        return b"this is not an image"
    
    img = Image.new('RGB', size, color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format=format)
    return img_byte_arr.getvalue()

def test_model_info():
    with TestClient(app) as client:
        response = client.get("/api/v1/model/info")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "prototype"
        assert "ewaste" in data["trained_classes"]
        assert "battery" in data["e_waste_coverage"].lower()

def test_valid_image_classification():
    with TestClient(app) as client:
        img_bytes = create_test_image()
        response = client.post(
            "/api/v1/classify",
            files={"image": ("test.jpg", img_bytes, "image/jpeg")}
        )
        assert response.status_code == 200
        data = response.json()
        assert "class_name" in data
        assert "confidence" in data
        assert "category_group" in data
        assert "guidance" in data
        assert isinstance(data["is_low_confidence"], bool)

def test_unsupported_format():
    with TestClient(app) as client:
        img_bytes = create_test_image(format="gif")
        response = client.post(
            "/api/v1/classify",
            files={"image": ("test.gif", img_bytes, "image/gif")}
        )
        assert response.status_code == 400
        assert "Unsupported image format" in response.json()["detail"]

def test_invalid_corrupted_image():
    with TestClient(app) as client:
        img_bytes = create_test_image(corrupt=True)
        response = client.post(
            "/api/v1/classify",
            files={"image": ("test.jpg", img_bytes, "image/jpeg")}
        )
        assert response.status_code == 400
        assert "Invalid image format" in response.json()["detail"]

def test_oversized_image():
    with TestClient(app) as client:
        # Create 6MB payload
        img_bytes = b"0" * (6 * 1024 * 1024)
        response = client.post(
            "/api/v1/classify",
            files={"image": ("test.jpg", img_bytes, "image/jpeg")}
        )
        assert response.status_code == 413
        assert "Image too large" in response.json()["detail"]

def test_malformed_request():
    with TestClient(app) as client:
        response = client.post("/api/v1/classify")
        assert response.status_code == 422
