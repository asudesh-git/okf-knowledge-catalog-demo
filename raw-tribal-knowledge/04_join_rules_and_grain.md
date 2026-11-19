# Cross-Dataset Join Rules, Primary Keys & Cardinality Grain

## Table Grains
1. `auto_aftersales_data.vehicle_ownership`: **1 row per `vin`**.
2. `auto_sales_data.vehicle_sales`: **1 row per `sale_id` / `vin`** (`1:1` with `vehicle_ownership.vin`).
3. `auto_aftersales_data.service_orders`: **1 row per `service_order_id`** (`N:1` to `vin`, `dealership`, and `technician_id`).
4. `auto_aftersales_data.warranty_claims`: **1 row per `claim_id`** (`1:1` with `service_orders.service_order_id` where `is_warranty_covered = TRUE`).
5. `auto_aftersales_data.service_parts_usage`: **1 row per `usage_id`** (`N:1` to `service_order_id` — multiple part line items can belong to a single repair order).

## Critical Join Fan-Out Warning (`warranty_claims` <-> `service_parts_usage`)
- Joining `warranty_claims` directly to `service_parts_usage` on `service_order_id` multiplies each warranty claim row by the number of replacement parts installed during that service visit.
- **NEVER** compute `SUM(w.claim_amount)` after joining `warranty_claims` directly to `service_parts_usage` without first pre-aggregating `service_parts_usage` to the `service_order_id` grain (using `GROUP BY service_order_id` with `LOGICAL_AND(defective_part_returned)` and `SUM(extended_cost)`).
