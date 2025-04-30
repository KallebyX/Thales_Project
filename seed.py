from app import create_app, db
from models import User, Patient, UploadedECG
from werkzeug.security import generate_password_hash
from faker import Faker
import random
from datetime import datetime, UTC

fake = Faker()
app = create_app()

with app.app_context():
    print("Limpando dados antigos...")
    UploadedECG.query.delete()
    Patient.query.delete()
    User.query.delete()
    db.session.commit()

    print("Criando usuário admin...")
    admin = User(
        email="admin@email.com",
        password=generate_password_hash("123456"),
        username="Admin",
        is_admin=True
    )
    db.session.add(admin)
    db.session.flush()

    print("Criando pacientes e ECGs...")
    for _ in range(3):
        patient = Patient(
            name=fake.name(),
            birth_date=fake.date_of_birth(minimum_age=30, maximum_age=75),
            gender=random.choice(["Masculino", "Feminino"]),
            cpf=str(fake.unique.random_number(digits=11)),
            phone=fake.phone_number(),
            user_id=admin.id
        )
        db.session.add(patient)
        db.session.commit()

        ecg = UploadedECG(
            patient_id=patient.id,
            user_id=admin.id,
            filename=f"{fake.uuid4()}.png",
            created_at=datetime.now(UTC)
        )
        db.session.add(ecg)

    db.session.commit()
    print("Seed finalizado com sucesso.")