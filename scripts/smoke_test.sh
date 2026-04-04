#!/bin/bash
#
# smoke_test.sh - Verify Athena is working correctly
#
# Usage: ./scripts/smoke_test.sh [port]
# Default port: 9105

set -e

PORT=${1:-9105}
BASE="http://localhost:$PORT"
PASS=0
FAIL=0

check() {
  local name="$1"
  local url="$2"
  local expected="$3"

  response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null)
  status=$(echo "$response" | tail -1)
  body=$(echo "$response" | head -1)

  if [ "$status" = "$expected" ]; then
    echo "  PASS  $name ($status)"
    PASS=$((PASS + 1))
  else
    echo "  FAIL  $name (got $status, expected $expected)"
    FAIL=$((FAIL + 1))
  fi
}

check_json_count() {
  local name="$1"
  local url="$2"
  local min_count="$3"

  body=$(curl -s "$url" 2>/dev/null)
  count=$(echo "$body" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null)

  if [ -n "$count" ] && [ "$count" -ge "$min_count" ]; then
    echo "  PASS  $name ($count items, min $min_count)"
    PASS=$((PASS + 1))
  else
    echo "  FAIL  $name (got ${count:-error}, expected >= $min_count)"
    FAIL=$((FAIL + 1))
  fi
}

echo "=================================="
echo "Athena Smoke Test — port $PORT"
echo "=================================="
echo ""

# Check if server is running
if ! curl -s "$BASE/api/health" > /dev/null 2>&1; then
  echo "ERROR: Athena not running on port $PORT"
  echo "Start with: PYTHONPATH=. uvicorn athena.src.main:app --port $PORT"
  exit 1
fi

echo "--- Health ---"
check "Health endpoint" "$BASE/api/health" "200"
check "Root endpoint" "$BASE/" "200"

echo ""
echo "--- Conditions ---"
check "All conditions" "$BASE/api/conditions" "200"
check_json_count "Total conditions" "$BASE/api/conditions" 200
check_json_count "Peds conditions" "$BASE/api/conditions?specialty=pediatrics" 40
check_json_count "IM conditions" "$BASE/api/conditions?specialty=internal_medicine" 170
check_json_count "FP conditions" "$BASE/api/conditions?specialty=family_practice" 200
check_json_count "FP 6-month-old" "$BASE/api/conditions?specialty=family_practice&age_months=6" 20
check_json_count "FP 30-year-old" "$BASE/api/conditions?specialty=family_practice&age_months=360" 130
check_json_count "IM cardiology" "$BASE/api/conditions?specialty=internal_medicine&system=cardiology" 15
check "Single condition (asthma)" "$BASE/api/conditions/asthma" "200"
check "Unknown condition (404)" "$BASE/api/conditions/nonexistent" "404"

echo ""
echo "--- Frameworks ---"
check "All frameworks" "$BASE/api/frameworks" "200"
check_json_count "Total frameworks" "$BASE/api/frameworks" 300
check_json_count "Peds frameworks" "$BASE/api/frameworks?specialty=pediatrics" 160
check_json_count "IM frameworks" "$BASE/api/frameworks?specialty=internal_medicine" 170
check "Framework for croup (peds)" "$BASE/api/frameworks/for-condition/croup?specialty=pediatrics" "200"
check "Croup NOT in IM (404)" "$BASE/api/frameworks/for-condition/croup?specialty=internal_medicine" "404"
check "CHF framework (IM)" "$BASE/api/frameworks/for-condition/chf_hfref?specialty=internal_medicine" "200"
check "Asthma shared (peds)" "$BASE/api/frameworks/for-condition/asthma?specialty=pediatrics" "200"
check "Asthma shared (IM)" "$BASE/api/frameworks/for-condition/asthma?specialty=internal_medicine" "200"

echo ""
echo "--- Specialties ---"
check_json_count "All specialties" "$BASE/api/specialties" 3
check "Pediatrics" "$BASE/api/specialties/pediatrics" "200"
check "Internal Medicine" "$BASE/api/specialties/internal_medicine" "200"
check "Family Practice" "$BASE/api/specialties/family_practice" "200"
check "Unknown specialty (404)" "$BASE/api/specialties/surgery" "404"

echo ""
echo "--- Learner Tracks ---"
check_json_count "All tracks" "$BASE/api/learner-tracks" 15
check_json_count "Peds residents" "$BASE/api/learner-tracks?specialty=pediatrics&level=resident" 3
check_json_count "IM students" "$BASE/api/learner-tracks?specialty=internal_medicine&level=student" 1

echo ""
echo "--- Disease Arcs ---"
check_json_count "All arcs" "$BASE/api/disease-arcs" 14
check_json_count "Peds arcs" "$BASE/api/disease-arcs?specialty=pediatrics" 6
check_json_count "IM arcs" "$BASE/api/disease-arcs?specialty=internal_medicine" 8
check_json_count "FP arcs" "$BASE/api/disease-arcs?specialty=family_practice" 14

echo ""
echo "--- Immunizations ---"
check "Immunizations endpoint" "$BASE/api/immunizations" "200"

echo ""
echo "=================================="
echo "Results: $PASS passed, $FAIL failed"
echo "=================================="

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
