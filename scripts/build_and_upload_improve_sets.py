#!/usr/bin/env python3
"""Generates and uploads the Evaluation Set and Curation Set JSONL files for Knowledge Studio's 'Improve' step.

Validates against both:
1. Frontend UI parser: //cloud/console/web/knowledgeagent/enrichment/enrichment_wizard/step_improve/eval_file_parser.ts
2. Backend EMS & Curation Loop builders:
   - //cloud/dataplex/context_success/agents/enrichment/curation_loop/ems/eval_set_builder.py
   - //cloud/dataplex/context_success/agents/enrichment/curation_loop/benchmark_from_dataset.py
"""

import json
from pathlib import Path
import subprocess
import urllib.error
import urllib.parse
import urllib.request

PROJECT_ID = "sa-demo-agentic"
LOCATION = "us-central1"
BUCKET_NAME = "sa-demo-agentic-okf-context"
BASE_DIR = Path("/usr/local/google/home/asudesh/ace/okf-knowledge-catalog-demo")
IMPROVE_DIR = BASE_DIR / "improve-sets"


def get_token() -> str:
  return subprocess.check_output(
      ["gcloud", "auth", "print-access-token"], text=True
  ).strip()


def api_call(method: str, url: str, token: str, body: bytes | None = None, content_type: str = "application/json") -> tuple[int, dict]:
  headers = {
      "Authorization": f"Bearer {token}",
      "x-goog-user-project": PROJECT_ID,
      "Content-Type": content_type,
  }
  req = urllib.request.Request(url, data=body, headers=headers, method=method)
  try:
    with urllib.request.urlopen(req, timeout=30) as resp:
      raw = resp.read().decode("utf-8")
      return resp.status, json.loads(raw) if raw else {}
  except urllib.error.HTTPError as e:
    raw = e.read().decode("utf-8", errors="replace")
    try:
      return e.code, json.loads(raw)
    except Exception:
      return e.code, {"raw": raw}


