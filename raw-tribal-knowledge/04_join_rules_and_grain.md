# Cross-Dataset Join Rules, Primary Keys & Cardinality Grain

## Table Grains
1. `auto_aftersales_data.vehicle_ownership`: **1 row per `vin`** (5,000 rows).
2. `auto_sales_data.vehicle_sales`: **1 row per `sale_id` / `vin`** (5,000 rows, 1:1 with `vehicle_ownership.vin`).
3. `auto_aftersales_data.service_orders`: **1 row per `service_order_id`** (6,104 rows; `N:1` to `vin`, `N:1` to `dealership_id`, `N:1` to `technician_id`).
4. `auto_aftersales_data.warranty_claims`: **1 row per `claim_id`** (1,894 rows; **1:1** with `service_orders.service_order_id` where `is_warranty_covered = TRUE`).
5. `auto_aftersales_data.service_parts_usage`: **1 row per `usage_id`** (10,861 rows; **N:1** to `service_order_id`—averaging 1.78 part rows per service order).

## Critical Join Fan-Out Warning (`warranty_claims` <-> `service_parts_usage`)
- Joining `warranty_claims` (`1,894` rows) directly to `service_parts_usage` (`10,861` rows) on `service_order_id` produces **3,372 joined rows**.
- **NEVER** compute `SUM(w.claim_amount)` after joining `warranty_claims` to `service_parts_usage` without first pre-aggregating `service_parts_usage` to the `service_order_id` grain (e.g., `GROUP BY service_order_id` with `LOGICAL_AND(defective_part_returned)` and `SUM(total_part_cost)`), OR using `SUM(DISTINCT ...)`. Unaggregated joins inflate `claim_amount` by ~1.78x!
