from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import sys
import os

# Add root directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.inference.classifier import WasteClassifier
from api.routers import disposal, users, ewaste, smartbins, auth

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="WasteSense AI API",
    description="Inference API for the CIRCUIT Waste Management Project",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(disposal.router)
app.include_router(users.router)
app.include_router(ewaste.router)
app.include_router(smartbins.router)

# Global classifier instance
classifier = None

@app.on_event("startup")
async def load_model():
    global classifier
    try:
        classifier = WasteClassifier(config_path="ml/config/model_config.json")
    except Exception as e:
        print(f"Failed to load model: {e}")
        # Let it fail on predict so we can test failure states if needed
        classifier = None

class PredictionResponse(BaseModel):
    class_name: str
    confidence: float
    category_group: str
    guidance: str
    is_low_confidence: bool

class ModelInfoResponse(BaseModel):
    model_name: str
    model_version: str
    status: str
    trained_classes: list[str]
    dataset_version: str
    e_waste_coverage: str

from api.routers.auth import require_role
from db.models import User
from fastapi import Depends

@app.post("/api/v1/classify", response_model=PredictionResponse)
async def classify_image(image: UploadFile = File(...), current_user: User = Depends(require_role("student", "staff", "admin"))):
    """
    Classifies a single waste item.
    Note: Do not submit images with multiple distinct waste objects.
    """
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model failed to load.")
        
    # Check format
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Unsupported image format. Use JPEG or PNG.")
        
    try:
        # Read contents
        contents = await image.read()
        
        # Check size (e.g. 5MB max)
        if len(contents) > 5 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Image too large. Maximum size is 5MB.")
            
        prediction = classifier.predict(contents)
        return PredictionResponse(**prediction)
        
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error during classification.")

@app.get("/api/v1/model/info", response_model=ModelInfoResponse)
async def get_model_info():
    """
    Returns metadata about the currently active model.
    """
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model failed to load.")
        
    cfg = classifier.config
    return ModelInfoResponse(
        model_name=cfg["name"],
        model_version=cfg["version"],
        status=cfg["status"],
        trained_classes=cfg["trained_classes"],
        dataset_version=cfg["dataset_version"],
        e_waste_coverage=cfg["e_waste_coverage"]
    )
