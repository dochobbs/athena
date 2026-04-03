#!/usr/bin/env python3
"""Migrate Oread conditions.yaml into Athena's per-condition YAML files.

Splits the monolithic conditions.yaml into individual files, adds specialty
metadata, and routes conditions to shared/ or peds/ based on cross-specialty
applicability.

Usage:
  python scripts/migrate_conditions.py [--dry-run]
"""
import sys
from pathlib import Path

import yaml

# Conditions that span both peds and adult medicine → go to shared/
# These will get specialty_variants added in a later step
SHARED_CONDITIONS = {
  "asthma",
  "anxiety_disorder",
  "depression",
  "obesity",
  "prediabetes",
  "urinary_tract_infection",
  "migraine",
  "obstructive_sleep_apnea",
  "epilepsy",
  "allergic_rhinitis",
  "iron_deficiency_anemia",
  "functional_constipation",
  "gerd",
  "eczema",
}

OREAD_CONDITIONS = Path(__file__).parent.parent.parent / "synpat" / "knowledge" / "conditions" / "conditions.yaml"
ATHENA_CONDITIONS = Path(__file__).parent.parent / "knowledge" / "conditions"


def transform_condition(key: str, data: dict) -> dict:
  """Add Athena-specific fields to an Oread condition."""
  result = {"id": key}

  # Copy display_name and aliases
  if "display_name" in data:
    result["display_name"] = data["display_name"]
  else:
    result["display_name"] = key.replace("_", " ").title()

  if "aliases" in data:
    result["aliases"] = data["aliases"]

  # Map billing_codes to flat fields
  if "billing_codes" in data:
    bc = data["billing_codes"]
    if "snomed" in bc:
      result["snomed"] = str(bc["snomed"])
    if "icd10" in bc:
      result["icd10"] = bc["icd10"]
  # Some conditions have icd10 at top level (mental health ones)
  if "icd10" in data and "icd10" not in result:
    result["icd10"] = data["icd10"]

  # Category and system
  if "category" in data:
    result["category"] = data["category"]
  if "system" in data:
    result["system"] = data["system"]

  # Specialty metadata
  is_shared = key in SHARED_CONDITIONS
  if is_shared:
    result["specialties"] = ["peds", "im"]
  else:
    result["specialties"] = ["peds"]

  # Age range
  age_range = {}
  if "demographics" in data and "age_months" in data["demographics"]:
    am = data["demographics"]["age_months"]
    if "min" in am:
      age_range["min_months"] = am["min"]
    if "max" in am:
      age_range["max_months"] = am["max"]
    if "peak" in am:
      age_range["peak"] = am["peak"]
  elif "age_ranges" in data:
    ar = data["age_ranges"]
    if "min_months" in ar:
      age_range["min_months"] = ar["min_months"]
    if "max_months" in ar:
      age_range["max_months"] = ar["max_months"]
  if age_range:
    result["age_range"] = age_range

  # Copy remaining clinical fields as-is (Oread-compatible)
  for field in [
    "demographics", "prevalence", "seasonality", "vitals_impact",
    "presentation", "diagnostics", "treatment", "comorbidities",
    "monitoring_requirements", "progression",
  ]:
    if field in data:
      result[field] = data[field]

  return result


def main():
  dry_run = "--dry-run" in sys.argv

  if not OREAD_CONDITIONS.exists():
    print(f"ERROR: Source not found: {OREAD_CONDITIONS}")
    sys.exit(1)

  with open(OREAD_CONDITIONS) as f:
    all_conditions = yaml.safe_load(f)

  # Remove metadata keys
  all_conditions.pop("_seasonal_weights", None)

  peds_dir = ATHENA_CONDITIONS / "peds"
  shared_dir = ATHENA_CONDITIONS / "shared"

  peds_count = 0
  shared_count = 0
  skipped = []

  for key, data in all_conditions.items():
    if not isinstance(data, dict):
      skipped.append(key)
      continue

    transformed = transform_condition(key, data)
    is_shared = key in SHARED_CONDITIONS
    target_dir = shared_dir if is_shared else peds_dir
    target_file = target_dir / f"{key}.yaml"

    if dry_run:
      pool = "shared" if is_shared else "peds"
      print(f"  [{pool}] {key} → {target_file.name}")
    else:
      target_dir.mkdir(parents=True, exist_ok=True)
      with open(target_file, "w") as f:
        yaml.dump(transformed, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    if is_shared:
      shared_count += 1
    else:
      peds_count += 1

  print(f"\nMigration {'(DRY RUN) ' if dry_run else ''}complete:")
  print(f"  Peds-only: {peds_count} conditions → {peds_dir}")
  print(f"  Shared:    {shared_count} conditions → {shared_dir}")
  print(f"  Total:     {peds_count + shared_count}")
  if skipped:
    print(f"  Skipped:   {skipped}")


if __name__ == "__main__":
  main()
