# Analyst Curation Loop Learnings (Conversational Analytics Feedback)

## Learning 1 (`warranty-spend-overstatement-fix`)
- **Observed Agent Failure**: When asked for *"Total warranty spend by defect category"*, an ungrounded agent ran `SELECT defect_category, SUM(claim_amount) FROM warranty_claims GROUP BY 1`.
- **Root Cause**: The query summed unadjudicated (`Pending`, `Under Review`) and rejected (`Denied`) claims alongside `Approved` claims.
- **Verified Correction**: Always filter `claim_status = 'Approved'` for realized spend, or separate `Approved` vs. `Open Reserve Exposure` (`Pending`, `Under Review`) into distinct columns.

## Learning 2 (`dealership-warranty-absorption-trap`)
- **Observed Agent Failure**: When asked *"How much service cost did the OEM absorb under warranty across dealerships?"*, an ungrounded agent filtered `WHERE service_type = 'Warranty Repair'`.
- **Root Cause**: `service_orders` also records covered `'Repair'` and `'Recall Service'` orders where `is_warranty_covered = TRUE` and `customer_paid_amount = 0`.
- **Verified Correction**: Filter `service_orders` strictly using `WHERE is_warranty_covered = TRUE` and compute `SUM(total_cost - customer_paid_amount)`.

## Learning 3 (`parts-usage-fanout-on-claims`)
- **Observed Agent Failure**: Joining `warranty_claims` directly to `service_parts_usage` on `service_order_id` and running `SUM(w.claim_amount)` inflated warranty claim dollars proportionally to replaced part count per visit.
- **Root Cause**: `service_parts_usage` has `N:1` cardinality to `service_order_id`.
- **Verified Correction**: Pre-aggregate `service_parts_usage` by `service_order_id` using `LOGICAL_AND(defective_part_returned)` in a CTE before joining to `warranty_claims`.
