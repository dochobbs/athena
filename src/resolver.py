from __future__ import annotations

from .loader import KnowledgeStore
from .models import Condition, Framework, LearnerTrack, DiseaseArc


class KnowledgeResolver:
  """Filters knowledge by specialty, age, learner level, and organ system."""

  def __init__(self, store: KnowledgeStore):
    self._store = store

  def _get_pools(self, specialty: str) -> list[str]:
    """Get knowledge pools for a specialty."""
    spec = self._store.get_specialty(specialty)
    if spec is None:
      return []
    return spec.knowledge_pools

  def _condition_in_pools(self, condition: Condition, pools: list[str]) -> bool:
    """Check if condition belongs to any of the given pools."""
    pool = self._store.get_condition_pool(condition.id)
    return pool in pools

  def _condition_matches_age(self, condition: Condition, age_months: int) -> bool:
    """Check if condition is valid for given age."""
    age_range = condition.age_range
    if age_range.min_months and age_months < age_range.min_months:
      return False
    if age_range.max_months and age_months > age_range.max_months:
      return False
    return True

  def resolve_conditions(
    self,
    specialty: str,
    age_months: int | None = None,
    level: str | None = None,
    system: str | None = None,
  ) -> list[Condition]:
    pools = self._get_pools(specialty)
    if not pools:
      return []

    results = []
    for condition in self._store.get_all_conditions():
      if not self._condition_in_pools(condition, pools):
        continue
      if age_months is not None and not self._condition_matches_age(condition, age_months):
        continue
      if system is not None and condition.system != system:
        continue
      results.append(condition)

    return results

  def resolve_frameworks(
    self,
    specialty: str,
    category: str | None = None,
  ) -> list[Framework]:
    pools = self._get_pools(specialty)
    if not pools:
      return []

    results = []
    for fw in self._store.get_all_frameworks():
      pool = self._store.get_framework_pool(fw.id)
      if pool not in pools:
        continue
      if category is not None and fw.category != category:
        continue
      results.append(fw)

    return results

  def resolve_framework_for_condition(
    self,
    condition: str,
    specialty: str,
    level: str | None = None,
  ) -> Framework | None:
    pools = self._get_pools(specialty)
    if not pools:
      return None

    fw = self._store.get_framework(condition)
    if fw is None:
      return None

    pool = self._store.get_framework_pool(fw.id)
    if pool not in pools:
      return None

    return fw

  def resolve_disease_arcs(
    self,
    specialty: str,
  ) -> list[DiseaseArc]:
    pools = self._get_pools(specialty)
    if not pools:
      return []

    results = []
    for arc in self._store.get_all_disease_arcs():
      if any(s in pools for s in arc.specialties):
        results.append(arc)
    return results

  def resolve_learner_tracks(
    self,
    specialty: str | None = None,
    level: str | None = None,
  ) -> list[LearnerTrack]:
    results = []
    for track in self._store.get_all_learner_tracks():
      if specialty is not None and track.specialty != specialty:
        continue
      if level is not None and track.level != level:
        continue
      results.append(track)
    return results
