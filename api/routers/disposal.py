from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import hashlib

from db.database import get_db
from db.models import DisposalSession, User, GreenCreditRule
from services.reward_engine import RewardEngine, RewardError

router = APIRouter(prefix="/api/v1/disposal", tags=["disposal"])

class ClassificationResult(BaseModel):
    class_name: str
    category_group: str
    confidence: float

class DisposalStartRequest(BaseModel):
    user_id: str
    classification: ClassificationResult
    image_hash: str = "placeholder_hash" # In production, this would be computed from the uploaded bytes

class DisposalStartResponse(BaseModel):
    session_id: str
    recommended_disposal_type: str
    points_available: int
    verification_required: bool

class VerifyResponse(BaseModel):
    user_id: str
    total_credits: int
    earned_this_session: int
    transaction_id: str | None = None

from api.routers.auth import require_role

@router.post("/start", response_model=DisposalStartResponse)
def start_disposal(req: DisposalStartRequest, db: Session = Depends(get_db), current_user: User = Depends(require_role("student"))):
    # Validate User
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Create Session
    session = DisposalSession(
        user_id=req.user_id,
        predicted_class=req.classification.class_name,
        category_group=req.classification.category_group,
        confidence=req.classification.confidence,
        image_hash=req.image_hash
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Check points available
    rule = db.query(GreenCreditRule).filter(
        GreenCreditRule.waste_class == req.classification.class_name,
        GreenCreditRule.active == True
    ).first()
    points = rule.points if rule else 0

    # Business Logic Overrides
    if req.classification.confidence < 0.65 or req.classification.class_name == "mixed":
        points = 0

    return DisposalStartResponse(
        session_id=session.id,
        recommended_disposal_type=req.classification.category_group,
        points_available=points,
        verification_required=True
    )

@router.post("/{session_id}/verify", response_model=VerifyResponse)
def verify_disposal(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_role("student"))):
    engine = RewardEngine(db)
    
    # Fetch session to know the user_id beforehand for the response (if reward engine fails we might not have it, but we can query it)
    session = db.query(DisposalSession).filter(DisposalSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
        
    user_id = session.user_id

    try:
        result = engine.verify_and_reward(session_id)
        
        # Calculate new total
        total = engine.get_user_balance(user_id)
        
        return VerifyResponse(
            user_id=user_id,
            total_credits=total,
            earned_this_session=result["points_awarded"],
            transaction_id=result["transaction_id"]
        )
    except RewardError as e:
        raise HTTPException(status_code=400, detail=str(e))
