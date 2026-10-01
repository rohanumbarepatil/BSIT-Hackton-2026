from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.models import DisposalSession, DisposalVerification, GreenCreditTransaction, GreenCreditRule

class RewardError(Exception):
    pass

class RewardEngine:
    def __init__(self, db: Session):
        self.db = db

    def _get_points_for_class(self, waste_class: str) -> int:
        rule = self.db.query(GreenCreditRule).filter(
            GreenCreditRule.waste_class == waste_class,
            GreenCreditRule.active == True
        ).first()
        if not rule:
            return 0
        return rule.points

    def verify_and_reward(self, session_id: str) -> dict:
        """
        Verifies a disposal session (development user confirmation) and awards points if eligible.
        Executes within a database transaction to prevent race conditions.
        """
        # Fetch the session
        session = self.db.query(DisposalSession).filter(DisposalSession.id == session_id).with_for_update().first()
        
        if not session:
            raise RewardError("Invalid disposal session ID.")

        if session.status != "pending":
            raise RewardError(f"Session is already {session.status}.")

        # Check existing verification to be absolutely safe (should be blocked by status, but double check)
        existing_verification = self.db.query(DisposalVerification).filter(DisposalVerification.disposal_session_id == session_id).first()
        if existing_verification:
            raise RewardError("Session has already been verified.")

        # Anti-abuse: Confidence threshold
        # Assuming the classifier threshold check was done previously, but we strictly enforce > 0.65 here
        if session.confidence < 0.65:
            session.status = "rejected"
            self.db.commit()
            raise RewardError("Cannot award points for low-confidence predictions.")

        # Anti-abuse: Mixed waste gets 0 points
        if session.predicted_class == "mixed":
            session.status = "rejected"
            self.db.commit()
            raise RewardError("Mixed waste is not eligible for Green Credits.")

        points_to_award = self._get_points_for_class(session.predicted_class)

        try:
            # 1. Create verification record (Development mechanism)
            verification = DisposalVerification(
                disposal_session_id=session.id,
                verification_method="user_confirmation_development",
                verified=True
            )
            self.db.add(verification)

            # 2. Create transaction if points > 0
            transaction_id = None
            if points_to_award > 0:
                transaction = GreenCreditTransaction(
                    user_id=session.user_id,
                    disposal_session_id=session.id,
                    points=points_to_award,
                    reason=f"Proper disposal of {session.predicted_class}"
                )
                self.db.add(transaction)
                self.db.flush() # flush to get transaction ID
                transaction_id = transaction.id

            # 3. Update session status
            session.status = "verified"
            
            # Commit the atomic transaction
            self.db.commit()

            return {
                "success": True,
                "points_awarded": points_to_award,
                "transaction_id": transaction_id
            }

        except IntegrityError:
            self.db.rollback()
            raise RewardError("Database integrity error. Possible duplicate verification.")
        except Exception as e:
            self.db.rollback()
            raise RewardError(f"Internal reward engine error: {str(e)}")

    def get_user_balance(self, user_id: str) -> int:
        transactions = self.db.query(GreenCreditTransaction).filter(GreenCreditTransaction.user_id == user_id).all()
        return sum(t.points for t in transactions)

    def get_user_history(self, user_id: str) -> list:
        transactions = self.db.query(GreenCreditTransaction).filter(GreenCreditTransaction.user_id == user_id).order_by(GreenCreditTransaction.created_at.desc()).all()
        return [
            {
                "id": t.id,
                "points": t.points,
                "reason": t.reason,
                "created_at": t.created_at
            } for t in transactions
        ]
