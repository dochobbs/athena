"""Resolver coverage tests — validates specialty filtering across the full knowledge base.

Tests that the resolver correctly partitions conditions and frameworks by
specialty, age, and organ system using the real production knowledge.
"""
from pathlib import Path

import pytest

from athena.src.loader import KnowledgeStore
from athena.src.resolver import KnowledgeResolver

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"


@pytest.fixture(scope="module")
def resolver():
  store = KnowledgeStore(KNOWLEDGE_DIR)
  return KnowledgeResolver(store)


@pytest.fixture(scope="module")
def store():
  return KnowledgeStore(KNOWLEDGE_DIR)


# ─── Specialty Partitioning ───────────────────────────────────

class TestSpecialtyPartitioning:
  def test_fp_is_superset(self, resolver):
    """Family Practice must return ALL conditions from peds and IM."""
    peds = {c.id for c in resolver.resolve_conditions(specialty="pediatrics")}
    im = {c.id for c in resolver.resolve_conditions(specialty="internal_medicine")}
    fp = {c.id for c in resolver.resolve_conditions(specialty="family_practice")}
    assert peds | im == fp, f"FP missing: {(peds | im) - fp}"

  def test_peds_no_im_only(self, resolver, store):
    """Peds should never include IM-only conditions."""
    peds = resolver.resolve_conditions(specialty="pediatrics")
    for c in peds:
      pool = store.get_condition_pool(c.id)
      assert pool != "im", f"{c.id} is IM-only but appeared in peds results"

  def test_im_no_peds_only(self, resolver, store):
    """IM should never include peds-only conditions."""
    im = resolver.resolve_conditions(specialty="internal_medicine")
    for c in im:
      pool = store.get_condition_pool(c.id)
      assert pool != "peds", f"{c.id} is peds-only but appeared in IM results"

  def test_shared_in_both(self, resolver, store):
    """Shared conditions must appear in both peds and IM results."""
    peds_ids = {c.id for c in resolver.resolve_conditions(specialty="pediatrics")}
    im_ids = {c.id for c in resolver.resolve_conditions(specialty="internal_medicine")}
    for c in store.get_all_conditions():
      if store.get_condition_pool(c.id) == "shared":
        assert c.id in peds_ids, f"Shared condition {c.id} missing from peds"
        assert c.id in im_ids, f"Shared condition {c.id} missing from IM"

  def test_unknown_specialty_empty(self, resolver):
    assert resolver.resolve_conditions(specialty="dermatology") == []
    assert resolver.resolve_frameworks(specialty="dermatology") == []


# ─── Age Filtering ────────────────────────────────────────────

class TestAgeFiltering:
  def test_newborn_only_peds(self, resolver):
    """A newborn should only get peds conditions."""
    results = resolver.resolve_conditions(specialty="family_practice", age_months=0)
    for c in results:
      assert "peds" in c.specialties or "im" in c.specialties

  def test_infant_no_adult_conditions(self, resolver):
    """A 6-month-old should not get COPD, CHF, etc."""
    results = resolver.resolve_conditions(specialty="family_practice", age_months=6)
    ids = {c.id for c in results}
    adult_only = {"copd_stable", "chf_hfref", "atrial_fibrillation", "cirrhosis"}
    overlap = ids & adult_only
    assert len(overlap) == 0, f"Adult conditions in infant results: {overlap}"

  def test_adult_no_croup(self, resolver):
    """A 40-year-old should not get croup or bronchiolitis."""
    results = resolver.resolve_conditions(specialty="family_practice", age_months=480)
    ids = {c.id for c in results}
    peds_only = {"croup", "bronchiolitis", "roseola", "hand_foot_mouth_disease"}
    overlap = ids & peds_only
    assert len(overlap) == 0, f"Peds conditions in adult results: {overlap}"

  def test_elderly_gets_geriatrics(self, resolver):
    """A 75-year-old should see geriatrics conditions."""
    results = resolver.resolve_conditions(specialty="internal_medicine", age_months=900)
    ids = {c.id for c in results}
    geri = {"polypharmacy", "falls_assessment", "frailty_syndrome"}
    for g in geri:
      if g in {c.id for c in resolver._store.get_all_conditions()}:
        assert g in ids, f"Geriatrics condition {g} missing for 75yo"

  def test_age_filtering_reduces_count(self, resolver):
    """Filtering by age should return fewer conditions than unfiltered."""
    all_fp = resolver.resolve_conditions(specialty="family_practice")
    infant = resolver.resolve_conditions(specialty="family_practice", age_months=6)
    assert len(infant) < len(all_fp), "Age filter didn't reduce results"


