# Analyst Curation Loop Learnings (Conversational Analytics Feedback)

## Learning 1 (`warranty-spend-overstatement-fix`)
- **Observed Agent Failure**: When asked for *"Total warranty spend by failure component"*, the ungrounded agent executed `SELECT failure_component, SUM(claim_amount) FROM warranty_claims GROUP BY 1`, reporting **`$1,798,306.90`**.
- **Root Cause**: The agent summed unadjudicated (`Pending`, `Under Review`) and rejected (`Denied`) claims alongside `Approved` claims.
- **Verified Correction**: Always filter `claim_status = 'Approved'` for realized spend (`$1,254,786.01`), or report `Approved` vs `Open Exposure` (`Pending` + `Under Review` = `$404,016.42`) in separate columns.

## Learning 2 (`dealership-warranty-absorption-trap`)
- **Observed Agent Failure**: When asked *"How much service cost did the OEM absorb under warranty across dealerships?"*, the ungrounded agent filtered `WHERE service_type = 'Warranty Repair'`, returning **`$826,977.80`** instead of **`$1,591,386.85`**.
- **Root Cause**: `service_orders` has 690 `'Repair'` rows and 282 `'Recall Service'` rows where `is_warranty_covered = TRUE` and `customer_paid_amount = 0`.
- **Verified Correction**: Filter `service_orders` using `WHERE is_warranty_covered = TRUE` and compute `SUM(total_cost - customer_paid_amount)`.

## Learning 3 (`parts-usage-fanout-on-claims`)
- **Observed Agent Failure**: Joining `warranty_claims` directly to `service_parts_usage` on `service_order_id` and running `SUM(w.claim_amount)` inflated warranty claim dollars from `$1,254,786.01` to **`$2,226,419.83`** (1.77x fan-out).
- **Root Cause**: `service_parts_usage` has multiple part rows per `service_order_id` (`10,861` rows across `6,104` service orders).
- **Verified Correction**: Pre-aggregate `service_parts_usage` by `service_order_id` in a CTE before joining to `warranty_claims`.
