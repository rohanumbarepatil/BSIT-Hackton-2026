from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import datetime

from db.database import get_db
from db.models import User
from services.reward_engine import RewardEngine

router = APIRouter(prefix="/api/v1/users", tags=["users"])

class CreditBalanceResponse(BaseModel):
    user_id: str
    total_credits: int

class TransactionItem(BaseModel):
    id: str
    points: int
    reason: str
    created_at: datetime.datetime

class CreditHistoryResponse(BaseModel):
    user_id: str
    history: List[TransactionItem]

from api.routers.auth import require_role

@router.get("/{user_id}/credits", response_model=CreditBalanceResponse)
def get_credits(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_role("student", "admin"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    engine = RewardEngine(db)
    balance = engine.get_user_balance(user_id)
    
    return CreditBalanceResponse(user_id=user_id, total_credits=balance)

@router.get("/{user_id}/credit-history", response_model=CreditHistoryResponse)
def get_credit_history(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_role("student", "admin"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    engine = RewardEngine(db)
    history = engine.get_user_history(user_id)
    
    return CreditHistoryResponse(user_id=user_id, history=history)
