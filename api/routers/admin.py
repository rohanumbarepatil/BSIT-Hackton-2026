from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from datetime import datetime

from db.database import get_db
from db.models import User, EwasteAuditTrail, GreenCreditTransaction, DisposalVerification, DisposalSession
from api.routers.auth import require_role

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
    dependencies=[Depends(require_role("admin"))]
)

@router.get("/users")
def get_admin_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    # also get total credits per user to display
    result = []
    for u in users:
        credits = db.query(func.sum(GreenCreditTransaction.points)).filter(GreenCreditTransaction.user_id == u.id).scalar() or 0
        result.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "green_credits": credits,
            "status": "Active" if u.is_active else "Inactive",
            "joined": u.created_at
        })
    return result

@router.get("/audit-logs")
def get_admin_audit_logs(db: Session = Depends(get_db)):
    # e-waste audits
    ewaste_logs = db.query(EwasteAuditTrail).all()
    
    # credit/disposal audits
    transactions = db.query(GreenCreditTransaction).all()

    audit_logs = []
    
    for log in ewaste_logs:
        audit_logs.append({
            "timestamp": log.timestamp.isoformat(),
            "actor": "System/Staff", 
            "action": f"{log.previous_status} -> {log.new_status}",
            "entity": log.asset_internal_id,
            "role": "STAFF",
            "details": log.notes or "Status update"
        })
        
    for txn in transactions:
        user = db.query(User).filter(User.id == txn.user_id).first()
        actor_name = user.name if user else "Unknown"
        role_name = user.role.upper() if user else "STUDENT"
        
        audit_logs.append({
            "timestamp": txn.created_at.isoformat(),
            "actor": actor_name,
            "action": "CREDIT_AWARDED",
            "entity": txn.disposal_session_id,
            "role": role_name,
            "details": f"{txn.reason} ({txn.points} points)"
        })
        
    # Sort descending by timestamp
    audit_logs.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"items": audit_logs, "total": len(audit_logs)}

@router.get("/credits/overview")
def get_credits_overview(db: Session = Depends(get_db)):
    total_awarded = db.query(func.sum(GreenCreditTransaction.points)).scalar() or 0
    students_participating = db.query(GreenCreditTransaction.user_id).distinct().count()
    verified_disposals = db.query(DisposalVerification).filter(DisposalVerification.verified == True).count()
    credits_today = db.query(func.sum(GreenCreditTransaction.points)).filter(
        func.date(GreenCreditTransaction.created_at) == datetime.utcnow().date()
    ).scalar() or 0
    
    return {
        "total_awarded": total_awarded,
        "students_participating": students_participating,
        "verified_disposals": verified_disposals,
        "credits_today": credits_today
    }

@router.get("/credits/students")
def get_student_credit_distribution(db: Session = Depends(get_db)):
    # Find all students who have credits
    users = db.query(User).filter(User.role == "student").all()
    distribution = []
    
    for u in users:
        credits = db.query(func.sum(GreenCreditTransaction.points)).filter(GreenCreditTransaction.user_id == u.id).scalar() or 0
        verifications = db.query(DisposalSession).join(DisposalVerification).filter(
            DisposalSession.user_id == u.id,
            DisposalVerification.verified == True
        ).count()
        
        last_txn = db.query(GreenCreditTransaction).filter(GreenCreditTransaction.user_id == u.id).order_by(GreenCreditTransaction.created_at.desc()).first()
        
        distribution.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "total_credits": credits,
            "verified_disposals": verifications,
            "last_activity": last_txn.created_at.isoformat() if last_txn else None
        })
        
    distribution.sort(key=lambda x: x["total_credits"], reverse=True)
    
    # Assign ranks
    for idx, item in enumerate(distribution):
        item["rank"] = idx + 1
        
    return distribution
