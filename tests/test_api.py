def test_root(client):
  response = client.get("/")
  assert response.status_code == 200
  data = response.json()
  assert data["name"] == "Athena"
  assert data["status"] == "running"


def test_health(client):
  response = client.get("/api/health")
  assert response.status_code == 200
  data = response.json()
  assert data["status"] == "healthy"
  assert data["service"] == "athena"
  assert data["knowledge"]["conditions"] == 3
  assert data["knowledge"]["frameworks"] == 3
  assert data["knowledge"]["specialties"] == 3


class TestConditionsAPI:
  def test_list_all(self, client):
    r = client.get("/api/conditions")
    assert r.status_code == 200
    assert len(r.json()) == 3

  def test_filter_by_specialty_peds(self, client):
    r = client.get("/api/conditions?specialty=pediatrics")
    assert r.status_code == 200
    ids = {c["id"] for c in r.json()}
    assert "croup" in ids
    assert "asthma" in ids
    assert "copd" not in ids

  def test_filter_by_specialty_im(self, client):
    r = client.get("/api/conditions?specialty=internal_medicine")
    ids = {c["id"] for c in r.json()}
    assert "copd" in ids
    assert "asthma" in ids
    assert "croup" not in ids

  def test_filter_by_specialty_fp(self, client):
    r = client.get("/api/conditions?specialty=family_practice")
    ids = {c["id"] for c in r.json()}
    assert len(ids) == 3

  def test_filter_by_age(self, client):
    r = client.get("/api/conditions?specialty=family_practice&age_months=6")
    ids = {c["id"] for c in r.json()}
    assert "croup" in ids
    assert "asthma" not in ids

  def test_filter_by_system(self, client):
    r = client.get("/api/conditions?system=pulmonary")
    assert len(r.json()) == 3

  def test_get_single_condition(self, client):
    r = client.get("/api/conditions/asthma")
    assert r.status_code == 200
    data = r.json()
    assert data["display_name"] == "Asthma"
    assert "peds" in data["specialty_variants"]
    assert "im" in data["specialty_variants"]

  def test_get_condition_not_found(self, client):
    r = client.get("/api/conditions/nonexistent")
    assert r.status_code == 404


class TestFrameworksAPI:
  def test_list_all(self, client):
    r = client.get("/api/frameworks")
    assert r.status_code == 200
    assert len(r.json()) == 3

  def test_filter_by_specialty(self, client):
    r = client.get("/api/frameworks?specialty=pediatrics")
    ids = {f["id"] for f in r.json()}
    assert "croup" in ids
    assert "asthma" in ids
    assert "copd" not in ids

  def test_get_single_framework(self, client):
    r = client.get("/api/frameworks/croup")
    assert r.status_code == 200
    data = r.json()
    assert data["topic"] == "Croup"
    assert len(data["teaching_goals"]) > 0

  def test_get_framework_not_found(self, client):
    r = client.get("/api/frameworks/nonexistent")
    assert r.status_code == 404

  def test_get_framework_for_condition(self, client):
    r = client.get("/api/frameworks/for-condition/asthma?specialty=pediatrics")
    assert r.status_code == 200
    assert r.json()["topic"] == "Asthma"

  def test_framework_for_condition_wrong_specialty(self, client):
    r = client.get("/api/frameworks/for-condition/croup?specialty=internal_medicine")
    assert r.status_code == 404


class TestSpecialtiesAPI:
  def test_list_specialties(self, client):
    r = client.get("/api/specialties")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 3
    ids = {s["id"] for s in data}
    assert ids == {"pediatrics", "internal_medicine", "family_practice"}

  def test_get_specialty(self, client):
    r = client.get("/api/specialties/pediatrics")
    assert r.status_code == 200
    data = r.json()
    assert data["display_name"] == "Pediatrics"
    assert "peds" in data["knowledge_pools"]

  def test_get_specialty_not_found(self, client):
    r = client.get("/api/specialties/dermatology")
    assert r.status_code == 404


class TestLearnersAPI:
  def test_list_all_tracks(self, client):
    r = client.get("/api/learner-tracks")
    assert r.status_code == 200
    assert len(r.json()) > 0

  def test_filter_by_specialty(self, client):
    r = client.get("/api/learner-tracks?specialty=pediatrics")
    assert r.status_code == 200
    for track in r.json():
      assert track["specialty"] == "pediatrics"

  def test_filter_by_level(self, client):
    r = client.get("/api/learner-tracks?level=resident")
    assert r.status_code == 200
    for track in r.json():
      assert track["level"] == "resident"


class TestDiseaseArcsAPI:
  def test_list_arcs_empty(self, client):
    r = client.get("/api/disease-arcs")
    assert r.status_code == 200
    assert r.json() == []

  def test_list_arcs_with_specialty(self, client):
    r = client.get("/api/disease-arcs?specialty=pediatrics")
    assert r.status_code == 200


class TestImmunizationsAPI:
  def test_list_immunizations_empty(self, client):
    r = client.get("/api/immunizations")
    assert r.status_code == 200
    assert r.json() == []
