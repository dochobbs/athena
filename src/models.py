from __future__ import annotations

from pydantic import BaseModel, Field


# --- Shared building blocks ---

class AgeRange(BaseModel):
  min_months: int = 0
  max_months: int | None = None
  peak: list[int] | None = None


class VitalsImpact(BaseModel):
  temp_f: list[float] | None = None
  hr_multiplier: float | None = None
  rr_multiplier: float | None = None
  spo2_min: int | None = None
  respiratory_rate: dict | None = None
  spo2: dict | None = None


class SymptomDef(BaseModel):
  name: str
  probability: float = 1.0
  description: str = ""
  age_min: int | None = None


class PhysicalExamFinding(BaseModel):
  system: str
  finding: str
  probability: float = 1.0


class LabDef(BaseModel):
  agent: str
  loinc: str = ""


class MedicationDef(BaseModel):
  agent: str
  rxnorm: str = ""
  dose_mg_kg: float | None = None
  max_dose_mg: float | None = None
  frequency: str = ""
  duration_days: int | None = None
  route: str = "oral"
  indication: str = ""
  prn: bool = False
  age_min_months: int | None = None


class SpecialtyVariant(BaseModel):
  typical_age: str = ""
  common_triggers: list[str] = Field(default_factory=list)
  teaching_emphasis: str = ""
  key_differentials: list[str] = Field(default_factory=list)


# --- Demographics (from Oread condition schema) ---

class DemographicsDef(BaseModel):
  age_months: AgeRange | None = None
  gender_bias: dict[str, float] | None = None
  risk_factors: list[str] = Field(default_factory=list)


class PrevalenceDef(BaseModel):
  annual_episodes_per_child: float | None = None
  lifetime_by_age_3: float | None = None
  hospitalization_rate_under_1: float | None = None
  notes: str = ""


class SeasonalityDef(BaseModel):
  peak_months: list[int] = Field(default_factory=list)
  weight_multiplier: float = 1.0


# --- Core domain models ---

class Condition(BaseModel):
  id: str
  display_name: str
  aliases: list[str] = Field(default_factory=list)
  snomed: str = ""
  icd10: list[str] = Field(default_factory=list)
  rxnorm_primary: str = ""
  category: str = ""  # acute | chronic | newborn
  system: str = ""  # pulmonary | gi | cardiology | etc.
  specialties: list[str] = Field(default_factory=list)  # ["peds", "im"]
  age_range: AgeRange = Field(default_factory=AgeRange)
  complexity: dict[str, str] = Field(default_factory=dict)
  specialty_variants: dict[str, SpecialtyVariant] = Field(default_factory=dict)

  # Clinical data (Oread-compatible)
  demographics: DemographicsDef | None = None
  prevalence: PrevalenceDef | None = None
  seasonality: SeasonalityDef | None = None
  vitals_impact: VitalsImpact | dict | None = None
  presentation: dict | None = None  # Flexible: symptoms, duration, PE
  diagnostics: dict | None = None  # Labs, imaging
  treatment: dict | None = None  # Medications, instructions
  progression: list[dict] | None = None  # Disease arc links


class Framework(BaseModel):
  id: str
  topic: str
  aliases: list[str] = Field(default_factory=list)
  category: str = ""
  specialties: list[str] = Field(default_factory=list)
  age_range_months: list[int] | None = None

  # Required
  teaching_goals: list[str] = Field(default_factory=list)
  common_mistakes: list[str] = Field(default_factory=list)
  red_flags: list[str] = Field(default_factory=list)
  clinical_pearls: list[str] = Field(default_factory=list)

  # Recommended
  key_history_questions: list[str] | None = None
  key_exam_findings: list[str] | None = None
  treatment_principles: list[str] | None = None
  disposition_guidance: list[str] | None = None

  # Optional
  differential_diagnosis: list[str] | None = None
  seasonality: SeasonalityDef | None = None
  parent_styles: list[str] | None = None
  sources: list[str] | None = None
  images: list[dict] | None = None

  # Well-child specific
  visit_type: str | None = None
  visit_age_months: int | None = None
  expected_milestones: dict | None = None
  screening_tools: list[dict] | None = None
  anticipatory_guidance: dict | None = None
  immunizations_due: list[dict] | None = None
  physical_exam_focus: list[dict] | None = None


class Specialty(BaseModel):
  id: str
  display_name: str
  description: str = ""
  age_range: AgeRange = Field(default_factory=AgeRange)
  knowledge_pools: list[str] = Field(default_factory=list)


class LearnerTrack(BaseModel):
  id: str
  display_name: str
  level: str  # student | resident | np_student | fellow | attending
  specialty: str
  year: int | None = None
  complexity_cap: str = "moderate"  # straightforward | moderate | challenging
  description: str = ""


class DiseaseArcStage(BaseModel):
  condition_id: str
  display_name: str
  typical_age_range: list[int] = Field(default_factory=list)
  symptoms: list[str] = Field(default_factory=list)
  treatments: list[str] = Field(default_factory=list)
  transition_triggers: list[str] = Field(default_factory=list)


class DiseaseArc(BaseModel):
  id: str
  name: str
  description: str = ""
  specialties: list[str] = Field(default_factory=list)
  stages: list[DiseaseArcStage] = Field(default_factory=list)
  clinical_pearls: list[str] = Field(default_factory=list)
  references: list[str] = Field(default_factory=list)
