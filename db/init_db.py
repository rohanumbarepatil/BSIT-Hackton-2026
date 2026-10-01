from db.database import engine, Base, SessionLocal
from db.models import User, GreenCreditRule, EwasteRecycler, EwasteAsset, EwasteAuditTrail, SmartBin, TelemetryReading
import datetime

def init_db():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if test user exists
    test_user = db.query(User).filter(User.email == "test@example.com").first()
    if not test_user:
        test_user = User(id="test_user_1", name="Test User", email="test@example.com")
        db.add(test_user)
        
    # Check if rules exist
    if db.query(GreenCreditRule).count() == 0:
        rules = [
            GreenCreditRule(waste_class="organic", points=5),
            GreenCreditRule(waste_class="paper", points=5),
            GreenCreditRule(waste_class="glass", points=5),
            GreenCreditRule(waste_class="plastic", points=5),
            GreenCreditRule(waste_class="metal", points=8),
            GreenCreditRule(waste_class="ewaste", points=20),
            GreenCreditRule(waste_class="mixed", points=0),
        ]
        db.add_all(rules)
        
    # Seed Recyclers
    if db.query(EwasteRecycler).count() == 0:
        r1 = EwasteRecycler(name="GreenTech Recyclers", authorization_reference="AUTH-1234")
        r2 = EwasteRecycler(name="EnviroSafe Disposal", authorization_reference="AUTH-9876")
        db.add_all([r1, r2])
        db.flush()
        
        # Seed Assets
        a1 = EwasteAsset(asset_id="LAB-PC-001", asset_name="Dell Optiplex 7050", asset_type="Desktop PC", department="Computer Lab A", serial_number="SN1001", status="REGISTERED")
        a2 = EwasteAsset(asset_id="LAB-MON-002", asset_name="Dell 24in Monitor", asset_type="Monitor", department="Computer Lab A", serial_number="SN1002", status="IN_USE")
        a3 = EwasteAsset(asset_id="LAB-KBD-003", asset_name="Logitech Keyboard", asset_type="Keyboard", department="Computer Lab B", serial_number="SN1003", status="DECOMMISSIONED")
        a4 = EwasteAsset(asset_id="LAB-BAT-004", asset_name="APC UPS Battery", asset_type="Battery", department="Server Room", serial_number="SN1004", status="HANDED_OVER", recycler_id=r1.id, handover_date=datetime.datetime.utcnow(), received_by="John Doe")
        
        # Asset 5 Full Lifecycle
        a5 = EwasteAsset(asset_id="LAB-PRN-005", asset_name="HP LaserJet Pro", asset_type="Printer", department="Library", serial_number="SN1005", status="RECYCLED", recycler_id=r2.id, handover_date=datetime.datetime.utcnow(), received_by="Jane Doe", certificate_reference="CERT-999", recycled_at=datetime.datetime.utcnow())
        
        db.add_all([a1, a2, a3, a4, a5])
        db.flush()
        
        # Seed Audit Trail for Asset 5
        audits = [
            EwasteAuditTrail(asset_internal_id=a5.id, previous_status="NONE", new_status="REGISTERED", notes="Initial Registration"),
            EwasteAuditTrail(asset_internal_id=a5.id, previous_status="REGISTERED", new_status="IN_USE", notes="Deployed to Library"),
            EwasteAuditTrail(asset_internal_id=a5.id, previous_status="IN_USE", new_status="DECOMMISSIONED", notes="End of life"),
            EwasteAuditTrail(asset_internal_id=a5.id, previous_status="DECOMMISSIONED", new_status="HANDED_OVER", notes="Handed to EnviroSafe"),
            EwasteAuditTrail(asset_internal_id=a5.id, previous_status="HANDED_OVER", new_status="RECYCLED", notes="Recycled, Cert #CERT-999 received")
        ]
        db.add_all(audits)

    # Seed Smart Bins
    if db.query(SmartBin).count() == 0:
        now = datetime.datetime.utcnow()
        # BIN-001: NORMAL
        b1 = SmartBin(bin_id="BIN-001", name="BIN-001", location="CSE Building", waste_type="Dry Recyclable", current_fill_percent=45.0, status="NORMAL")
        # BIN-002: WARNING
        b2 = SmartBin(bin_id="BIN-002", name="BIN-002", location="Library", waste_type="Dry Recyclable", current_fill_percent=75.0, status="WARNING")
        # BIN-003: PREDICTED_FULL (Will be inferred as Critical, but let's give it telemetry to show high fill rate)
        b3 = SmartBin(bin_id="BIN-003", name="BIN-003", location="Hostel", waste_type="Biodegradable", current_fill_percent=80.0, status="WARNING")
        # BIN-004: CRITICAL
        b4 = SmartBin(bin_id="BIN-004", name="BIN-004", location="Cafeteria", waste_type="Biodegradable", current_fill_percent=95.0, status="CRITICAL")
        # BIN-005: OVERFLOW
        b5 = SmartBin(bin_id="BIN-005", name="BIN-005", location="Electronics Lab", waste_type="E-Waste", current_fill_percent=105.0, status="OVERFLOW")
        
        db.add_all([b1, b2, b3, b4, b5])
        db.flush()
        
        # Telemetry to make BIN-003 a "PREDICTED_FULL" scenario
        # e.g., 2 hours ago it was at 10%, now at 80% (35%/hr) -> full in < 1 hour
        t1 = TelemetryReading(bin_internal_id=b3.id, fill_percent=10.0, timestamp=now - datetime.timedelta(hours=2))
        t2 = TelemetryReading(bin_internal_id=b3.id, fill_percent=80.0, timestamp=now)
        
        db.add_all([t1, t2])
        
    db.commit()
    db.close()

if __name__ == "__main__":
    print("Initializing DB...")
    init_db()
    print("Done.")