def build_curation_set_items() -> list[dict]:
  """Builds the Curation Set (enrichment_dataset_uri) for hill-climbing the Enrichment Agent."""
  return [
      {
          "display_name": "C01 Realized Warranty Cost vs Gross Submitted Claims",
          "evaluation_item_type": "REQUEST",
          "evaluation_request": {
              "prompt": {
                  "text": "What is our total realized warranty cost compared to open reserve exposure and denied claims across all failure components?"
              },
              "golden_response": {
                  "candidate": "golden",
                  "text": (
                      "SELECT failure_component, "
                      "ROUND(SUM(CASE WHEN claim_status = 'Approved' THEN claim_amount ELSE 0 END), 2) AS realized_warranty_cost, "
                      "ROUND(SUM(CASE WHEN claim_status IN ('Pending', 'Under Review') THEN claim_amount ELSE 0 END), 2) AS open_reserve_exposure, "
                      "ROUND(SUM(CASE WHEN claim_status = 'Denied' THEN claim_amount ELSE 0 END), 2) AS denied_claim_amount "
                      "FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims` "
                      "GROUP BY failure_component "
                      "ORDER BY realized_warranty_cost DESC"
                  ),
              },
              "rubrics": {
                  "sql_gate": {
                      "rubrics": [
                          {
                              "type": "SQL_ACCURACY",
                              "importance": "HIGH",
                              "content": {
                                  "property": {
                                      "description": "Must filter claim_status = 'Approved' ($1,254,786.01 total) for realized warranty cost and separate 'Pending'/'Under Review' ($404,016.42) as open reserve exposure while excluding 'Denied' ($139,504.47)."
                                  }
                              },
                          }
                      ]
                  }
              },
          },
          "metadata": {
              "case_id": "C01",
              "tables": ["sa-demo-agentic.auto_aftersales_data.warranty_claims"],
              "sql_notes": [
                  "Raw SUM(claim_amount) ($1,798,306.90) overstates realized warranty cost because it includes Pending, Under Review, and Denied claims."
              ],
          },
      },
      {
          "display_name": "C02 Net OEM Warranty Burden & Supplier Core-Return Leakage",
          "evaluation_item_type": "REQUEST",
          "evaluation_request": {
              "prompt": {
                  "text": "Calculate our Recoverable Supplier Chargeback, Unrecovered Supplier Leakage from unreturned defective parts, and Net OEM Warranty Burden."
              },
              "golden_response": {
                  "candidate": "golden",
                  "text": (
                      "WITH parts_by_order AS ("
                      "  SELECT service_order_id, LOGICAL_AND(defective_part_returned) AS all_defective_parts_returned "
                      "  FROM `sa-demo-agentic.auto_aftersales_data.service_parts_usage` "
                      "  GROUP BY service_order_id"
                      ") "
                      "SELECT "
                      "ROUND(SUM(CASE WHEN w.claim_status = 'Approved' THEN w.claim_amount ELSE 0 END), 2) AS realized_warranty_cost, "
                      "ROUND(SUM(CASE WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = TRUE THEN w.claim_amount * 0.70 ELSE 0 END), 2) AS recoverable_supplier_chargeback, "
                      "ROUND(SUM(CASE WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = FALSE THEN w.claim_amount * 0.70 ELSE 0 END), 2) AS unrecovered_supplier_leakage, "
                      "ROUND(SUM(CASE WHEN w.claim_status = 'Approved' THEN w.claim_amount ELSE 0 END) - SUM(CASE WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = TRUE THEN w.claim_amount * 0.70 ELSE 0 END), 2) AS net_oem_warranty_burden "
                      "FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims` w "
                      "LEFT JOIN parts_by_order p USING (service_order_id)"
                  ),
              },
              "rubrics": {
                  "sql_gate": {
                      "rubrics": [
                          {
                              "type": "SQL_ACCURACY",
                              "importance": "HIGH",
                              "content": {
                                  "property": {
                                      "description": "Must pre-aggregate service_parts_usage by service_order_id using LOGICAL_AND(defective_part_returned) to prevent 1.78x join fan-out, and apply 70% supplier recovery only on Approved supplier_fault=TRUE claims where all defective parts were returned."
                                  }
                              },
                          }
                      ]
                  }
              },
          },
          "metadata": {
              "case_id": "C02",
              "tables": [
                  "sa-demo-agentic.auto_aftersales_data.warranty_claims",
                  "sa-demo-agentic.auto_aftersales_data.service_parts_usage",
              ],
              "sql_notes": [
                  "Never join warranty_claims directly to service_parts_usage without pre-aggregating service_parts_usage to service_order_id grain."
              ],
          },
      },
      {
          "display_name": "C03 Total Dealership Service Cost Absorbed Under Warranty",
          "evaluation_item_type": "REQUEST",
          "evaluation_request": {
              "prompt": {
                  "text": "How much total service order cost was absorbed by the OEM under warranty across our dealerships, broken down by service type?"
              },
              "golden_response": {
                  "candidate": "golden",
                  "text": (
                      "SELECT service_type, COUNT(*) AS covered_orders, "
                      "ROUND(SUM(total_cost - customer_paid_amount), 2) AS oem_absorbed_warranty_cost "
                      "FROM `sa-demo-agentic.auto_aftersales_data.service_orders` "
                      "WHERE is_warranty_covered = TRUE "
                      "GROUP BY service_type "
                      "ORDER BY oem_absorbed_warranty_cost DESC"
                  ),
              },
              "rubrics": {
                  "sql_gate": {
                      "rubrics": [
                          {
                              "type": "SQL_ACCURACY",
                              "importance": "HIGH",
                              "content": {
                                  "property": {
                                      "description": "Must filter WHERE is_warranty_covered = TRUE ($1,591,386.85 across 1,894 orders) rather than WHERE service_type = 'Warranty Repair' ($826,977.80), which misses 690 covered Repair orders and 282 covered Recall Service orders."
                                  }
                              },
                          }
                      ]
                  }
              },
          },
          "metadata": {
              "case_id": "C03",
              "tables": ["sa-demo-agentic.auto_aftersales_data.service_orders"],
              "sql_notes": [
                  "Use is_warranty_covered = TRUE to capture all 1,894 warranty-absorbed service visits ($1,591,386.85)."
              ],
          },
      },
      {
          "display_name": "C04 Active Fleet Entitled to OEM Warranty Coverage",
          "evaluation_item_type": "REQUEST",
          "evaluation_request": {
              "prompt": {
                  "text": "How many vehicles in our fleet are currently entitled to OEM warranty coverage under our secondary-market transfer rules?"
              },
              "golden_response": {
                  "candidate": "golden",
                  "text": (
                      "SELECT "
                      "COUNTIF(warranty_end_date >= CURRENT_DATE() AND (ownership_status = 'Active' OR (ownership_status = 'Transferred' AND extended_warranty_purchased = TRUE))) AS active_warranty_entitled_fleet, "
                      "COUNTIF(ownership_status = 'Active') AS active_original_owners, "
                      "COUNTIF(ownership_status = 'Transferred' AND extended_warranty_purchased = TRUE) AS transferred_with_extended_warranty, "
                      "COUNTIF(ownership_status = 'Transferred' AND extended_warranty_purchased = FALSE) AS transferred_unentitled_excluded, "
                      "COUNTIF(ownership_status = 'Buyback') AS buyback_excluded "
                      "FROM `sa-demo-agentic.auto_aftersales_data.vehicle_ownership`"
                  ),
              },
              "rubrics": {
                  "sql_gate": {
                      "rubrics": [
                          {
                              "type": "SQL_ACCURACY",
                              "importance": "HIGH",
                              "content": {
                                  "property": {
                                      "description": "Must include Active vehicles (4,582) plus Transferred vehicles with extended_warranty_purchased = TRUE (68) for a total of 4,650 entitled vehicles, while excluding Buyback (114) and Transferred without extended warranty (236)."
                                  }
                              },
                          }
                      ]
                  }
              },
          },
          "metadata": {
              "case_id": "C04",
              "tables": ["sa-demo-agentic.auto_aftersales_data.vehicle_ownership"],
              "sql_notes": [
                  "Standard warranty does not transfer on resale unless extended_warranty_purchased = TRUE."
              ],
          },
      },
      {
          "display_name": "C05 Active Manufacturing Plants vs 259-Row Catalog Padding",
          "evaluation_item_type": "REQUEST",
          "evaluation_request": {
              "prompt": {
                  "text": "List our active manufacturing plants, their capacity, and their approved OEM assembly-fault warranty cost vs component-source supplier-fault cost."
              },
              "golden_response": {
                  "candidate": "golden",
                  "text": (
                      "WITH active_plants AS ("
                      "  SELECT DISTINCT p.plant_id, p.plant_name, p.location, p.capacity "
                      "  FROM `sa-demo-agentic.auto_manufacturing_data.plants` p "
                      "  INNER JOIN `sa-demo-agentic.auto_manufacturing_data.assembly_line_status` als "
                      "    ON p.plant_name = als.plant_name"
                      "), "
                      "assembly_claims AS ("
                      "  SELECT build_plant_name AS plant_name, "
                      "  ROUND(SUM(CASE WHEN claim_status = 'Approved' AND supplier_fault = FALSE THEN claim_amount ELSE 0 END), 2) AS assembly_fault_warranty_cost "
                      "  FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims` GROUP BY build_plant_name"
                      "), "
                      "component_claims AS ("
                      "  SELECT part_source_plant_name AS plant_name, "
                      "  ROUND(SUM(CASE WHEN claim_status = 'Approved' AND supplier_fault = TRUE THEN claim_amount ELSE 0 END), 2) AS component_fault_warranty_cost "
                      "  FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims` GROUP BY part_source_plant_name"
                      ") "
                      "SELECT ap.plant_id, ap.plant_name, ap.location, ap.capacity, "
                      "COALESCE(ac.assembly_fault_warranty_cost, 0) AS assembly_fault_warranty_cost, "
                      "COALESCE(cc.component_fault_warranty_cost, 0) AS component_fault_warranty_cost "
                      "FROM active_plants ap "
                      "LEFT JOIN assembly_claims ac USING (plant_name) "
                      "LEFT JOIN component_claims cc USING (plant_name) "
                      "ORDER BY assembly_fault_warranty_cost DESC"
                  ),
              },
              "rubrics": {
                  "sql_gate": {
                      "rubrics": [
                          {
                              "type": "SQL_ACCURACY",
                              "importance": "HIGH",
                              "content": {
                                  "property": {
                                      "description": "Must filter out the 252 padded placeholder rows in auto_manufacturing_data.plants by joining to assembly_line_status (leaving 7 active plants), and distinguish build_plant_name (assembly fault) from part_source_plant_name (supplier component fault)."
                                  }
                              },
                          }
                      ]
                  }
              },
          },
          "metadata": {
              "case_id": "C05",
              "tables": [
                  "sa-demo-agentic.auto_manufacturing_data.plants",
                  "sa-demo-agentic.auto_manufacturing_data.assembly_line_status",
                  "sa-demo-agentic.auto_aftersales_data.warranty_claims",
              ],
              "sql_notes": [
                  "plants, vehicle_models, and dealerships contain 259 rows where 251-252 rows are inactive ERP catalog padding."
              ],
          },
      },
  ]


