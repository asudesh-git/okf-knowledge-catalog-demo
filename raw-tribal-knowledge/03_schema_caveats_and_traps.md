# Tacit Schema Caveats & Data Traps in `sa-demo-agentic`

## Trap 1: Dimension Table Catalog Padding (`259 rows` vs `7–8 active entities`)
- **Affected Tables**:
  - `sa-demo-agentic.auto_manufacturing_data.plants` (259 rows; only **7 active plants** have assembly lines, parts inventory, or vehicles built).
  - `sa-demo-agentic.auto_sales_data.vehicle_models` (259 rows; only **8 active models**, `model_id` 1..8, have vehicle sales or warranty claims).
  - `sa-demo-agentic.auto_sales_data.dealerships` (259 rows; only **8 active dealerships**, `dealership_id` 1..8, have sales or service orders).
- **Impact on AI Agents**: Any agent that runs `SELECT AVG(annual_capacity) FROM plants` or `LEFT JOIN vehicle_sales` from the dimension table without filtering to active operational entities dilutes per-entity averages by **32x** and outputs 251 empty rows.
- **Mandatory Guardrail**: Always `INNER JOIN` to fact tables (`vehicle_sales`, `service_orders`, `warranty_claims`, `assembly_line_status`) or filter `WHERE model_id BETWEEN 1 AND 8` / `dealership_id BETWEEN 1 AND 8`.

## Trap 2: `build_plant_name` vs `part_source_plant_name` in `warranty_claims`
- **Affected Table**: `sa-demo-agentic.auto_aftersales_data.warranty_claims`
- **Impact on AI Agents**: `warranty_claims` has two plant columns:
  - `build_plant_name`: Final assembly plant where the vehicle (`vin`) was built.
  - `part_source_plant_name`: Component plant that manufactured the failed part.
- **Mandatory Guardrail**:
  - For **Assembly Plant Quality Audits**, group by `build_plant_name` and filter `supplier_fault = FALSE`.
  - For **Component/Stamping Plant Defect Audits**, group by `part_source_plant_name`.

## Trap 3: `service_type = 'Warranty Repair'` Misses 48% of Covered Service Cost
- **Affected Table**: `sa-demo-agentic.auto_aftersales_data.service_orders`
- **Impact on AI Agents**: Filtering `WHERE service_type = 'Warranty Repair'` captures only 922 orders (`$826,977.80`), missing 690 `'Repair'` orders (`$558,639.28`) and 282 `'Recall Service'` orders (`$205,769.77`) that ALSO have `is_warranty_covered = TRUE` and `customer_paid_amount = 0`.
- **Mandatory Guardrail**: Always use `WHERE is_warranty_covered = TRUE` when calculating OEM-absorbed dealership repair spend.

## Trap 4: Zero Native BigQuery Column Descriptions in `auto_aftersales_data`
- **Affected Dataset**: `sa-demo-agentic.auto_aftersales_data`
- **Impact on AI Agents**: All 6 tables in `auto_aftersales_data` originally had `0` column descriptions in BigQuery `INFORMATION_SCHEMA.COLUMN_FIELD_PATHS`, forcing agents to guess column semantics from column names alone.

## Trap 5: Cross-Cloud Promo Code Typo & Identity Match Confidence (`auto_sales_data`)
- **Affected Tables**: `customer_identity_crosswalk`, `crm_campaign_history`
- **Mandatory Guardrail**: Filter `match_confidence >= 0.85` for verified customer attribution, and always include both `'PLATINUM-VIP'` and legacy typo `'PLATNUM-VIP'` when filtering Platinum VIP campaign conversions.
