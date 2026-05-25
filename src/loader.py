from __future__ import annotations

from pathlib import Path

import yaml

from .models import (
  Condition,
  Framework,
  Specialty,
  LearnerTrack,
  DiseaseArc,
)


class KnowledgeStore:
  """Loads and indexes YAML knowledge files from a directory tree."""

  def __init__(self, knowledge_dir: Path | str):
    self._dir = Path(knowledge_dir)
    self._conditions: dict[str, Condition] = {}
    self._condition_pools: dict[str, str] = {}
    self._frameworks: dict[str, Framework] = {}
    self._framework_pools: dict[str, str] = {}
    self._specialties: dict[str, Specialty] = {}
    self._learner_tracks: list[LearnerTrack] = []
    self._disease_arcs: dict[str, DiseaseArc] = {}
    self._load()

  def _load(self):
    self._load_specialties()
    self._load_conditions()
    self._load_frameworks()
    self._load_learner_tracks()
    self._load_disease_arcs()

  # --- Loading ---

  def _load_yaml(self, path: Path) -> dict | list | None:
    if not path.exists():
      return None
    try:
      with open(path, "r") as f:
        return yaml.safe_load(f)
    except yaml.YAMLError as e:
      raise RuntimeError(f"Malformed YAML in {path}: {e}") from e

  def _load_yaml_dir(self, directory: Path) -> list[tuple[dict, str]]:
    """Load all YAML files from a directory. Returns (data, filename_stem) pairs."""
    results = []
    if not directory.exists():
      return results
    for path in sorted(directory.glob("*.yaml")):
      if path.stem.startswith("_"):
        continue
      data = self._load_yaml(path)
      if data:
        results.append((data, path.stem))
    return results

  def _load_specialties(self):
    spec_dir = self._dir / "specialties"
    for data, stem in self._load_yaml_dir(spec_dir):
      spec = Specialty(**data)
      self._specialties[spec.id] = spec

  def _load_conditions(self):
    cond_dir = self._dir / "conditions"
    for pool in ["shared", "peds", "im"]:
      pool_dir = cond_dir / pool
      for data, stem in self._load_yaml_dir(pool_dir):
        if "id" not in data:
          data["id"] = stem
        condition = Condition(**data)
        self._conditions[condition.id] = condition
        self._condition_pools[condition.id] = pool

  def _load_frameworks(self):
    fw_dir = self._dir / "frameworks"
    for pool in ["shared", "peds", "im"]:
      pool_dir = fw_dir / pool
      for data, stem in self._load_yaml_dir(pool_dir):
        if "id" not in data:
          data["id"] = stem
        framework = Framework(**data)
        self._frameworks[framework.id] = framework
        self._framework_pools[framework.id] = pool

  def _load_learner_tracks(self):
    tracks_dir = self._dir / "learner_tracks"
    for data, stem in self._load_yaml_dir(tracks_dir):
      if "tracks" in data:
        for track_data in data["tracks"]:
          self._learner_tracks.append(LearnerTrack(**track_data))
      else:
        self._learner_tracks.append(LearnerTrack(**data))

  def _load_disease_arcs(self):
    arcs_dir = self._dir / "disease_arcs"
    for pool in ["peds", "im"]:
      pool_dir = arcs_dir / pool
      for data, stem in self._load_yaml_dir(pool_dir):
        if "id" not in data:
          data["id"] = stem
        # Normalize stage field names (Oread uses condition_key)
        for stage in data.get("stages", []):
          if "condition_key" in stage and "condition_id" not in stage:
            stage["condition_id"] = stage.pop("condition_key")
        arc = DiseaseArc(**data)
        self._disease_arcs[arc.id] = arc

  # --- Accessors ---

  def get_all_conditions(self) -> list[Condition]:
    return list(self._conditions.values())

  def get_condition(self, condition_id: str) -> Condition | None:
    return self._conditions.get(condition_id)

  def get_condition_pool(self, condition_id: str) -> str | None:
    return self._condition_pools.get(condition_id)

  def get_all_frameworks(self) -> list[Framework]:
    return list(self._frameworks.values())

  def get_framework(self, framework_id: str) -> Framework | None:
    return self._frameworks.get(framework_id)

  def get_framework_pool(self, framework_id: str) -> str | None:
    return self._framework_pools.get(framework_id)

  def get_all_specialties(self) -> list[Specialty]:
    return list(self._specialties.values())

  def get_specialty(self, specialty_id: str) -> Specialty | None:
    return self._specialties.get(specialty_id)

  def get_all_learner_tracks(self) -> list[LearnerTrack]:
    return list(self._learner_tracks)

  def get_all_disease_arcs(self) -> list[DiseaseArc]:
    return list(self._disease_arcs.values())

  def get_disease_arc(self, arc_id: str) -> DiseaseArc | None:
    return self._disease_arcs.get(arc_id)
