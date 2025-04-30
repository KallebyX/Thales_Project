# services/patient_service.py
from utils import calcular_risco_cardiaco


def build_patients_data(patients):
    """
    Constrói os dados serializados dos pacientes, incluindo cálculo de risco e campos adicionais.
    """
    out = []
    for p in patients:
        # Calcula risco e recupera atributos opcionais com valores padrão
        risco = calcular_risco_cardiaco(p)
        # Lista de comorbidades do paciente
        comorbs = p.comorbidities or []

        # Extrai lista de medicamentos: prioriza o atributo p.medications, caso exista; caso contrário usa última consulta
        meds = []
        # Se Patient tiver atributo 'medications'
        if hasattr(p, 'medications') and p.medications:
            raw = p.medications
            if isinstance(raw, str):
                # string CSV -> lista
                meds = [m.strip() for m in raw.split(',') if m.strip()]
            elif isinstance(raw, (list, tuple)):
                meds = list(raw)
            else:
                meds = [str(raw)]
        elif hasattr(p, 'consultations') and p.consultations:
            # fallback para última consulta
            latest = sorted(
                p.consultations,
                key=lambda c: (getattr(c, 'consultation_date', None) or getattr(c, 'created_at', None)),
                reverse=True
            )[0]
            raw = getattr(latest, 'medications', None) or []
            meds = list(raw) if isinstance(raw, (list, tuple)) else ([m.strip() for m in str(raw).split(',') if m.strip()])

        # Observações adicionais do paciente
        obs = p.observations or ''

        out.append({
            'id': p.id,
            'name': p.name,
            'cpf': p.cpf,
            'birth_date': p.birth_date.isoformat() if p.birth_date else '',
            'risk_level': risco.get('nivel_risco'),
            'risk_pontuacao': risco.get('pontuacao'),
            'risk_sugestao': risco.get('sugestao'),
            'risk_idade': risco.get('idade'),
            'comorbidities': ', '.join(comorbs) if isinstance(comorbs, (list, tuple)) else str(comorbs),
            'medications': ', '.join(meds) if isinstance(meds, (list, tuple)) else str(meds),
            'observations': obs,
        })
    return out


if __name__ == "__main__":
    from datetime import datetime

    class FakeConsultation:
        def __init__(self):
            self.medications = "aspirina, dipirona"
            self.created_at = datetime.now()

if __name__ == "__main__":
    from datetime import datetime
    # código de teste ou print para rodar build_patients_data()

    class FakeConsultation:
        def __init__(self):
            self.medications = "aspirina, dipirona"
            self.created_at = datetime.now()

    class FakePatient:
        def __init__(self):
            self.id = 1
            self.name = "Paciente Teste"
            self.cpf = "12345678900"
            self.birth_date = datetime(1990, 5, 10).date()
            self.risk_level = "moderado"
            self.risk_score = 5
            self.comorbidities = ["hipertensão", "diabetes"]
            self.medications = ["enalapril", "metformina"]
            self.observations = "Paciente em acompanhamento"
            self.consultations = [FakeConsultation()]
            self.created_at = datetime.now()
            self.updated_at = datetime.now()

            # Campos exigidos pela função de risco
            self.previous_events = ["infarto"]
            self.cardiac_symptoms = ["dor no peito"]
            self.sleep_duration = 6
            self.sleep_quality = "boa"
            self.diet = "equilibrada"
            self.smoking_status = "não"
            self.alcohol = "socialmente"
            self.exercise = "moderado"
            self.gender = "F"
            self.weight = 70
            self.height = 1.70
            self.age = 33

    pacientes = [FakePatient()]
    resultado = build_patients_data(pacientes)

    from pprint import pprint
    pprint(resultado)
