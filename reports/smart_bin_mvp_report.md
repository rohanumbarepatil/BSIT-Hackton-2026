# Campus Smart-Bin Telemetry MVP

The software-only simulated telemetry MVP has been completed successfully, perfectly mimicking IoT data flow for the hackathon demo without needing physical hardware.

## 1. Architecture & Telemetry Simulation
The architecture utilizes a completely hardware-agnostic design. A simple `POST /api/v1/bins/{bin_id}/telemetry` endpoint expects a JSON payload containing only the `fill_percent`. 
*   **No Hardware Code**: No ESP32, Arduino, MQTT, or GPIO dependencies were introduced.
*   **State Machine**:
    *   `0-69%` = `NORMAL`
    *   `70-84%` = `WARNING`
    *   `85-99%` = `CRITICAL`
    *   `100%+` = `OVERFLOW`

## 2. Prediction Method (Predictive Collection)
The predictive engine dynamically calculates the fill rate based exclusively on incoming telemetry timestamps:
*   `fill_rate = change in fill_percent / time_elapsed_in_hours`
*   `hours_to_full = (100 - current_fill_percent) / fill_rate`

If a bin is filling fast enough to reach 100% in under 12 hours, the alert state shifts to `PREDICTED_FULL` (e.g. *"BIN-003 predicted to reach capacity in 0.57 hours."*). If a bin lacks 2 telemetry events, it safely returns `INSUFFICIENT_HISTORY` without fabricating data.

## 3. Demo Bins Seeded
5 demo bins were successfully seeded to cover all edge cases:
1.  **BIN-001 (CSE Building)** - Normal (45%)
2.  **BIN-002 (Library)** - Warning (75%)
3.  **BIN-003 (Hostel)** - Warning (80%, but seeded with telemetry making it `PREDICTED_FULL`)
4.  **BIN-004 (Cafeteria)** - Critical (95%)
5.  **BIN-005 (Electronics Lab)** - Overflow (105%)

## 4. Endpoints Built
*   `GET /api/v1/bins`: Lists all smart bins and their current statuses.
*   `GET /api/v1/bins/{bin_id}`: Retrieves specific bin data.
*   `POST /api/v1/bins/{bin_id}/telemetry`: Accepts simulated sensor readings.
*   `GET /api/v1/bins/{bin_id}/prediction`: Dynamically calculates fill rates.
*   `GET /api/v1/bins/alerts`: Aggregates active Overflow, Critical, Warning, and Predicted Full alerts.
*   `POST /api/v1/bins/{bin_id}/collect`: Resets a bin to `0% / NORMAL` and drops a `0%` telemetry reading to correctly reset the math.
*   `GET /api/v1/bins/dashboard/stats`: Supplies the dashboard with integer totals of bins in each status.

## 5. Test Results
The MVP logic was validated via `pytest tests/test_smartbins.py -v`.
*   100% Pass Rate (5/5).
*   Correctly calculates predictions, captures overflows, handles telemetry state transitions, and performs clean collection resets.

## 6. Protection of Existing Assets
**Important:** No modifications were made to the AI Image Classifier, the Green Credit engine, the Institutional E-Waste APIs, or the dataset prep scripts. The MVP strictly adheres to the requested bounds.
