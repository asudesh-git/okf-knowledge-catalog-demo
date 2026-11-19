# Automotive Enterprise Domain Ontology (Manufacturing -> Sales -> After-Sales)

## Core Domain Entities & Lifecycle Hierarchy

1. **Manufacturing Plant (`auto_manufacturing_data.plants`)**:
   - Physical assembly or component-manufacturing facility identified by `plant_id` and `plant_name`.
   - **Critical Dual-Role Relationship**: A plant can act as the **Vehicle Final Assembly Plant** (`warranty_claims.build_plant_name`, `vehicle_models.plant_id`) OR as the **Component Source Plant** (`warranty_claims.part_source_plant_name`, `parts_inventory.plant_name`).
   - Operational OEM assembly plants are isolated by joining `plants` (`INNER JOIN`) to `assembly_line_status` on `plant_name`; external Tier-1/Tier-2 component suppliers and unallocated facility codes do not appear on active OEM assembly lines.

2. **Vehicle Model (`auto_sales_data.vehicle_models`)**:
   - Canonical vehicle platform defined by `model_id`, `model`, `vehicle_type` (`SUV`, `Truck`, `Sedan`, `EV`), `base_price`, and assembly `plant_id`.
   - Active production vehicle models sold and serviced in the fleet are identified via `INNER JOIN` to operational sales/ownership tables (`vehicle_sales`, `vehicle_ownership`).

3. **Sold & Entitled Vehicle (`auto_sales_data.vehicle_sales` <-> `auto_aftersales_data.vehicle_ownership`)**:
   - Uniquely identified across the enterprise by **VIN (`vin`)** (`1:1` grain across `vehicle_sales` and `vehicle_ownership`).
   - **Warranty Entitlement State Machine**:
     - `ownership_status = 'Active'`: Full factory and extended warranty entitlement while `warranty_end_date >= CURRENT_DATE()`.
     - `ownership_status = 'Transferred'`: Secondary-market resale. Standard factory coverage terminates upon resale UNLESS `extended_warranty_purchased = TRUE`.
     - `ownership_status = 'Buyback'`: Lemon-law or manufacturer buyback. Permanently excluded from active customer warranty entitlement cohorts.
     - **True Active Warranty Entitlement Fleet**: `warranty_end_date >= CURRENT_DATE() AND (ownership_status = 'Active' OR (ownership_status = 'Transferred' AND extended_warranty_purchased = TRUE))`.

4. **Dealership Service Event (`auto_aftersales_data.service_orders`)**:
   - Repair, maintenance, or recall visit at an authorized dealership (`dealership`, `vin`, `technician_id`).
   - **Warranty Absorption Classification**: Any service order with `is_warranty_covered = TRUE` (across `service_type IN ('Warranty Repair', 'Repair', 'Recall Service')`) is absorbed by the OEM (`customer_paid_amount = 0.0`) and generates a corresponding `warranty_claims` record (`1:1` on `service_order_id`).

5. **Component Replacement (`auto_aftersales_data.service_parts_usage`)**:
   - Line-item parts (`part_name`, `part_source_plant_name`, `quantity_used`, `unit_cost`, `extended_cost`) installed during a `service_order_id`.
   - Tracks physical return of defective cores via `defective_part_returned` (`BOOL`), which governs supplier chargeback recovery eligibility.

6. **Warranty Claim & Supplier Recovery (`auto_aftersales_data.warranty_claims`)**:
   - Financial adjudication record (`claim_id`, `service_order_id`, `vin`, `claim_status`, `claim_amount`, `supplier_fault`).
   - Adjudication states: `'Approved'` (realized ledger cost), `'Pending'` and `'Under Review'` (open reserve exposure), `'Denied'` (rejected, `$0` OEM liability).
