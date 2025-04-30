import pytest
from datetime import datetime
from services.patient_service import build_patients_data
from types import SimpleNamespace
from utils import calcular_risco_cardiaco


def test_build_patients_data():
    class FakeConsultation:
        def __init__(self):
            self.medications = "aspirina, dipirona"
            self.created_at = datetime.now()

    fake_patient = SimpleNamespace(
        id=1,
        name="Teste",
        cpf="12345678900",
        birth_date=datetime(2000, 1, 1).date(),
        risk_level="moderado",
        risk_score=5,
        comorbidities=["hipertensão"],
        medications=["enalapril"],
        observations="Paciente teste",
        consultations=[FakeConsultation()],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        previous_events=["infarto"],
        cardiac_symptoms=["dor no peito"],
        sleep_duration=6,
        sleep_quality="boa",
        diet="equilibrada",
        smoking_status="não",
        alcohol="socialmente",
        exercise="moderado",
        gender="F",
        weight=70,
        height=1.70,
        age=23
    )
    data = build_patients_data([fake_patient])
    assert isinstance(data, list)
    assert data[0]['name'] == "Teste"


def test_calcular_risco_cardiaco_completo():
    fake_patient = SimpleNamespace(
        age=45,
        gender="M",
        smoking_status="sim",
        history_family=["infarto"],
        comorbidities=["hipertensao"],
        exercise="baixo",
        diet="ruim",
        sleep_quality="ruim"
    )
    result = calcular_risco_cardiaco(fake_patient)
    assert isinstance(result, dict)
    assert 'nivel_risco' in result
    assert 'pontuacao' in result


def test_calcular_risco_cardiaco_incompleto():
    fake_patient = SimpleNamespace()
    result = calcular_risco_cardiaco(fake_patient)
    assert isinstance(result, dict)
    assert result['nivel_risco'] == 'Indefinido'


# Testes complementares
from utils import gerar_senha_segura, enviar_email_reset, calcular_idade

def test_gerar_senha_segura():
    senha = gerar_senha_segura(16)
    assert isinstance(senha, str)
    assert len(senha) == 16
    assert any(c.isdigit() for c in senha)
    assert any(c.isupper() for c in senha)
    assert any(c.islower() for c in senha)

def test_calcular_idade():
    from datetime import date
    idade = calcular_idade(date(2000, 1, 1))
    assert isinstance(idade, int)
    assert idade >= 20

def test_enviar_email_reset_mockado(monkeypatch):
    class MockMail:
        def send(self, msg):
            assert msg.subject.startswith("Redefinição")
            assert "Senha temporária" in msg.body
            assert msg.recipients == ["teste@exemplo.com"]
    monkeypatch.setattr("utils.mail", MockMail())
    enviar_email_reset("teste@exemplo.com", "senha123!")
