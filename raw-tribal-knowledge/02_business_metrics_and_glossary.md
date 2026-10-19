# Enterprise Business Metrics & Canonical Formulas

## 1. Realized Warranty Cost (`realized_warranty_cost`)
- **Definition**: Adjudicated, financially recognized OEM warranty claim expenditure.
- **Canonical SQL Formula**:
  `SUM(CASE WHEN claim_status = 'Approved' THEN claim_amount ELSE 0 END)` on `sa-demo-agentic.auto_aftersales_data.warranty_claims`.
- **Empirical Baseline in `sa-demo-agentic`**: **`$1,254,786.01`** across **1,331 approved claims** (vs. `$1,798,306.90` gross unfiltered `SUM(claim_amount)` across all 1,894 claims).
- **Exclusions**: Must exclude `'Pending'` (`$217,261.21`), `'Under Review'` (`$186,755.21`), and `'Denied'` (`$139,504.47`).

## 2. Open Warranty Reserve Exposure (`open_warranty_exposure`)
- **Definition**: Unadjudicated warranty liability currently in review queues.
- **Canonical SQL Formula**:
  `SUM(CASE WHEN claim_status IN ('Pending', 'Under Review') THEN claim_amount ELSE 0 END)`
- **Empirical Baseline in `sa-demo-agentic`**: **`$404,016.42`** (`233 Pending + 186 Under Review = 419 claims`).

## 3. Supplier Chargeback Recovery & Unrecovered Supplier Leakage (`net_oem_warranty_burden`)
- **Definition**: Under OEM Supplier Quality Assurance (SQA) contracts, when an `'Approved'` warranty claim is caused by a vendor defect (`supplier_fault = TRUE`), the OEM recovers **70% of `claim_amount`** from the supplier **ONLY IF** all defective parts replaced on that `service_order_id` were physically returned to the central teardown depot (`LOGICAL_AND(defective_part_returned) = TRUE` in `service_parts_usage`).
- **Unrecovered Supplier Leakage**: If any replaced part on an approved supplier-fault claim has `defective_part_returned = FALSE`, the supplier chargeback is forfeited (`0%` recovery), creating **Dealership Core-Return Leakage**.
- **Net OEM Warranty Burden Formula**:
  `Realized Warranty Cost - Recoverable Supplier Chargeback`

## 4. Total OEM Warranty-Covered Service Absorption (`oem_warranty_absorption`)
- **Definition**: Total dealership repair cost absorbed by the OEM across all warranty-covered visits in `service_orders`.
- **Canonical SQL Formula**:
  `SUM(total_cost - customer_paid_amount) WHERE is_warranty_covered = TRUE`
- **Empirical Baseline in `sa-demo-agentic`**: **`$1,591,386.85`** across **1,894 service orders**:
  - `service_type = 'Warranty Repair'` (922 orders): `$826,977.80`
  - `service_type = 'Repair' AND is_warranty_covered = TRUE` (690 goodwill/bumper-to-bumper covered repairs): `$558,639.28`
  - `service_type = 'Recall Service' AND is_warranty_covered = TRUE` (282 campaign repairs): `$205,769.77`

## 5. Active Warranty Entitlement Fleet (`active_warranty_entitlement_fleet`)
- **Definition**: Count of vehicles currently entitled to OEM warranty coverage.
- **Canonical SQL Filter**:
  `warranty_end_date >= CURRENT_DATE() AND (ownership_status = 'Active' OR (ownership_status = 'Transferred' AND extended_warranty_purchased = TRUE))`
- **Empirical Baseline in `sa-demo-agentic`**: **`4,650` vehicles** (`4,582 Active + 68 Transferred with transferable extended warranty`). Excludes `114 Buyback` and `236 Transferred without extended warranty`.

## 6. Assembly Plant Claim Rate per 1,000 Vehicles Built (`plant_claim_rate_per_1000_built`)
- **Definition**: Approved assembly-fault warranty claims per 1,000 vehicles produced by a final assembly plant.
- **Canonical SQL Formula**:
  `COUNTIF(w.claim_status = 'Approved' AND w.supplier_fault = FALSE) * 1000.0 / COUNT(DISTINCT v.vin)` joined via `w.build_plant_name = p.plant_name`.