def build_evaluation_set_items() -> list[dict]:
  """Builds the held-out End-to-End Evaluation Set (evaluation_dataset_uri).

  Note: Kept normalized (no top-level `name` and no `evaluation_request.rubrics`)
  so `eval_set_builder.py` can use the fast bulk `ImportEvaluationSet` LRO path
  AND the UI `eval_file_parser.ts` renders the live preview table.
  """
  return [
      {
          "display_name": "E01 Net OEM Warranty Burden & Supplier Leakage by Component",
          "evaluation_item_type": "REQUEST",
          "evaluation_request": {
              "prompt": {
                  "text": "For each failure component, report our Realized Warranty Cost, 70% Recoverable Supplier Chargeback (requiring all replaced defective parts returned), Unrecovered Supplier Leakage, and Net OEM Warranty Burden."
              },
              "golden_response": {
                  "candidate": "golden",
                  "text": (
                      "WITH parts_by_order AS ("
                      "  SELECT service_order_id, LOGICAL_AND(defective_part_returned) AS all_defective_parts_returned "
                      "  FROM `sa-demo-agentic.auto_aftersales_data.service_parts_usage` "
                      "  GROUP BY service_order_id"
                      ") "
                      "SELECT w.failure_component, "
                      "COUNTIF(w.claim_status = 'Approved') AS approved_claims, "
                      "ROUND(SUM(CASE WHEN w.claim_status = 'Approved' THEN w.claim_amount ELSE 0 END), 2) AS realized_warranty_cost, "
                      "ROUND(SUM(CASE WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = TRUE THEN w.claim_amount * 0.70 ELSE 0 END), 2) AS recoverable_supplier_chargeback, "
                      "ROUND(SUM(CASE WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = FALSE THEN w.claim_amount * 0.70 ELSE 0 END), 2) AS unrecovered_supplier_leakage, "
                      "ROUND(SUM(CASE WHEN w.claim_status = 'Approved' THEN w.claim_amount ELSE 0 END) - SUM(CASE WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = TRUE THEN w.claim_amount * 0.70 ELSE 0 END), 2) AS net_oem_warranty_burden "
                      "FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims` w "
                      "LEFT JOIN parts_by_order p USING (service_order_id) "
                      "GROUP BY w.failure_component "
                      "ORDER BY net_oem_warranty_burden DESC"
                  ),
              },
          },
          "metadata": {
              "case_id": "E01",
              "tables": [
                  "sa-demo-agentic.auto_aftersales_data.warranty_claims",
                  "sa-demo-agentic.auto_aftersales_data.service_parts_usage",
              ],
          },
      },
      {
          "display_name": "E02 Realized Warranty Spend per Entitled Vehicle by Active Model",
          "evaluation_item_type": "REQUEST",
          "evaluation_request": {
              "prompt": {
                  "text": "Across our 8 active vehicle models, what is the Active Warranty Entitled Fleet size, total Realized Warranty Cost, and Realized Warranty Cost per Entitled Vehicle?"
              },
              "golden_response": {
                  "candidate": "golden",
                  "text": (
                      "WITH entitled_fleet AS ("
                      "  SELECT vin, model_id, "
                      "  (warranty_end_date >= CURRENT_DATE() AND (ownership_status = 'Active' OR (ownership_status = 'Transferred' AND extended_warranty_purchased = TRUE))) AS is_entitled "
                      "  FROM `sa-demo-agentic.auto_aftersales_data.vehicle_ownership`"
                      "), "
                      "approved_claims AS ("
                      "  SELECT vin, SUM(claim_amount) AS approved_spend "
                      "  FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims` "
                      "  WHERE claim_status = 'Approved' GROUP BY vin"
                      ") "
                      "SELECT vm.model_id, vm.model_name, vm.category, "
                      "COUNTIF(ef.is_entitled) AS active_entitled_fleet, "
                      "ROUND(SUM(COALESCE(ac.approved_spend, 0)), 2) AS realized_warranty_spend, "
                      "ROUND(SAFE_DIVIDE(SUM(COALESCE(ac.approved_spend, 0)), COUNTIF(ef.is_entitled)), 2) AS realized_warranty_cost_per_entitled_vehicle "
                      "FROM `sa-demo-agentic.auto_sales_data.vehicle_models` vm "
                      "INNER JOIN entitled_fleet ef ON vm.model_id = ef.model_id "
                      "LEFT JOIN approved_claims ac ON ef.vin = ac.vin "
                      "GROUP BY vm.model_id, vm.model_name, vm.category "
                      "ORDER BY realized_warranty_spend DESC"
                  ),
              },
          },
          "metadata": {
              "case_id": "E02",
              "tables": [
                  "sa-demo-agentic.auto_sales_data.vehicle_models",
                  "sa-demo-agentic.auto_aftersales_data.vehicle_ownership",
                  "sa-demo-agentic.auto_aftersales_data.warranty_claims",
              ],
          },
      },
      {
          "display_name": "E03 Dealership OEM Warranty Absorption & Unreturned Core Leakage",
          "evaluation_item_type": "REQUEST",
          "evaluation_request": {
              "prompt": {
                  "text": "For our 8 active dealerships, show total OEM warranty-absorbed service cost (including covered Repair and Recall Service orders) and total Unrecovered Supplier Leakage from unreturned defective parts."
              },
              "golden_response": {
                  "candidate": "golden",
                  "text": (
                      "WITH parts_by_order AS ("
                      "  SELECT service_order_id, LOGICAL_AND(defective_part_returned) AS all_defective_parts_returned "
                      "  FROM `sa-demo-agentic.auto_aftersales_data.service_parts_usage` "
                      "  GROUP BY service_order_id"
                      "), "
                      "order_metrics AS ("
                      "  SELECT so.dealership_id, "
                      "  COUNTIF(so.is_warranty_covered) AS warranty_covered_orders, "
                      "  ROUND(SUM(CASE WHEN so.is_warranty_covered THEN so.total_cost - so.customer_paid_amount ELSE 0 END), 2) AS oem_absorbed_service_cost, "
                      "  ROUND(SUM(CASE WHEN w.claim_status = 'Approved' AND w.supplier_fault = TRUE AND COALESCE(p.all_defective_parts_returned, FALSE) = FALSE THEN w.claim_amount * 0.70 ELSE 0 END), 2) AS unrecovered_supplier_leakage "
                      "  FROM `sa-demo-agentic.auto_aftersales_data.service_orders` so "
                      "  LEFT JOIN `sa-demo-agentic.auto_aftersales_data.warranty_claims` w USING (service_order_id) "
                      "  LEFT JOIN parts_by_order p USING (service_order_id) "
                      "  GROUP BY so.dealership_id"
                      ") "
                      "SELECT d.dealership_id, d.dealership_name, d.region, d.state, "
                      "om.warranty_covered_orders, om.oem_absorbed_service_cost, om.unrecovered_supplier_leakage "
                      "FROM `sa-demo-agentic.auto_sales_data.dealerships` d "
                      "INNER JOIN order_metrics om USING (dealership_id) "
                      "ORDER BY om.unrecovered_supplier_leakage DESC"
                  ),
              },
          },
          "metadata": {
              "case_id": "E03",
              "tables": [
                  "sa-demo-agentic.auto_sales_data.dealerships",
                  "sa-demo-agentic.auto_aftersales_data.service_orders",
                  "sa-demo-agentic.auto_aftersales_data.warranty_claims",
                  "sa-demo-agentic.auto_aftersales_data.service_parts_usage",
              ],
          },
      },
      {
          "display_name": "E04 Assembly Plant vs Component Source Plant Approved Warranty Cost",
          "evaluation_item_type": "REQUEST",
          "evaluation_request": {
              "prompt": {
                  "text": "Across our 7 active manufacturing plants, compare Approved OEM assembly-fault warranty cost (by build_plant_name) against Approved supplier-fault warranty cost (by part_source_plant_name)."
              },
              "golden_response": {
                  "candidate": "golden",
                  "text": (
                      "WITH active_plants AS ("
                      "  SELECT DISTINCT p.plant_id, p.plant_name, p.location, p.capacity "
                      "  FROM `sa-demo-agentic.auto_manufacturing_data.plants` p "
                      "  INNER JOIN `sa-demo-agentic.auto_manufacturing_data.assembly_line_status` als "
                      "    ON p.plant_name = als.plant_name"
                      "), "
                      "assembly_claims AS ("
                      "  SELECT build_plant_name AS plant_name, "
                      "  COUNTIF(claim_status = 'Approved' AND supplier_fault = FALSE) AS approved_assembly_claims, "
                      "  ROUND(SUM(CASE WHEN claim_status = 'Approved' AND supplier_fault = FALSE THEN claim_amount ELSE 0 END), 2) AS assembly_fault_cost "
                      "  FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims` GROUP BY build_plant_name"
                      "), "
                      "component_claims AS ("
                      "  SELECT part_source_plant_name AS plant_name, "
                      "  COUNTIF(claim_status = 'Approved' AND supplier_fault = TRUE) AS approved_component_claims, "
                      "  ROUND(SUM(CASE WHEN claim_status = 'Approved' AND supplier_fault = TRUE THEN claim_amount ELSE 0 END), 2) AS component_fault_cost "
                      "  FROM `sa-demo-agentic.auto_aftersales_data.warranty_claims` GROUP BY part_source_plant_name"
                      ") "
                      "SELECT ap.plant_id, ap.plant_name, ap.location, ap.capacity, "
                      "COALESCE(ac.approved_assembly_claims, 0) AS approved_assembly_claims, "
                      "COALESCE(ac.assembly_fault_cost, 0) AS assembly_fault_cost, "
                      "COALESCE(cc.approved_component_claims, 0) AS approved_component_claims, "
                      "COALESCE(cc.component_fault_cost, 0) AS component_fault_cost "
                      "FROM active_plants ap "
                      "LEFT JOIN assembly_claims ac USING (plant_name) "
                      "LEFT JOIN component_claims cc USING (plant_name) "
                      "ORDER BY assembly_fault_cost DESC"
                  ),
              },
          },
          "metadata": {
              "case_id": "E04",
              "tables": [
                  "sa-demo-agentic.auto_manufacturing_data.plants",
                  "sa-demo-agentic.auto_manufacturing_data.assembly_line_status",
                  "sa-demo-agentic.auto_aftersales_data.warranty_claims",
              ],
          },
      },
  ]


