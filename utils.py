# utils.py

import secrets
import string
from flask_mail import Message
from extensions import mail
import logging

# Pesos e limites para cálculo de risco
RISK_WEIGHTS = {
    'idade_masc': {'threshold': 55, 'weight': 2},
    'idade_fem': {'threshold': 65, 'weight': 2},
    'Hipertensão arterial sistêmica': 2,
    'Diabetes mellitus tipo 1': 3,
    'Diabetes mellitus tipo 2': 3,
    'Dislipidemia': 2,
    'Obesidade': 2,
    'Doença renal crônica': 3,
    'Doença arterial periférica': 3,
    'Doença arterial coronariana': 4,
    'Fibrilação atrial': 2,
    'tabagismo': 2,
    'sedentarismo': 1,
    'imc_obesidade': 2,
    'evento_previo': 4,
    'hist_familiar': 2
}

def gerar_senha_segura(length: int = 12) -> str:
    """
    Gera uma senha aleatória com letras, dígitos e caracteres especiais.
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def enviar_email_reset(to_email: str, new_password: str) -> None:
    """
    Envia um e-mail com a nova senha ao usuário.
    Requer configuração de Flask-Mail em `extensions.mail`.
    """
    msg = Message(
        subject="Redefinição de Senha – ECG IA Primário",
        recipients=[to_email],
        body=(
            f"Sua senha foi redefinida com sucesso!\n\n"
            f"Senha temporária: {new_password}\n\n"
            "Por favor, altere-a após o primeiro login."
        )
    )
    try:
        mail.send(msg)
    except Exception as e:
        logging.error(f"Falha ao enviar email de reset para {to_email}: {e}")

from datetime import date

def calcular_idade(birth_date):
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def calcular_risco_cardiaco(patient):
    """
    Calcula o risco cardiovascular do paciente baseado nas novas estruturas de dados (comorbidades, hábitos, etc).
    Adaptado das diretrizes SBC/ESC.
    """
    if not patient:
        return {
            "pontuacao": 0,
            "nivel_risco": "Desconhecido",
            "sugestao": "Paciente não encontrado.",
            "idade": None
        }

    pontuacao = 0
    # --- Normalize patient lists for case-insensitive matching ---
    comorbs = [c.strip().lower() for c in (patient.comorbidities or [])]
    eventos = [e.strip().lower() for e in (patient.previous_events or [])]
    history_raw = patient.history_family if isinstance(patient.history_family, list) else ([patient.history_family] if patient.history_family else [])
    history_family = [h.strip().lower() for h in history_raw]

    # Breakdown scores
    idade_score = comorb_score = tabaco_score = exerc_score = imc_score = eventos_score = famil_score = 0

    # 1. Idade
    idade = calcular_idade(patient.birth_date) if patient.birth_date else None
    if idade:
        if (patient.gender == "Masculino" and idade >= RISK_WEIGHTS['idade_masc']['threshold']):
            pontuacao += RISK_WEIGHTS['idade_masc']['weight']
            idade_score = RISK_WEIGHTS['idade_masc']['weight']
        elif (patient.gender == "Feminino" and idade >= RISK_WEIGHTS['idade_fem']['threshold']):
            pontuacao += RISK_WEIGHTS['idade_fem']['weight']
            idade_score = RISK_WEIGHTS['idade_fem']['weight']

    # 2. Comorbidades (agora lista) — loop genérico
    comorb_score = 0
    for cond, weight in RISK_WEIGHTS.items():
        # pular entradas não numéricas (e.g. thresholds)
        if isinstance(weight, dict):
            continue
        # comparar sem case-sensitive
        if cond.lower() in comorbs:
            pontuacao += weight
            comorb_score += weight

    # 3. Hábitos (tabagismo e exercício)
    if hasattr(patient, 'smoking_status') and patient.smoking_status and isinstance(patient.smoking_status, str):
        if "fumante" in patient.smoking_status.lower():
            pontuacao += RISK_WEIGHTS['tabagismo']
            tabaco_score = RISK_WEIGHTS['tabagismo']

    if patient.exercise and isinstance(patient.exercise, str):
        exercise = patient.exercise.lower()
        if "nunca" in exercise or "nenhuma" in exercise or "não" in exercise:
            pontuacao += RISK_WEIGHTS['sedentarismo']
            exerc_score = RISK_WEIGHTS['sedentarismo']

    # 4. IMC baseado em peso e altura
    if patient.weight and patient.height:
        imc = patient.weight / (patient.height ** 2)
        if imc >= 30:
            pontuacao += RISK_WEIGHTS['imc_obesidade']
            imc_score = RISK_WEIGHTS['imc_obesidade']

    # 5. Histórico de eventos prévios
    event_terms = ["infarto prévio", "avc prévio", "angioplastia prévia", "cirurgia cardíaca prévia"]
    if any(term in eventos for term in event_terms):
        pontuacao += RISK_WEIGHTS['evento_previo']
        eventos_score = RISK_WEIGHTS['evento_previo']

    # 6. Histórico familiar positivo
    for entry in history_family:
        if any(keyword in entry for keyword in ["infarto", "avc", "cardíaco", "coronário"]):
            pontuacao += RISK_WEIGHTS['hist_familiar']
            famil_score = RISK_WEIGHTS['hist_familiar']
            break

    # Classificação de risco
    if pontuacao <= 2:
        nivel_risco = "Baixo risco"
        sugestao = "Recomendar manutenção de hábitos saudáveis e acompanhamento periódico."
    elif 3 <= pontuacao <= 5:
        nivel_risco = "Risco moderado"
        sugestao = "Incentivar controle rigoroso dos fatores de risco e acompanhamento mais frequente."
    elif 6 <= pontuacao <= 8:
        nivel_risco = "Alto risco"
        sugestao = "Necessário intervenção clínica ativa para controle dos fatores de risco."
    else:
        nivel_risco = "Muito alto risco"
        sugestao = "Paciente deve ser encaminhado para avaliação cardiológica especializada."

    breakdown = {
        'idade': idade_score,
        'comorbidades': comorb_score,
        'tabagismo': tabaco_score,
        'sedentarismo': exerc_score,
        'imc_obesidade': imc_score,
        'evento_previo': eventos_score,
        'hist_familiar': famil_score
    }

    logging.debug(
        f"Paciente {getattr(patient, 'id', '?')} — idade:{idade_score}, "
        f"comorb:{comorb_score}, tabagismo:{tabaco_score}, sedentarismo:{exerc_score}, "
        f"imc:{imc_score}, evento:{eventos_score}, familiar:{famil_score} "
        f"=> total pontuacao={pontuacao}"
    )

    return {
        "pontuacao": pontuacao,
        "nivel_risco": nivel_risco,
        "sugestao": sugestao,
        "idade": idade,
        "breakdown": breakdown
    }