# Tacit Schema Caveats & Data Traps in `sa-demo-agentic`

## Trap 1: Unallocated Dimension Catalog Entries (`plants`, `vehicle_models`, `dealerships`)
- **Affected Tables**:
  - `sa-demo-agentic.auto_manufacturing_data.plants` (includes unallocated facility codes alongside active OEM final assembly plants and component suppliers).
  - `sa-demo-agentic.auto_sales_data.vehicle_models` (includes unallocated/legacy catalog models without active sales).
  - `sa-demo-agentic.auto_sales_data.dealerships` (includes unallocated/inactive franchise codes).
- **Impact on AI Agents**: Any agent that runs `SELECT AVG(capacity) FROM plants` or `LEFT JOIN` from an unfiltered dimension table without joining to active operational tables dilutes per-entity averages and outputs empty rows.
- **Mandatory Guardrail**: Always `INNER JOIN` to active operational/fact tables (`assembly_line_status` for OEM plants; `vehicle_sales`, `service_orders`, or `warranty_claims` for models and dealerships).

## Trap 2: `build_plant_name` vs `part_source_plant_name` in `warranty_claims`
- **Affected Table**: `sa-demo-agentic.auto_aftersales_data.warranty_claims`
- **Impact on AI Agents**: `warranty_claims` carries two plant columns:
  - `build_plant_name`: Final assembly plant where the vehicle (`vin`) was built.
  - `part_source_plant_name`: Component plant that manufactured the failed part.
- **Mandatory Guardrail**:
  - For **Assembly Plant Quality Audits**, group by `build_plant_name` and filter `supplier_fault = FALSE`.
  - For **Component/Supplier Plant Defect Audits**, group by `part_source_plant_name` and filter `supplier_fault = TRUE`.

## Trap 3: `service_type = 'Warranty Repair'` Misses Covered `'Repair'` and `'Recall Service'` Orders
- **Affected Table**: `sa-demo-agentic.auto_aftersales_data.service_orders`
- **Impact on AI Agents**: Filtering `WHERE service_type = 'Warranty Repair'` omits `'Repair'` and `'Recall Service'` orders that also have `is_warranty_covered = TRUE` and `customer_paid_amount = 0`.
- **Mandatory Guardrail**: Always use `WHERE is_warranty_covered = TRUE` when calculating OEM-absorbed dealership repair spend.

## Trap 4: Cross-Cloud Promo Code Typo & Identity Match Confidence (`auto_sales_data`)
- **Affected Tables**: `customer_identity_crosswalk`, `crm_campaign_history`
- **Mandatory Guardrail**: Filter `match_confidence >= 0.85` for verified customer attribution, and always include both `'PLATINUM-VIP'` and legacy typo `'PLATNUM-VIP'` when filtering Platinum VIP campaign conversions.