# ─── Organ System Filtering ──────────────────────────────────

class TestSystemFiltering:
  def test_cardiology_only_cardiology(self, resolver):
    """System filter should only return matching system."""
    results = resolver.resolve_conditions(
      specialty="internal_medicine", system="cardiology"
    )
    for c in results:
      assert c.system == "cardiology", f"{c.id} has system={c.system}, expected cardiology"

  def test_system_filter_reduces_count(self, resolver):
    """System filter should return fewer than all IM conditions."""
    all_im = resolver.resolve_conditions(specialty="internal_medicine")
    cardio = resolver.resolve_conditions(specialty="internal_medicine", system="cardiology")
    assert len(cardio) < len(all_im)
    assert len(cardio) > 0


# ─── Framework Resolver ──────────────────────────────────────

class TestFrameworkResolver:
  def test_fp_frameworks_superset(self, resolver):
    """FP frameworks should be superset of peds + IM."""
    peds = {f.id for f in resolver.resolve_frameworks(specialty="pediatrics")}
    im = {f.id for f in resolver.resolve_frameworks(specialty="internal_medicine")}
    fp = {f.id for f in resolver.resolve_frameworks(specialty="family_practice")}
    assert peds | im == fp

  def test_peds_framework_for_croup(self, resolver):
    fw = resolver.resolve_framework_for_condition("croup", specialty="pediatrics")
    assert fw is not None
    assert "Croup" in fw.topic

  def test_no_croup_in_im(self, resolver):
    fw = resolver.resolve_framework_for_condition("croup", specialty="internal_medicine")
    assert fw is None

  def test_im_framework_for_chf(self, resolver):
    fw = resolver.resolve_framework_for_condition("chf_hfref", specialty="internal_medicine")
    assert fw is not None

  def test_shared_framework_in_both(self, resolver):
    """Asthma framework (shared) should be available in both peds and IM."""
    peds_fw = resolver.resolve_framework_for_condition("asthma", specialty="pediatrics")
    im_fw = resolver.resolve_framework_for_condition("asthma", specialty="internal_medicine")
    assert peds_fw is not None, "Asthma framework missing from peds"
    assert im_fw is not None, "Asthma framework missing from IM"


# ─── Disease Arc Resolver ─────────────────────────────────────

class TestDiseaseArcResolver:
  def test_peds_arcs(self, resolver):
    arcs = resolver.resolve_disease_arcs(specialty="pediatrics")
    ids = {a.id for a in arcs}
    assert "atopic_march" in ids

  def test_im_arcs(self, resolver):
    arcs = resolver.resolve_disease_arcs(specialty="internal_medicine")
    ids = {a.id for a in arcs}
    assert "metabolic_cascade" in ids
    assert "atopic_march" not in ids  # peds only

  def test_fp_sees_all_arcs(self, resolver):
    peds_arcs = resolver.resolve_disease_arcs(specialty="pediatrics")
    im_arcs = resolver.resolve_disease_arcs(specialty="internal_medicine")
    fp_arcs = resolver.resolve_disease_arcs(specialty="family_practice")
    assert len(fp_arcs) == len(peds_arcs) + len(im_arcs)


# ─── Learner Track Resolver ──────────────────────────────────

class TestLearnerTrackResolver:
  def test_peds_residents(self, resolver):
    tracks = resolver.resolve_learner_tracks(specialty="pediatrics", level="resident")
    assert len(tracks) > 0
    for t in tracks:
      assert t.specialty == "pediatrics"
      assert t.level == "resident"

  def test_im_students(self, resolver):
    tracks = resolver.resolve_learner_tracks(specialty="internal_medicine", level="student")
    assert len(tracks) > 0

  def test_all_tracks_have_valid_levels(self, resolver):
    valid_levels = {"student", "resident", "np_student", "fellow", "attending"}
    tracks = resolver.resolve_learner_tracks()
    for t in tracks:
      assert t.level in valid_levels, f"{t.id}: invalid level '{t.level}'"
