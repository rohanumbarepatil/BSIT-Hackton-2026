from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import datetime

from db.database import get_db
from db.models import EwasteAsset, EwasteRecycler, EwasteAuditTrail

router = APIRouter(prefix="/api/v1/ewaste", tags=["ewaste"])

# Models
class AssetResponse(BaseModel):
    id: str
    asset_id: str
    asset_name: str
    asset_type: str
    department: str
    serial_number: str
    status: str
    created_at: datetime.datetime

class TransitionRequest(BaseModel):
    new_status: str
    notes: Optional[str] = None
    
    # Optional fields based on status
    recycler_id: Optional[str] = None
    received_by: Optional[str] = None
    certificate_reference: Optional[str] = None

class AuditTrailResponse(BaseModel):
    previous_status: str
    new_status: str
    notes: Optional[str]
    timestamp: datetime.datetime

class DashboardResponse(BaseModel):
    total_assets: int
    in_use: int
    decommissioned: int
    handed_over: int
    recycled: int

VALID_TRANSITIONS = {
    "REGISTERED": ["IN_USE"],
    "IN_USE": ["DECOMMISSIONED"],
    "DECOMMISSIONED": ["HANDED_OVER"],
    "HANDED_OVER": ["RECYCLED"],
    "RECYCLED": []
}

from api.routers.auth import require_role
from db.models import User

@router.get("/assets", response_model=List[AssetResponse])
def get_assets(db: Session = Depends(get_db), current_user: User = Depends(require_role("staff", "admin", "recycler"))):
    assets = db.query(EwasteAsset).all()
    return assets

@router.get("/assets/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_role("staff", "admin", "recycler"))):
    asset = db.query(EwasteAsset).filter(EwasteAsset.asset_id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.post("/assets/{asset_id}/transition")
def transition_asset(asset_id: str, req: TransitionRequest, db: Session = Depends(get_db), current_user: User = Depends(require_role("staff", "admin", "recycler"))):
    asset = db.query(EwasteAsset).filter(EwasteAsset.asset_id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    current_status = asset.status
    if req.new_status not in VALID_TRANSITIONS.get(current_status, []):
        raise HTTPException(status_code=400, detail=f"Invalid transition from {current_status} to {req.new_status}")
        
    # Apply specific status rules
    if req.new_status == "HANDED_OVER":
        if not req.recycler_id or not req.received_by:
            raise HTTPException(status_code=400, detail="HANDED_OVER requires recycler_id and received_by")
        asset.recycler_id = req.recycler_id
        asset.received_by = req.received_by
        asset.handover_date = datetime.datetime.utcnow()
        
    elif req.new_status == "RECYCLED":
        if not req.recycler_id or not req.certificate_reference:
            raise HTTPException(status_code=400, detail="RECYCLED requires recycler_id and certificate_reference")
        asset.certificate_reference = req.certificate_reference
        asset.recycled_at = datetime.datetime.utcnow()
        asset.recycler_id = req.recycler_id

    # Update status
    asset.status = req.new_status
    
    # Audit trail
    audit = EwasteAuditTrail(
        asset_internal_id=asset.id,
        previous_status=current_status,
        new_status=req.new_status,
        notes=req.notes
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Status updated successfully", "new_status": asset.status}

@router.get("/assets/{asset_id}/audit", response_model=List[AuditTrailResponse])
def get_asset_audit(asset_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_role("staff", "admin", "recycler"))):
    asset = db.query(EwasteAsset).filter(EwasteAsset.asset_id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    audits = db.query(EwasteAuditTrail).filter(EwasteAuditTrail.asset_internal_id == asset.id).order_by(EwasteAuditTrail.timestamp.asc()).all()
    return audits

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(require_role("staff", "admin"))):
    assets = db.query(EwasteAsset).all()
    
    in_use = sum(1 for a in assets if a.status == "IN_USE")
    decommissioned = sum(1 for a in assets if a.status == "DECOMMISSIONED")
    handed_over = sum(1 for a in assets if a.status == "HANDED_OVER")
    recycled = sum(1 for a in assets if a.status == "RECYCLED")
    
    return DashboardResponse(
        total_assets=len(assets),
        in_use=in_use,
        decommissioned=decommissioned,
        handed_over=handed_over,
        recycled=recycled
    )
