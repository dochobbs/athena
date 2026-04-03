from athena.src.models import (
  Condition,
  SpecialtyVariant,
  Framework,
  Specialty,
  LearnerTrack,
  DiseaseArc,
  DiseaseArcStage,
  AgeRange,
)


class TestCondition:
  def test_minimal_condition(self):
    c = Condition(
      id="asthma",
      display_name="Asthma",
      snomed="195967001",
      icd10=["J45.909"],
      category="chronic",
      system="pulmonary",
      specialties=["peds", "im"],
      age_range=AgeRange(min_months=12),
    )
    assert c.id == "asthma"
    assert c.specialties == ["peds", "im"]
    assert c.age_range.min_months == 12
    assert c.age_range.max_months is None

  def test_condition_with_variants(self):
    c = Condition(
      id="asthma",
      display_name="Asthma",
      snomed="195967001",
      icd10=["J45.909"],
      category="chronic",
      system="pulmonary",
      specialties=["peds", "im"],
      age_range=AgeRange(min_months=12),
      specialty_variants={
        "peds": SpecialtyVariant(
          typical_age="5-12 years",
          common_triggers=["viral URI", "exercise"],
          teaching_emphasis="action plan compliance",
          key_differentials=["bronchiolitis", "croup"],
        ),
      },
    )
    assert c.specialty_variants["peds"].typical_age == "5-12 years"

  def test_peds_only_condition(self):
    c = Condition(
      id="croup",
      display_name="Croup",
      snomed="71186008",
      icd10=["J05.0"],
      category="acute",
      system="respiratory",
      specialties=["peds"],
      age_range=AgeRange(min_months=6, max_months=72),
    )
    assert c.specialties == ["peds"]
    assert c.age_range.max_months == 72


class TestFramework:
  def test_minimal_framework(self):
    f = Framework(
      id="asthma",
      topic="Asthma",
      category="pulmonary",
      specialties=["peds", "im"],
      teaching_goals=["Recognize wheezing patterns"],
      common_mistakes=["Missing exercise trigger"],
      red_flags=["Silent chest"],
      clinical_pearls=["Step therapy compliance"],
    )
    assert f.id == "asthma"
    assert len(f.teaching_goals) == 1

  def test_framework_with_optional_fields(self):
    f = Framework(
      id="croup",
      topic="Croup",
      category="respiratory",
      specialties=["peds"],
      teaching_goals=["Identify barky cough"],
      common_mistakes=["Missing stridor at rest"],
      red_flags=["Drooling"],
      clinical_pearls=["Dexamethasone single dose"],
      key_history_questions=["Onset timing?"],
      key_exam_findings=["Inspiratory stridor"],
      treatment_principles=["Steroids first"],
      disposition_guidance=["Admit if stridor at rest"],
    )
    assert f.key_history_questions == ["Onset timing?"]


class TestSpecialty:
  def test_specialty(self):
    s = Specialty(
      id="pediatrics",
      display_name="Pediatrics",
      age_range=AgeRange(min_months=0, max_months=216),
      description="Care of infants, children, and adolescents",
      knowledge_pools=["peds", "shared"],
    )
    assert s.knowledge_pools == ["peds", "shared"]

  def test_family_practice_pools(self):
    s = Specialty(
      id="family_practice",
      display_name="Family Practice",
      age_range=AgeRange(min_months=0),
      description="Primary care across all ages",
      knowledge_pools=["peds", "im", "shared"],
    )
    assert len(s.knowledge_pools) == 3


class TestLearnerTrack:
  def test_learner_track(self):
    lt = LearnerTrack(
      id="pgy1_peds",
      display_name="PGY-1 Pediatrics Resident",
      level="resident",
      specialty="pediatrics",
      year=1,
      complexity_cap="moderate",
    )
    assert lt.level == "resident"
    assert lt.complexity_cap == "moderate"


class TestDiseaseArc:
  def test_disease_arc(self):
    arc = DiseaseArc(
      id="atopic_march",
      name="Atopic March",
      description="Eczema to food allergy to asthma to allergic rhinitis",
      specialties=["peds"],
      stages=[
        DiseaseArcStage(
          condition_id="eczema",
          display_name="Eczema",
          typical_age_range=[3, 12],
          symptoms=["dry skin", "pruritus"],
          treatments=["emollients", "topical steroids"],
        ),
      ],
      clinical_pearls=["Early emollient use may prevent"],
    )
    assert len(arc.stages) == 1
    assert arc.stages[0].condition_id == "eczema"
