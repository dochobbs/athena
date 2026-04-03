from pathlib import Path

import pytest
from athena.src.loader import KnowledgeStore

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def store():
  return KnowledgeStore(FIXTURES_DIR)


class TestKnowledgeStore:
  def test_loads_conditions(self, store):
    conditions = store.get_all_conditions()
    assert len(conditions) == 3
    ids = {c.id for c in conditions}
    assert ids == {"asthma", "croup", "copd"}

  def test_loads_from_correct_pools(self, store):
    asthma = store.get_condition("asthma")
    assert asthma is not None
    assert "peds" in asthma.specialties
    assert "im" in asthma.specialties

    croup = store.get_condition("croup")
    assert croup is not None
    assert croup.specialties == ["peds"]

    copd = store.get_condition("copd")
    assert copd is not None
    assert copd.specialties == ["im"]

  def test_get_condition_not_found(self, store):
    assert store.get_condition("nonexistent") is None

  def test_loads_frameworks(self, store):
    frameworks = store.get_all_frameworks()
    assert len(frameworks) == 3
    ids = {f.id for f in frameworks}
    assert ids == {"asthma", "croup", "copd"}

  def test_get_framework(self, store):
    fw = store.get_framework("croup")
    assert fw is not None
    assert fw.topic == "Croup"
    assert fw.specialties == ["peds"]

  def test_loads_specialties(self, store):
    specialties = store.get_all_specialties()
    assert len(specialties) == 3
    ids = {s.id for s in specialties}
    assert ids == {"pediatrics", "internal_medicine", "family_practice"}

  def test_get_specialty(self, store):
    peds = store.get_specialty("pediatrics")
    assert peds is not None
    assert peds.knowledge_pools == ["peds", "shared"]

  def test_loads_learner_tracks(self, store):
    tracks = store.get_all_learner_tracks()
    assert len(tracks) > 0
    levels = {t.level for t in tracks}
    assert "resident" in levels

  def test_condition_source_pool(self, store):
    assert store.get_condition_pool("croup") == "peds"
    assert store.get_condition_pool("copd") == "im"
    assert store.get_condition_pool("asthma") == "shared"
