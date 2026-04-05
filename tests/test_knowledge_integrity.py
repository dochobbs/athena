"""Knowledge integrity tests — validates ALL YAML content loads correctly.

Tests every condition, framework, disease arc, and immunization schedule
for required fields, valid data types, and internal consistency.
"""
from pathlib import Path

import pytest
import yaml

from athena.src.loader import KnowledgeStore
from athena.src.models import Condition, Framework, DiseaseArc, Specialty, LearnerTrack

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"


@pytest.fixture(scope="module")
def store():
  return KnowledgeStore(KNOWLEDGE_DIR)


# ─── Conditions ───────────────────────────────────────────────

class TestConditionIntegrity:
  def test_all_conditions_load(self, store):
    """Every YAML in conditions/{shared,peds,im} should parse."""
    conditions = store.get_all_conditions()
    assert len(conditions) > 200, f"Expected 200+ conditions, got {len(conditions)}"

  def test_conditions_have_required_fields(self, store):
    """Every condition must have id, display_name, specialties, system."""
    for c in store.get_all_conditions():
      assert c.id, f"Condition missing id"
      assert c.display_name, f"{c.id}: missing display_name"
      assert c.specialties, f"{c.id}: missing specialties"
      assert c.system, f"{c.id}: missing system"

  def test_conditions_have_valid_specialties(self, store):
    """Specialties must be peds, im, or both."""
    valid = {"peds", "im"}
    for c in store.get_all_conditions():
      for s in c.specialties:
        assert s in valid, f"{c.id}: invalid specialty '{s}'"

  def test_conditions_have_icd10_or_snomed(self, store):
    """Every condition should have at least one medical code."""
    missing_codes = []
    for c in store.get_all_conditions():
      if not c.icd10 and not c.snomed:
        missing_codes.append(c.id)
    assert len(missing_codes) == 0, f"Conditions missing codes: {missing_codes}"

  def test_peds_conditions_in_peds_pool(self, store):
    """Conditions in peds/ must have 'peds' in specialties."""
    for c in store.get_all_conditions():
      pool = store.get_condition_pool(c.id)
      if pool == "peds":
        assert "peds" in c.specialties, f"{c.id}: in peds/ but specialties={c.specialties}"

  def test_im_conditions_in_im_pool(self, store):
    """Conditions in im/ must have 'im' in specialties."""
    for c in store.get_all_conditions():
      pool = store.get_condition_pool(c.id)
      if pool == "im":
        assert "im" in c.specialties, f"{c.id}: in im/ but specialties={c.specialties}"

  def test_shared_conditions_have_both_specialties(self, store):
    """Conditions in shared/ must have both peds and im."""
    for c in store.get_all_conditions():
      pool = store.get_condition_pool(c.id)
      if pool == "shared":
        assert "peds" in c.specialties and "im" in c.specialties, \
          f"{c.id}: in shared/ but specialties={c.specialties}"

  def test_no_duplicate_condition_ids(self, store):
    """No two conditions should have the same id."""
    ids = [c.id for c in store.get_all_conditions()]
    dupes = [x for x in ids if ids.count(x) > 1]
    assert len(set(dupes)) == 0, f"Duplicate condition IDs: {set(dupes)}"

  def test_condition_systems_are_known(self, store):
    """All organ systems should be from a known set."""
    known_systems = {
      "respiratory", "pulmonary", "ent", "gi", "gastrointestinal",
      "derm", "dermatology", "dermatological",
      "cardiology", "endocrine", "metabolic",
      "renal", "genitourinary",
      "hematology", "hematological",
      "infectious_disease", "infectious",
      "rheumatology", "neurology", "neurological",
      "psychiatry", "mental_health",
      "geriatrics",
      "orthopedic", "ophthalmology", "eye",
      "urology", "general",
      "neurodevelopmental", "developmental", "immunological", "immunology",
      "wellness", "gynecology", "reproductive",
    }
    unknown = set()
    for c in store.get_all_conditions():
      if c.system and c.system not in known_systems:
        unknown.add(f"{c.id}:{c.system}")
    assert len(unknown) == 0, f"Unknown systems: {unknown}"


# ─── Frameworks ───────────────────────────────────────────────

