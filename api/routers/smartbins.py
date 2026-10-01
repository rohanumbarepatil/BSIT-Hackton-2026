from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import datetime

from db.database import get_db
from db.models import SmartBin, TelemetryReading, CollectionEvent

router = APIRouter(prefix="/api/v1/bins", tags=["smart_bins"])

class TelemetryRequest(BaseModel):
    fill_percent: float

class BinResponse(BaseModel):
    id: str
    bin_id: str
    name: str
    location: str
    waste_type: str
    capacity_percent: float
    current_fill_percent: float
    status: str
    last_updated: datetime.datetime

class PredictionResponse(BaseModel):
    bin_id: str
    prediction_status: str
    current_fill_percent: float
    fill_rate_per_hour: Optional[float] = None
    hours_to_full: Optional[float] = None

class AlertResponse(BaseModel):
    bin_id: str
    level: str
    message: str

class DashboardResponse(BaseModel):
    total_bins: int
    normal: int
    warning: int
    critical: int
    overflow: int

def get_status_from_fill(fill: float) -> str:
    if fill >= 100:
        return "OVERFLOW"
    elif fill >= 85:
        return "CRITICAL"
    elif fill >= 70:
        return "WARNING"
    return "NORMAL"

def calculate_prediction(db: Session, bin_record: SmartBin) -> PredictionResponse:
    readings = db.query(TelemetryReading).filter(
        TelemetryReading.bin_internal_id == bin_record.id
    ).order_by(TelemetryReading.timestamp.desc()).limit(2).all()
    
    if len(readings) < 2:
        return PredictionResponse(
            bin_id=bin_record.bin_id,
            prediction_status="INSUFFICIENT_HISTORY",
            current_fill_percent=bin_record.current_fill_percent
        )
        
    latest = readings[0]
    previous = readings[1]
    
    fill_diff = latest.fill_percent - previous.fill_percent
    time_diff_hours = (latest.timestamp - previous.timestamp).total_seconds() / 3600.0
    
    if time_diff_hours <= 0 or fill_diff <= 0:
        return PredictionResponse(
            bin_id=bin_record.bin_id,
            prediction_status="INSUFFICIENT_HISTORY",
            current_fill_percent=bin_record.current_fill_percent
        )
        
    fill_rate = fill_diff / time_diff_hours
    hours_to_full = (100.0 - bin_record.current_fill_percent) / fill_rate if fill_rate > 0 else 999
    
    status = "PREDICTED_FULL" if hours_to_full < 12 else "STABLE"
    if bin_record.current_fill_percent >= 100:
        status = "ALREADY_FULL"
        hours_to_full = 0
        
    return PredictionResponse(
        bin_id=bin_record.bin_id,
        prediction_status=status,
        current_fill_percent=bin_record.current_fill_percent,
        fill_rate_per_hour=round(fill_rate, 2),
        hours_to_full=round(hours_to_full, 2)
    )

from api.routers.auth import require_role
from db.models import User

@router.get("", response_model=List[BinResponse])
def get_bins(db: Session = Depends(get_db), current_user: User = Depends(require_role("staff", "admin"))):
    return db.query(SmartBin).all()

@router.get("/alerts", response_model=List[AlertResponse])
def get_alerts(db: Session = Depends(get_db), current_user: User = Depends(require_role("staff", "admin"))):
    bins = db.query(SmartBin).all()
    alerts = []
    
    for b in bins:
        if b.status == "OVERFLOW":
            alerts.append(AlertResponse(bin_id=b.bin_id, level="OVERFLOW", message=f"{b.bin_id} is overflowing!"))
        elif b.status == "CRITICAL":
            alerts.append(AlertResponse(bin_id=b.bin_id, level="CRITICAL", message=f"{b.bin_id} is critically full."))
        elif b.status == "WARNING":
            # Check prediction
            pred = calculate_prediction(db, b)
            if pred.prediction_status == "PREDICTED_FULL" and pred.hours_to_full is not None:
                alerts.append(AlertResponse(bin_id=b.bin_id, level="PREDICTED_FULL", message=f"{b.bin_id} predicted to reach capacity in {pred.hours_to_full} hours."))
            else:
                alerts.append(AlertResponse(bin_id=b.bin_id, level="WARNING", message=f"{b.bin_id} is filling up."))
                
    return alerts

@router.get("/{bin_id}", response_model=BinResponse)
def get_bin(bin_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_role("staff", "admin"))):
    b = db.query(SmartBin).filter(SmartBin.bin_id == bin_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Bin not found")
    return b

@router.post("/{bin_id}/telemetry")
def update_telemetry(bin_id: str, req: TelemetryRequest, db: Session = Depends(get_db)):
    b = db.query(SmartBin).filter(SmartBin.bin_id == bin_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Bin not found")
        
    b.current_fill_percent = req.fill_percent
    b.status = get_status_from_fill(req.fill_percent)
    b.last_updated = datetime.datetime.utcnow()
    
    reading = TelemetryReading(
        bin_internal_id=b.id,
        fill_percent=req.fill_percent
    )
    
    db.add(reading)
    db.commit()
    
    return {"message": "Telemetry updated", "status": b.status}

@router.get("/{bin_id}/prediction", response_model=PredictionResponse)
def get_prediction(bin_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_role("staff", "admin"))):
    b = db.query(SmartBin).filter(SmartBin.bin_id == bin_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Bin not found")
        
    return calculate_prediction(db, b)

@router.post("/{bin_id}/collect")
def collect_bin(bin_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_role("staff", "admin"))):
    b = db.query(SmartBin).filter(SmartBin.bin_id == bin_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Bin not found")
        
    b.current_fill_percent = 0.0
    b.status = "NORMAL"
    b.last_updated = datetime.datetime.utcnow()
    
    event = CollectionEvent(bin_internal_id=b.id)
    db.add(event)
    
    # Also add a 0% telemetry reading to reset predictive rate
    reading = TelemetryReading(bin_internal_id=b.id, fill_percent=0.0)
    db.add(reading)
    
    db.commit()
    return {"message": "Bin collected and reset"}

@router.get("/dashboard/stats", response_model=DashboardResponse)
def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(require_role("staff", "admin"))):
    bins = db.query(SmartBin).all()
    
    return DashboardResponse(
        total_bins=len(bins),
        normal=sum(1 for b in bins if b.status == "NORMAL"),
        warning=sum(1 for b in bins if b.status == "WARNING"),
        critical=sum(1 for b in bins if b.status == "CRITICAL"),
        overflow=sum(1 for b in bins if b.status == "OVERFLOW")
    )
