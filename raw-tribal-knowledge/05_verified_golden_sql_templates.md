# Verified Golden SQL Templates (`sa-demo-agentic`)

## Query 1: Net OEM Warranty Burden & Unrecovered Supplier Chargeback Leakage by Failure Component
```sql
WITH parts_by_order AS (
  SELECT
    service_order_id,
    COUNT(*) AS part_line_items,
    SUM(total_part_cost) AS total_replaced_parts_cost,
    LOGICAL_AND(defective_part_returned) AS all_defective_parts_returned
  FROM `sa-demo-agentic.auto_aftersales_data.service_parts_usage`
  GROUP BY service_order_id
)
SELECT
  w.failure_component,
  COUNT(w.claim_id) AS total_claims_submitted,
  COUNTIF(w.claim_status = 'Approved') AS approved_claims,
  ROUND(SUM(w.claim_amount), 2) AS gross_submitted_claim_amount,
  ROUND(SUM(CASE WHEN w.claim_status = 'Approved' THEN w.claim_amount ELSE 0 END), 2) AS realized_warranty_cost,
  ROUND(SUM(CASE
    WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = TRUE
    THEN w.claim_amount * 0.70 ELSE 0 END), 2) AS recoverable_supplier_chargeback,
  ROUND(SUM(CASE
    WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = FALSE
    THEN w.claim_amount * 0.70 ELSE 0 END), 2) AS unrecovered_supplier_leakage,
  ROUND(
    SUM(CASE WHEN w.claim_status = 'Approved' THEN w.claim_amount ELSE 0 END) -
    SUM(CASE
      WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = TRUE
      THEN w.claim_amount * 0.70 ELSE 0 END),
    2
  ) AS net_oem_warranty_burden
FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims` w
LEFT JOIN parts_by_order p
  ON w.service_order_id = p.service_order_id
GROUP BY w.failure_component
ORDER BY net_oem_warranty_burden DESC;
```

## Query 2: Active Fleet Warranty Entitlement & Claim Frequency by Vehicle Model
```sql
WITH entitled_fleet AS (
  SELECT
    vo.vin,
    vo.model_id,
    vo.ownership_status,
    vo.extended_warranty_purchased,
    CASE
      WHEN vo.warranty_end_date >= CURRENT_DATE()
       AND (vo.ownership_status = 'Active'
            OR (vo.ownership_status = 'Transferred' AND vo.extended_warranty_purchased = TRUE))
      THEN TRUE
      ELSE FALSE
    END AS is_warranty_entitled
  FROM `sa-demo-agentic.auto_aftersales_data.vehicle_ownership` vo
),
approved_claims_by_vin AS (
  SELECT
    vin,
    COUNT(claim_id) AS approved_claim_count,
    SUM(claim_amount) AS approved_claim_spend
  FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims`
  WHERE claim_status = 'Approved'
  GROUP BY vin
)
SELECT
  vm.model_id,
  vm.model_name,
  vm.category,
  COUNT(ef.vin) AS total_sold_fleet,
  COUNTIF(ef.is_warranty_entitled) AS active_entitled_fleet,
  SUM(COALESCE(ac.approved_claim_count, 0)) AS total_approved_claims,
  ROUND(SUM(COALESCE(ac.approved_claim_spend, 0)), 2) AS realized_warranty_spend,
  ROUND(SAFE_DIVIDE(SUM(COALESCE(ac.approved_claim_spend, 0)), COUNTIF(ef.is_warranty_entitled)), 2) AS realized_warranty_cost_per_entitled_vehicle
FROM `sa-demo-agentic.auto_sales_data.vehicle_models` vm
INNER JOIN entitled_fleet ef
  ON vm.model_id = ef.model_id
LEFT JOIN approved_claims_by_vin ac
  ON ef.vin = ac.vin
GROUP BY vm.model_id, vm.model_name, vm.category
ORDER BY realized_warranty_spend DESC;
```

## Query 3: Final Assembly Plant vs Component Source Plant Quality Scorecard
```sql
WITH active_plants AS (
  SELECT DISTINCT p.plant_id, p.plant_name, p.location, p.capacity
  FROM `sa-demo-agentic.auto_manufacturing_data.plants` p
  INNER JOIN `sa-demo-agentic.auto_manufacturing_data.assembly_line_status` als
    ON p.plant_name = als.plant_name
),
assembly_claims AS (
  SELECT
    build_plant_name AS plant_name,
    COUNTIF(claim_status = 'Approved' AND supplier_fault = FALSE) AS approved_assembly_fault_claims,
    ROUND(SUM(CASE WHEN claim_status = 'Approved' AND supplier_fault = FALSE THEN claim_amount ELSE 0 END), 2) AS assembly_fault_warranty_cost
  FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims`
  GROUP BY build_plant_name
),
component_claims AS (
  SELECT
    part_source_plant_name AS plant_name,
    COUNTIF(claim_status = 'Approved' AND supplier_fault = TRUE) AS approved_component_fault_claims,
    ROUND(SUM(CASE WHEN claim_status = 'Approved' AND supplier_fault = TRUE THEN claim_amount ELSE 0 END), 2) AS component_fault_warranty_cost
  FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims`
  GROUP BY part_source_plant_name
)
SELECT
  ap.plant_id,
  ap.plant_name,
  ap.location,
  ap.capacity,
  COALESCE(ac.approved_assembly_fault_claims, 0) AS approved_assembly_fault_claims,
  COALESCE(ac.assembly_fault_warranty_cost, 0.0) AS assembly_fault_warranty_cost,
  COALESCE(cc.approved_component_fault_claims, 0) AS approved_component_fault_claims,
  COALESCE(cc.component_fault_warranty_cost, 0.0) AS component_fault_warranty_cost
FROM active_plants ap
LEFT JOIN assembly_claims ac USING (plant_name)
LEFT JOIN component_claims cc USING (plant_name)
ORDER BY assembly_fault_warranty_cost DESC;
```
