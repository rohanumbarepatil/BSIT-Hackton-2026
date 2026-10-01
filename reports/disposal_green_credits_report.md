# Application Phase 2: Disposal Verification & Green Credits

The Disposal workflow and Green Credits reward engine have been successfully implemented and integrated into the FastAPI backend without altering the underlying ML model inference abstraction.

## 1. Database Schema
Implemented via `SQLAlchemy` (PostgreSQL-compatible) containing:
*   `users`: Stores basic user profiles.
*   `disposal_sessions`: Acts as the bridge between an AI prediction and a physical action. Stores the `predicted_class`, `confidence`, and `image_hash`.
*   `disposal_verifications`: Tracks verification events tied strictly 1:1 with disposal sessions.
*   `green_credit_transactions`: Immutable point transaction ledger mapping `user_id`, `points`, and `reason` (linked 1:1 to a verified session).
*   `green_credit_rules`: Dynamic points table ensuring rewards can be tuned without deploying new API code.

## 2. Waste Point Rules (Configured)
Stored inside `green_credit_rules`:
*   `organic` = 5
*   `paper` = 5
*   `glass` = 5
*   `plastic` = 5
*   `metal` = 8
*   `ewaste` = 20
*   `mixed` = 0

*(Note: These are explicitly configured development values and can be updated at any time via the database.)*

## 3. Reward Engine & Anti-Abuse Logic
The `RewardEngine` strictly enforces business logic within SQL atomic transactions:
1.  **Duplicate Protection**: A session can only be verified once. Any duplicate `/verify` call triggers an immediate `400 Bad Request`.
2.  **Confidence Check**: If the stored session's AI confidence was below `0.65`, no points are awarded, and the session is marked `rejected`.
3.  **Mixed Waste**: Classification of `mixed` waste automatically results in 0 points, even if the model was 99% confident.
4.  **Transaction Isolation**: Point transactions are flushed sequentially inside atomic DB commits to prevent race conditions (e.g., rapid-firing the verify endpoint).

## 4. E-Waste Limitation
The API strictly surfaces the following e-waste guidance:
> *"DANGER: Dispose of in the red e-waste collection bin only. Do not place in general waste."*

**Important Limitation:** The ML layer continues to report (via `/api/v1/model/info`) that the model identifies battery imagery only, and no claims have been made regarding full hardware/PCB coverage.

## 5. Endpoints Deployed
*   `POST /api/v1/disposal/start`: Begins the transaction based on an AI classification.
*   `POST /api/v1/disposal/{session_id}/verify`: Concludes the transaction.
*   `GET /api/v1/users/{user_id}/credits`: Fetches current lifetime balance.
*   `GET /api/v1/users/{user_id}/credit-history`: Fetches the entire immutable point ledger.

## 6. Testing Results
`pytest tests/test_disposal.py -v` was executed successfully.
*   `test_disposal_flow` (Full Start -> Verify -> Balance -> History) ✅
*   `test_low_confidence_disposal` (Fails to award points) ✅
*   `test_mixed_waste_disposal` (Fails to award points) ✅
*   `test_invalid_user_start` (404 Not Found) ✅
*   `test_invalid_session_verify` (404 Not Found) ✅

## 7. Known Limitations
> **"User confirmation is a development-stage verification mechanism and does not constitute tamper-proof proof of physical disposal."**

The `/verify` endpoint currently assumes the user actually deposited the item. Smart-Bin IoT telemetry or hardware QR-code verification is required in subsequent phases to make this fraud-proof.
