from pathlib import Path

import pytest
from athena.src.loader import KnowledgeStore
from athena.src.resolver import KnowledgeResolver

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def resolver():
  store = KnowledgeStore(FIXTURES_DIR)
  return KnowledgeResolver(store)


class TestResolveConditions:
  def test_peds_returns_peds_and_shared(self, resolver):
    results = resolver.resolve_conditions(specialty="pediatrics")
    ids = {c.id for c in results}
    assert "asthma" in ids  # shared
    assert "croup" in ids  # peds
    assert "copd" not in ids  # im only

  def test_im_returns_im_and_shared(self, resolver):
    results = resolver.resolve_conditions(specialty="internal_medicine")
    ids = {c.id for c in results}
    assert "asthma" in ids  # shared
    assert "copd" in ids  # im
    assert "croup" not in ids  # peds only

  def test_fp_returns_all(self, resolver):
    results = resolver.resolve_conditions(specialty="family_practice")
    ids = {c.id for c in results}
    assert "asthma" in ids
    assert "croup" in ids
    assert "copd" in ids

  def test_filter_by_age(self, resolver):
    # 6-month-old: croup valid (6-72mo), asthma not (min 12mo), copd not (min 480mo)
    results = resolver.resolve_conditions(specialty="family_practice", age_months=6)
    ids = {c.id for c in results}
    assert "croup" in ids
    assert "asthma" not in ids
    assert "copd" not in ids

  def test_filter_by_age_adult(self, resolver):
    # 600 months (50 years): copd valid, asthma valid, croup not (max 72mo)
    results = resolver.resolve_conditions(specialty="family_practice", age_months=600)
    ids = {c.id for c in results}
    assert "copd" in ids
    assert "asthma" in ids
    assert "croup" not in ids

  def test_filter_by_system(self, resolver):
    results = resolver.resolve_conditions(specialty="family_practice", system="pulmonary")
    assert len(results) == 3

  def test_unknown_specialty_returns_empty(self, resolver):
    results = resolver.resolve_conditions(specialty="dermatology")
    assert results == []


class TestResolveFrameworks:
  def test_peds_frameworks(self, resolver):
    results = resolver.resolve_frameworks(specialty="pediatrics")
    ids = {f.id for f in results}
    assert "asthma" in ids
    assert "croup" in ids
    assert "copd" not in ids

  def test_im_frameworks(self, resolver):
    results = resolver.resolve_frameworks(specialty="internal_medicine")
    ids = {f.id for f in results}
    assert "asthma" in ids
    assert "copd" in ids
    assert "croup" not in ids

  def test_fp_frameworks(self, resolver):
    results = resolver.resolve_frameworks(specialty="family_practice")
    ids = {f.id for f in results}
    assert len(ids) == 3

  def test_framework_for_condition(self, resolver):
    fw = resolver.resolve_framework_for_condition(
      condition="croup", specialty="pediatrics"
    )
    assert fw is not None
    assert fw.topic == "Croup"

  def test_framework_for_condition_wrong_specialty(self, resolver):
    fw = resolver.resolve_framework_for_condition(
      condition="croup", specialty="internal_medicine"
    )
    assert fw is None


class TestResolveLearnerTracks:
  def test_filter_by_specialty(self, resolver):
    tracks = resolver.resolve_learner_tracks(specialty="pediatrics")
    for t in tracks:
      assert t.specialty == "pediatrics"

  def test_filter_by_level(self, resolver):
    tracks = resolver.resolve_learner_tracks(level="resident")
    for t in tracks:
      assert t.level == "resident"