def ensure_gcs_bucket_and_upload(token: str, eval_path: Path, cur_path: Path) -> None:
  """Ensures gs://sa-demo-agentic-okf-context exists in sa-demo-agentic and uploads the JSONL files."""
  st, _ = api_call("GET", f"https://storage.googleapis.com/storage/v1/b/{BUCKET_NAME}", token)
  if st == 404:
    st_c, res_c = api_call(
        "POST",
        f"https://storage.googleapis.com/storage/v1/b?project={PROJECT_ID}",
        token,
        json.dumps({"name": BUCKET_NAME, "location": LOCATION}).encode("utf-8"),
    )
    print(f"Created bucket gs://{BUCKET_NAME}: status={st_c}")
  else:
    print(f"Bucket gs://{BUCKET_NAME} exists (status={st})")

  uploads = [
      ("improve/auto_aftersales_evaluation_set.jsonl", eval_path.read_bytes(), "application/jsonl"),
      ("improve/auto_aftersales_curation_set.jsonl", cur_path.read_bytes(), "application/jsonl"),
      ("evaluation.jsonl", eval_path.read_bytes(), "application/jsonl"),
      ("curation.jsonl", cur_path.read_bytes(), "application/jsonl"),
  ]
  for md_file in sorted((BASE_DIR / "raw-tribal-knowledge").glob("*.md")):
    uploads.append((f"tribal-knowledge/{md_file.name}", md_file.read_bytes(), "text/markdown"))

  for obj_name, data, ctype in uploads:
    enc_name = urllib.parse.quote(obj_name, safe="")
    url = f"https://storage.googleapis.com/upload/storage/v1/b/{BUCKET_NAME}/o?uploadType=media&name={enc_name}"
    st_u, res_u = api_call("POST", url, token, data, content_type=ctype)
    print(f"  Uploaded gs://{BUCKET_NAME}/{obj_name} -> status={st_u} ({len(data)} bytes)")


def main():
  IMPROVE_DIR.mkdir(parents=True, exist_ok=True)
  eval_items = build_evaluation_set_items()
  cur_items = build_curation_set_items()

  eval_path = IMPROVE_DIR / "auto_aftersales_evaluation_set.jsonl"
  cur_path = IMPROVE_DIR / "auto_aftersales_curation_set.jsonl"

  eval_path.write_text(
      "\n".join(json.dumps(item, ensure_ascii=False) for item in eval_items) + "\n",
      encoding="utf-8",
  )
  cur_path.write_text(
      "\n".join(json.dumps(item, ensure_ascii=False) for item in cur_items) + "\n",
      encoding="utf-8",
  )
  print(f"Wrote {len(eval_items)} items to {eval_path}")
  print(f"Wrote {len(cur_items)} items to {cur_path}")

  token = get_token()
  ensure_gcs_bucket_and_upload(token, eval_path, cur_path)


if __name__ == "__main__":
  main()
