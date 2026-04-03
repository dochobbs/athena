#!/usr/bin/env python3
"""Migrate Echo teaching frameworks into Athena's knowledge directory.

Copies framework YAML files, adds specialties metadata, and routes to
shared/ or peds/ based on whether a matching condition exists in shared/.

Usage:
  python scripts/migrate_frameworks.py [--dry-run]
"""
import sys
from pathlib import Path

import yaml

ECHO_FRAMEWORKS = Path(__file__).parent.parent.parent / "echo" / "knowledge" / "frameworks"
ATHENA_FRAMEWORKS = Path(__file__).parent.parent / "knowledge" / "frameworks"
ATHENA_CONDITIONS_SHARED = Path(__file__).parent.parent / "knowledge" / "conditions" / "shared"


def get_shared_condition_ids() -> set[str]:
  """Get IDs of conditions in shared/ pool."""
  ids = set()
  if ATHENA_CONDITIONS_SHARED.exists():
    for f in ATHENA_CONDITIONS_SHARED.glob("*.yaml"):
      ids.add(f.stem)
  return ids


def main():
  dry_run = "--dry-run" in sys.argv

  if not ECHO_FRAMEWORKS.exists():
    print(f"ERROR: Source not found: {ECHO_FRAMEWORKS}")
    sys.exit(1)

  shared_conditions = get_shared_condition_ids()
  peds_dir = ATHENA_FRAMEWORKS / "peds"
  shared_dir = ATHENA_FRAMEWORKS / "shared"

  peds_count = 0
  shared_count = 0
  skipped = []

  for src_file in sorted(ECHO_FRAMEWORKS.glob("*.yaml")):
    # Skip schema/template files
    if src_file.stem.startswith("_"):
      skipped.append(src_file.stem)
      continue

    with open(src_file) as f:
      data = yaml.safe_load(f)

    if not isinstance(data, dict):
      skipped.append(src_file.stem)
      continue

    # Ensure id field
    if "id" not in data:
      data["id"] = src_file.stem

    # Determine pool: if matching shared condition exists, put in shared/
    framework_id = data["id"]
    # Also check topic-derived key
    topic_key = data.get("topic", "").lower().replace(" ", "_").replace("-", "_")

    is_shared = (
      framework_id in shared_conditions
      or topic_key in shared_conditions
    )

    # Add specialties if not present
    if "specialties" not in data:
      if is_shared:
        data["specialties"] = ["peds", "im"]
      else:
        data["specialties"] = ["peds"]

    target_dir = shared_dir if is_shared else peds_dir
    target_file = target_dir / src_file.name

    if dry_run:
      pool = "shared" if is_shared else "peds"
      print(f"  [{pool}] {src_file.stem}")
    else:
      target_dir.mkdir(parents=True, exist_ok=True)
      with open(target_file, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    if is_shared:
      shared_count += 1
    else:
      peds_count += 1

  print(f"\nFramework migration {'(DRY RUN) ' if dry_run else ''}complete:")
  print(f"  Peds-only: {peds_count} frameworks → {peds_dir}")
  print(f"  Shared:    {shared_count} frameworks → {shared_dir}")
  print(f"  Total:     {peds_count + shared_count}")
  if skipped:
    print(f"  Skipped:   {skipped}")


if __name__ == "__main__":
  main()