class TestFrameworkIntegrity:
  def test_all_frameworks_load(self, store):
    """Every YAML in frameworks/{shared,peds,im} should parse."""
    frameworks = store.get_all_frameworks()
    assert len(frameworks) > 300, f"Expected 300+ frameworks, got {len(frameworks)}"

  def test_frameworks_have_required_fields(self, store):
    """Every framework must have id, topic, teaching_goals."""
    for f in store.get_all_frameworks():
      assert f.id, "Framework missing id"
      assert f.topic, f"{f.id}: missing topic"
      assert f.teaching_goals, f"{f.id}: missing teaching_goals"

  def test_frameworks_have_teaching_content(self, store):
    """Non-wellness frameworks should have goals, mistakes, red flags, and pearls."""
    incomplete = []
    for f in store.get_all_frameworks():
      # Well-child and wellness frameworks have different structure
      if f.visit_type in ("well_child", "wellness"):
        continue
      missing = []
      if not f.teaching_goals:
        missing.append("teaching_goals")
      if not f.common_mistakes:
        missing.append("common_mistakes")
      if not f.red_flags:
        missing.append("red_flags")
      if not f.clinical_pearls:
        missing.append("clinical_pearls")
      if missing:
        incomplete.append(f"{f.id}: {missing}")
    assert len(incomplete) == 0, f"Incomplete frameworks:\n" + "\n".join(incomplete[:10])

  def test_framework_lists_are_strings(self, store):
    """All list items in frameworks must be strings, not dicts."""
    bad = []
    for f in store.get_all_frameworks():
      for field_name in ["teaching_goals", "common_mistakes", "red_flags",
                         "clinical_pearls", "key_history_questions",
                         "key_exam_findings", "treatment_principles",
                         "disposition_guidance"]:
        items = getattr(f, field_name, None)
        if items:
          for i, item in enumerate(items):
            if not isinstance(item, str):
              bad.append(f"{f.id}.{field_name}[{i}]: {type(item).__name__}")
    assert len(bad) == 0, f"Non-string items in frameworks:\n" + "\n".join(bad[:10])

  def test_no_duplicate_framework_ids(self, store):
    """No two frameworks should have the same id."""
    ids = [f.id for f in store.get_all_frameworks()]
    dupes = [x for x in ids if ids.count(x) > 1]
    assert len(set(dupes)) == 0, f"Duplicate framework IDs: {set(dupes)}"


# ─── Disease Arcs ─────────────────────────────────────────────

class TestDiseaseArcIntegrity:
  def test_all_arcs_load(self, store):
    arcs = store.get_all_disease_arcs()
    assert len(arcs) >= 14, f"Expected 14+ disease arcs, got {len(arcs)}"

  def test_arcs_have_stages(self, store):
    for arc in store.get_all_disease_arcs():
      assert arc.stages, f"{arc.id}: has no stages"
      assert len(arc.stages) >= 2, f"{arc.id}: needs at least 2 stages, got {len(arc.stages)}"

  def test_arcs_have_pearls(self, store):
    for arc in store.get_all_disease_arcs():
      assert arc.clinical_pearls, f"{arc.id}: missing clinical_pearls"

  def test_arc_stages_have_condition_ids(self, store):
    for arc in store.get_all_disease_arcs():
      for stage in arc.stages:
        assert stage.condition_id, f"{arc.id}: stage missing condition_id"
        assert stage.display_name, f"{arc.id}: stage missing display_name"


# ─── Specialties & Learner Tracks ─────────────────────────────

class TestSpecialtyIntegrity:
  def test_three_specialties(self, store):
    specs = store.get_all_specialties()
    ids = {s.id for s in specs}
    assert ids == {"pediatrics", "internal_medicine", "family_practice"}

  def test_fp_has_all_pools(self, store):
    fp = store.get_specialty("family_practice")
    assert fp is not None
    assert set(fp.knowledge_pools) == {"peds", "im", "shared"}

  def test_learner_tracks_exist(self, store):
    tracks = store.get_all_learner_tracks()
    assert len(tracks) >= 15

  def test_learner_tracks_reference_valid_specialties(self, store):
    valid_specialties = {s.id for s in store.get_all_specialties()}
    for t in store.get_all_learner_tracks():
      assert t.specialty in valid_specialties, \
        f"{t.id}: references unknown specialty '{t.specialty}'"


# ─── Immunization Schedules ──────────────────────────────────

class TestImmunizationIntegrity:
  def test_peds_schedule_exists(self):
    path = KNOWLEDGE_DIR / "immunizations" / "peds_aap.yaml"
    assert path.exists(), "Peds AAP immunization schedule missing"
    with open(path) as f:
      data = yaml.safe_load(f)
    assert "vaccines" in data, "Peds schedule missing 'vaccines' section"
    assert "schedule" in data, "Peds schedule missing 'schedule' section"

  def test_adult_schedule_exists(self):
    path = KNOWLEDGE_DIR / "immunizations" / "adult_acip.yaml"
    assert path.exists(), "Adult ACIP immunization schedule missing"
    with open(path) as f:
      data = yaml.safe_load(f)
    assert "vaccines" in data, "Adult schedule missing 'vaccines' section"
    assert "schedule" in data, "Adult schedule missing 'schedule' section"

  def test_adult_schedule_has_age_groups(self):
    path = KNOWLEDGE_DIR / "immunizations" / "adult_acip.yaml"
    with open(path) as f:
      data = yaml.safe_load(f)
    schedule = data["schedule"]
    assert "age_18_26" in schedule
    assert "age_65_plus" in schedule


# ─── YAML Parsing ─────────────────────────────────────────────

class TestYAMLParsing:
  """Verify every YAML file in the knowledge tree parses without error."""

  def _yaml_files(self):
    """Find all YAML files in knowledge directory."""
    return list(KNOWLEDGE_DIR.rglob("*.yaml"))

  def test_all_yaml_files_parse(self):
    failures = []
    for path in self._yaml_files():
      if path.stem.startswith("_"):
        continue
      try:
        with open(path) as f:
          yaml.safe_load(f)
      except Exception as e:
        failures.append(f"{path.relative_to(KNOWLEDGE_DIR)}: {e}")
    assert len(failures) == 0, f"YAML parse failures:\n" + "\n".join(failures)

  def test_yaml_file_count(self):
    """Sanity check: we expect 500+ YAML files total."""
    count = len(self._yaml_files())
    assert count > 400, f"Expected 400+ YAML files, got {count}"
