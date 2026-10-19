# Automotive Enterprise Domain Ontology (Manufacturing -> Sales -> After-Sales)

## Core Domain Entities & Lifecycle Hierarchy

1. **Manufacturing Plant (`auto_manufacturing_data.plants`)**:
   - Physical assembly or component-stamping facility identified by `plant_id` and `plant_name`.
   - **Critical Dual-Role Relationship**: A plant can act as the **Vehicle Final Assembly Plant** (`warranty_claims.build_plant_name`, `vehicle_models.plant_id`) OR as the **Component Source Plant** (`warranty_claims.part_source_plant_name`, `parts_inventory.source_plant_id`).
   - Only **7 facilities** are active operational plants in the enterprise fleet; the remaining 252 rows in `plants` are unallocated global facility codes.

2. **Vehicle Model (`auto_sales_data.vehicle_models`)**:
   - Canonical vehicle platform defined by `model_id`, `model_name`, `category` (`SUV`, `Truck`, `Sedan`, `EV`), `msrp`, and primary assembly `plant_id`.
   - Only **8 vehicle models** (`model_id` 1 through 8) represent active production vehicles sold and serviced in the fleet.

3. **Sold & Entitled Vehicle (`auto_sales_data.vehicle_sales` <-> `auto_aftersales_data.vehicle_ownership`)**:
   - Uniquely identified across the enterprise by **VIN (`vin`)** (1:1 grain across `vehicle_sales` and `vehicle_ownership`, 5,000 vehicles).
   - **Warranty Entitlement State Machine**:
     - `ownership_status = 'Active'` (4,582 vehicles): Full factory and extended warranty entitlement.
     - `ownership_status = 'Transferred'` (304 vehicles): Secondary-market resale. Standard factory coverage terminates upon resale UNLESS `extended_warranty_purchased = TRUE` (68 vehicles retain transferable coverage; 236 lose coverage).
     - `ownership_status = 'Buyback'` (114 vehicles): Lemon-law or manufacturer buyback. Excluded from active customer warranty entitlement cohorts.
     - **True Active Warranty Entitlement Fleet** = `4,582 + 68 = 4,650` vehicles.

4. **Dealership Service Event (`auto_aftersales_data.service_orders`)**:
   - Repair, maintenance, or recall visit at an authorized dealership (`dealership_id`, `vin`, `technician_id`).
   - **Warranty Absorption Classification**: Any service order with `is_warranty_covered = TRUE` (1,894 orders across `service_type IN ('Warranty Repair', 'Repair', 'Recall Service')`) is absorbed by the OEM (`customer_paid_amount = 0.0`) and generates a corresponding `warranty_claims` record (`1:1` on `service_order_id`).

5. **Component Replacement (`auto_aftersales_data.service_parts_usage`)**:
   - Line-item parts (`part_number`, `part_name`, `part_category`, `quantity_used`, `unit_cost`, `total_part_cost`) installed during a `service_order_id`.
   - Tracks physical return of defective cores via `defective_part_returned` (`BOOL`), which governs supplier chargeback recovery eligibility.

6. **Warranty Claim & Supplier Recovery (`auto_aftersales_data.warranty_claims`)**:
   - Financial adjudication record (`claim_id`, `service_order_id`, `vin`, `claim_status`, `claim_amount`, `supplier_fault`).
   - Adjudication states: `'Approved'` (realized ledger cost), `'Pending'` and `'Under Review'` (open reserve exposure), `'Denied'` (rejected, zero OEM liability).
