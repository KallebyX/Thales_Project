from models import Patient
from extensions import db

# Atualizar todos os pacientes
patients = Patient.query.all()
for patient in patients:
    if not isinstance(patient.history_family, list):
        patient.history_family = []
    if not isinstance(patient.history_personal, list):
        patient.history_personal = []
    if not isinstance(patient.cardiac_symptoms, list):
        patient.cardiac_symptoms = []
    if not isinstance(patient.comorbidities, list):
        patient.comorbidities = []
    if not isinstance(patient.previous_events, list):
        patient.previous_events = []
    if not isinstance(patient.medications, list):
        patient.medications = []
db.session.commit()

print('Pacientes corrigidos!')