# Enterprise Business Metrics & Canonical Formulas

## 1. Realized Warranty Cost (`realized_warranty_cost`)
- **Definition**: Adjudicated, financially recognized OEM warranty claim expenditure.
- **Canonical SQL Formula**:
  `SUM(CASE WHEN claim_status = 'Approved' THEN claim_amount ELSE 0 END)` on `sa-demo-agentic.auto_aftersales_data.warranty_claims`.
- **Exclusions**: Exclude `'Pending'`, `'Under Review'` (open reserve exposure), and `'Denied'` (`$0` OEM financial liability).

## 2. Open Warranty Reserve Exposure (`open_warranty_exposure`)
- **Definition**: Unadjudicated warranty liability currently awaiting final adjudication.
- **Canonical SQL Formula**:
  `SUM(CASE WHEN claim_status IN ('Pending', 'Under Review') THEN claim_amount ELSE 0 END)`

## 3. Supplier Chargeback Recovery & Unrecovered Supplier Leakage (`net_oem_warranty_burden`)
- **Definition**: Under OEM Supplier Quality Assurance (SQA) contracts, when an `'Approved'` warranty claim is caused by a vendor defect (`supplier_fault = TRUE`), the OEM recovers **70% of `claim_amount`** from the supplier **ONLY IF** all defective parts replaced on that `service_order_id` were physically returned to the central teardown depot (`LOGICAL_AND(defective_part_returned) = TRUE` in `service_parts_usage`).
- **Unrecovered Supplier Leakage**: If any replaced part on an approved supplier-fault claim has `defective_part_returned = FALSE`, the supplier chargeback is forfeited (`0%` recovery), creating **Dealership Core-Return Leakage**.
- **Net OEM Warranty Burden Formula**:
  `Realized Warranty Cost - Recoverable Supplier Chargeback`

## 4. Total OEM Warranty-Covered Service Absorption (`oem_warranty_absorption`)
- **Definition**: Total dealership repair cost absorbed by the OEM across all warranty-covered visits in `service_orders`.
- **Canonical SQL Formula**:
  `SUM(total_cost - customer_paid_amount) WHERE is_warranty_covered = TRUE`
- **Coverage Scope**: Captures all warranty-absorbed visits across `'Warranty Repair'`, `'Repair'` (goodwill/bumper-to-bumper covered), and `'Recall Service'` orders.

## 5. Active Warranty Entitlement Fleet (`active_warranty_entitlement_fleet`)
- **Definition**: Count of vehicles currently entitled to OEM warranty coverage.
- **Canonical SQL Filter**:
  `warranty_end_date >= CURRENT_DATE() AND (ownership_status = 'Active' OR (ownership_status = 'Transferred' AND extended_warranty_purchased = TRUE))`
- **Exclusions**: Permanently excludes `'Buyback'` vehicles and secondary-market `'Transferred'` vehicles without an extended warranty.

## 6. Assembly Plant Claim Rate per 1,000 Vehicles Built (`plant_claim_rate_per_1000_built`)
- **Definition**: Approved assembly-fault warranty claims per 1,000 vehicles produced by a final assembly plant.
- **Canonical SQL Formula**:
  `COUNTIF(w.claim_status = 'Approved' AND w.supplier_fault = FALSE) * 1000.0 / COUNT(DISTINCT v.vin)` joined via `w.build_plant_name = p.plant_name`.
