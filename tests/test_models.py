import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from datetime import datetime
from models import User, Patient, Consultation, UploadedECG, LoginLog, load_user
from extensions import db

def test_user_model_fields_and_methods(app):
    from extensions import db
    with app.app_context():
        user = User(
            id=1,
            username="Dr. K",
            email="k@ex.com",
            password="hashed",
            is_admin=True,
            last_login_ip="127.0.0.1"
        )
        db.session.add(user)
        db.session.commit()

        assert repr(user) == "<User Dr. K>"
        assert user.last_ip == "127.0.0.1"
        assert user.get_id() == "1"
        assert user.is_authenticated is True
        assert user.is_active is True
        assert user.is_anonymous is False

        db.session.remove()
        db.drop_all()
        db.create_all()

def test_patient_model_fields_and_methods(app):
    from extensions import db
    with app.app_context():
        patient = Patient(
            id=1,
            name="Fulano",
            user_id=1,
            cpf="12345678900",
            gender="M",
            race="Pardo",
            birth_date=datetime(2000, 1, 1),
            history_personal=["diabetes"],
            history_family=["infarto"],
            comorbidities=["obesidade"],
            previous_events=["AVC"],
            medications=["losartana"],
            created_at=datetime.utcnow()
        )
        db.session.add(patient)
        db.session.commit()

        assert repr(patient) == "<Patient Fulano>"
        assert isinstance(patient.created_at, datetime)
        assert "diabetes" in patient.history_personal
        assert "AVC" in patient.previous_events
        assert "losartana" in patient.medications

        db.session.remove()
        db.drop_all()
        db.create_all()

def test_consultation_model_fields_and_methods(app):
    from extensions import db
    with app.app_context():
        consult = Consultation(
            id=1,
            patient_id=1,
            consultation_date=datetime(2025, 1, 1),
            observations="Check",
            medications="Med1, Med2"
        )
        db.session.add(consult)
        db.session.commit()

        assert "Consultation" in repr(consult)
        assert consult.patient_id == 1
        assert "Med1" in consult.medications

        db.session.remove()
        db.drop_all()
        db.create_all()

def test_uploadedecg_model_fields_and_methods(app):
    from extensions import db
    with app.app_context():
        ecg = UploadedECG(
            id=1,
            filename="ecg01.png",
            path="/uploads/ecg01.png",
            patient_id=1,
            user_id=1,
            upload_time=datetime.utcnow()
        )
        db.session.add(ecg)
        db.session.commit()

        assert "ecg01.png" in repr(ecg)
        assert ecg.patient_id == 1
        assert ecg.user_id == 1
        assert ecg.path == "/uploads/ecg01.png"
        assert isinstance(ecg.upload_time, datetime)

        db.session.remove()
        db.drop_all()
        db.create_all()

def test_loginlog_model_fields_and_methods(app):
    from extensions import db
    with app.app_context():
        now = datetime.utcnow()
        log = LoginLog(
            id=1,
            user_id=1,
            ip_address="192.168.0.1",
            timestamp=now
        )
        db.session.add(log)
        db.session.commit()

        assert f"<LoginLog user=1 at={now}>" == repr(log)
        assert log.ip_address == "192.168.0.1"

        db.session.remove()
        db.drop_all()
        db.create_all()

def test_relationships_between_models(app):
    from extensions import db
    with app.app_context():
        user = User(username="Relacionamentos", email="rel@ex.com", password="pw")
        db.session.add(user)
        db.session.commit()

        patient = Patient(name="PacienteR", user_id=user.id)
        ecg = UploadedECG(filename="rel_ecg.png", user_id=user.id, patient=patient)
        consult = Consultation(patient=patient, consultation_date=datetime.utcnow(), notes="Check", medications="A")
        log = LoginLog(user=user, ip_address="1.1.1.1")

        db.session.add_all([patient, ecg, consult, log])
        db.session.commit()

        assert patient in user.patients
        assert ecg in user.ecgs
        assert ecg in patient.ecgs
        assert consult in patient.consultations
        assert log in user.logs

        db.session.remove()
        db.drop_all()
        db.create_all()

def test_load_user_returns_none_for_invalid_id(app):
    assert load_user("nonexistent_id") is None