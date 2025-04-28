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
