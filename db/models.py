from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import relationship
import datetime
import uuid

from .database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False, default="")
    role = Column(String, nullable=False, default="student")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship("DisposalSession", back_populates="user")
    transactions = relationship("GreenCreditTransaction", back_populates="user")

class DisposalSession(Base):
    __tablename__ = "disposal_sessions"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    predicted_class = Column(String, nullable=False)
    category_group = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    image_hash = Column(String, index=True)
    status = Column(String, default="pending") # pending, verified, rejected
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    verification = relationship("DisposalVerification", back_populates="session", uselist=False)
    transaction = relationship("GreenCreditTransaction", back_populates="session", uselist=False)

class DisposalVerification(Base):
    __tablename__ = "disposal_verifications"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    disposal_session_id = Column(String, ForeignKey("disposal_sessions.id"), unique=True)
    verification_method = Column(String, nullable=False)
    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("DisposalSession", back_populates="verification")

class GreenCreditTransaction(Base):
    __tablename__ = "green_credit_transactions"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    disposal_session_id = Column(String, ForeignKey("disposal_sessions.id"), unique=True)
    points = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="transactions")
    session = relationship("DisposalSession", back_populates="transaction")

class GreenCreditRule(Base):
    __tablename__ = "green_credit_rules"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    waste_class = Column(String, unique=True, index=True, nullable=False)
    points = Column(Integer, nullable=False)
    active = Column(Boolean, default=True)

# --- E-Waste Lifecycle MVP Models ---

class EwasteRecycler(Base):
    __tablename__ = "ewaste_recyclers"
    
    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    name = Column(String, nullable=False)
    authorization_reference = Column(String, nullable=False)

class EwasteAsset(Base):
    __tablename__ = "ewaste_assets"
    
    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    asset_id = Column(String, unique=True, index=True, nullable=False) # e.g. LAB-PC-001
    asset_name = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)
    department = Column(String, nullable=False)
    serial_number = Column(String, nullable=False)
    status = Column(String, default="REGISTERED", nullable=False)
    
    # Handover details
    recycler_id = Column(String, ForeignKey("ewaste_recyclers.id"), nullable=True)
    handover_date = Column(DateTime, nullable=True)
    received_by = Column(String, nullable=True)
    
    # Recycled details
    certificate_reference = Column(String, nullable=True)
    recycled_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    audit_trail = relationship("EwasteAuditTrail", back_populates="asset")

class EwasteAuditTrail(Base):
    __tablename__ = "ewaste_audit_trails"
    
    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    asset_internal_id = Column(String, ForeignKey("ewaste_assets.id"))
    previous_status = Column(String, nullable=False)
    new_status = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    asset = relationship("EwasteAsset", back_populates="audit_trail")

# --- Smart-Bin Telemetry MVP Models ---

class SmartBin(Base):
    __tablename__ = "smart_bins"
    
    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    bin_id = Column(String, unique=True, index=True, nullable=False) # e.g. BIN-001
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    waste_type = Column(String, nullable=False)
    capacity_percent = Column(Float, default=100.0) # Used to check overflow limit
    current_fill_percent = Column(Float, default=0.0)
    status = Column(String, default="NORMAL", nullable=False)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    
    telemetry = relationship("TelemetryReading", back_populates="bin")
    collections = relationship("CollectionEvent", back_populates="bin")

class TelemetryReading(Base):
    __tablename__ = "telemetry_readings"
    
    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    bin_internal_id = Column(String, ForeignKey("smart_bins.id"))
    fill_percent = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    bin = relationship("SmartBin", back_populates="telemetry")

class CollectionEvent(Base):
    __tablename__ = "collection_events"
    
    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    bin_internal_id = Column(String, ForeignKey("smart_bins.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    bin = relationship("SmartBin", back_populates="collections")
