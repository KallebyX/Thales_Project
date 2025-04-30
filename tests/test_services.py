import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sys
import os
import importlib.util

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
module_path = os.path.abspath("services/patient_service.py")
spec = importlib.util.spec_from_file_location("services.patient_service", module_path)
ps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ps)
sys.modules["services.patient_service"] = ps
print("Módulo services.patient_service carregado!")
def test_birth_date_and_created_at():
    from datetime import datetime, date
    p = FakePatient(
        birth_date=date(1990, 5, 15),
        created_at=datetime(2023, 1, 1),
        updated_at=datetime(2023, 6, 1)
    )
    data = ps.build_patients_data([p])[0]
    assert data["birth_date"] == "1990-05-15"
    assert data["created_at"].startswith("2023")
    assert data["updated_at"].startswith("2023")

def test_invalid_medications_type():
    p = FakePatient(medications={"enalapril": True})
    data = ps.build_patients_data([p])[0]
    assert isinstance(data["medications"], list)

def test_invalid_comorbidities_type():
    p = FakePatient(comorbidities=12345)
    data = ps.build_patients_data([p])[0]
    assert isinstance(data["comorbidities"], list)

def test_none_observations():
    p = FakePatient(observations=None)
    data = ps.build_patients_data([p])[0]
    assert data["observations"] is None

def test_risk_level_and_score_present():
    p = FakePatient()
    p.risk_level = "Moderado"
    p.risk_score = 4
    data = ps.build_patients_data([p])[0]
    assert data["risk_level"] == "Moderado"
    assert data["risk_score"] == 4


import pytest

class FakeConsultation:
    def __init__(self, medications=None):
        self.medications = medications or []

class FakePatient:
    def __init__(
        self, id=1, name='Paciente Teste', birth_date=None, gender='F', cpf='00000000000',
        comorbidities=None, medications=None, observations=None,
        consultations=None, created_at=None, updated_at=None
    ):
        self.id = id
        self.name = name
        self.birth_date = birth_date
        self.gender = gender
        self.cpf = cpf
        self.comorbidities = comorbidities
        self.medications = medications
        self.observations = observations
        self.consultations = consultations or []
        self.created_at = created_at
        self.updated_at = updated_at

def test_empty_list_returns_empty():
    assert ps.build_patients_data([]) == []

def test_basic_fields_and_medications_list():
    p = FakePatient(medications=["enalapril", "simvastatina"])
    data = ps.build_patients_data([p])[0]
    assert data["id"] == 1
    assert data["name"] == "Paciente Teste"
    assert data["medications"] == ["enalapril", "simvastatina"]

def test_medications_as_string_csv():
    p = FakePatient(medications="atenolol, metformina")
    data = ps.build_patients_data([p])[0]
    assert data["medications"] == ["atenolol", "metformina"]

def test_medications_from_consultations():
    p = FakePatient(medications=None, consultations=[FakeConsultation(["omeprazol", "dipirona"])])
    data = ps.build_patients_data([p])[0]
    assert "omeprazol" in data["medications"]

def test_comorbidities_variants():
    p = FakePatient(comorbidities=["diabetes", "hipertensão"])
    data = ps.build_patients_data([p])[0]
    assert "diabetes" in data["comorbidities"]

def test_comorbidities_as_string():
    p = FakePatient(comorbidities="asma, obesidade")
    data = ps.build_patients_data([p])[0]
    assert "asma" in data["comorbidities"]

def test_observations_handling():
    p = FakePatient(observations="Paciente com histórico familiar.")
    data = ps.build_patients_data([p])[0]
    assert "histórico" in data["observations"]

def test_missing_fields_defaults():
    p = FakePatient(name=None, gender=None, cpf=None, medications=None, comorbidities=None)
    data = ps.build_patients_data([p])[0]
    assert data["name"] is None
    assert data["medications"] == []
    assert data["comorbidities"] == []
def test_risk_level_none():
    p = FakePatient()
    if hasattr(p, 'risk_level'):
        del p.risk_level
    if hasattr(p, 'risk_score'):
        del p.risk_score
    data = ps.build_patients_data([p])[0]
    assert "risk_level" not in data or data["risk_level"] is None
    assert "risk_score" not in data or data["risk_score"] is None

def test_consultation_medications_invalid():
    p = FakePatient(consultations=[FakeConsultation(medications="não é lista")])
    data = ps.build_patients_data([p])[0]
    assert isinstance(data["medications"], list)