import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import Patient, UploadedECG
from services.patient_service import build_patients_data
from utils import calcular_risco_cardiaco
from datetime import datetime
from collections import Counter

bp = Blueprint('patients', __name__)

# Permitir apenas arquivos de imagem
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required

def dashboard():
    # Tratamento de upload de ECG
    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Pasta de uploads (configuração em config.py)
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'instance/uploads')
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            # Persistir no banco
            ecg = UploadedECG(
                filename=filename,
                path=filepath,
                user_id=current_user.id,
                upload_time=datetime.utcnow()
            )
            db.session.add(ecg)
            db.session.commit()
            flash('ECG enviado com sucesso!', 'success')
        else:
            flash('Formato inválido. Use PNG ou JPG.', 'warning')
        return redirect(url_for('patients.dashboard'))

    # Leitura de dados para exibição
    patients = Patient.query.filter_by(user_id=current_user.id) \
                              .order_by(Patient.created_at.desc()) \
                              .all()
    ecgs = UploadedECG.query.filter_by(user_id=current_user.id) \
                               .order_by(UploadedECG.upload_time.desc()) \
                               .all()

    # Serialização para gráficos e relatórios
    patients_data = build_patients_data(patients)
    for entry, p in zip(patients_data, patients):
        risco = calcular_risco_cardiaco(p)
        entry['risk_level'] = risco.get('nivel_risco', 'Não calculado')
        entry['risk_pontuacao'] = risco.get('pontuacao', 'Indisponível')

    total_pacientes = len(patients)
    total_ecgs = len(ecgs)
    last_ecg = ecgs[0] if ecgs else None

    dates = [e.upload_time.date() for e in ecgs]
    counts = Counter(dates)
    sorted_dates = sorted(counts.keys())
    chart_labels = [d.strftime('%d/%m/%Y') for d in sorted_dates]
    chart_data = [counts[d] for d in sorted_dates]

    return render_template(
        'dashboard.html',
        user=current_user,
        patients=patients,
        ecgs=ecgs,
        total_pacientes=total_pacientes,
        total_ecgs=total_ecgs,
        last_ecg=last_ecg,
        chart_labels=chart_labels,
        chart_data=chart_data,
        patients_data=patients_data
    )

@bp.route('/new', methods=['POST'])
@login_required

def create_patient():
    name  = request.form.get('name')
    birth = request.form.get('birth_date')
    cpf   = request.form.get('cpf')
    if not name:
        flash('Nome é obrigatório.', 'warning')
        return redirect(url_for('patients.dashboard'))

    bd = None
    if birth:
        try:
            bd = datetime.strptime(birth, '%Y-%m-%d').date()
        except ValueError:
            flash('Data inválida.', 'warning')
            return redirect(url_for('patients.dashboard'))

    patient = Patient(
        name=name,
        birth_date=bd,
        cpf=cpf,
        user_id=current_user.id
    )
    db.session.add(patient)
    db.session.commit()
    flash('Paciente criado!', 'success')
    return redirect(url_for('patients.dashboard'))

@bp.route('/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required

def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if patient.user_id != current_user.id and not current_user.is_admin:
        flash('Sem permissão.', 'danger')
        return redirect(url_for('patients.dashboard'))

    if request.method == 'POST':
        # Dados pessoais
        patient.name = request.form.get('name') or patient.name
        birth = request.form.get('birth_date')
        if birth:
            try:
                patient.birth_date = datetime.strptime(birth, '%Y-%m-%d').date()
            except ValueError:
                flash('Data inválida.', 'warning')
                return redirect(url_for('patients.edit_patient', patient_id=patient_id))

        patient.gender         = request.form.get('gender') or patient.gender
        patient.race           = request.form.get('race') or patient.race
        patient.email          = request.form.get('email') or patient.email
        patient.phone          = request.form.get('phone') or patient.phone
        patient.address        = request.form.get('address') or patient.address
        patient.socioeconomic  = request.form.get('socioeconomic') or patient.socioeconomic

        # Comorbidades e histórico
        patient.comorbidities             = request.form.getlist('comorbidities') or []
        patient.history_personal          = request.form.getlist('history_personal') or []
        patient.history_personal_others   = request.form.get('history_personal_others') or patient.history_personal_others
        patient.history_family            = request.form.getlist('history_family') or []
        patient.history_family_others     = request.form.get('history_family_others') or patient.history_family_others

        # Hábitos e estilo de vida
        patient.smoking_status = request.form.get('smoking_status') or patient.smoking_status
        patient.alcohol        = request.form.get('alcohol') or patient.alcohol
        patient.exercise       = request.form.get('exercise') or patient.exercise
        patient.sleep_duration = request.form.get('sleep_duration') or patient.sleep_duration
        patient.sleep_quality  = request.form.get('sleep_quality') or patient.sleep_quality
        patient.diet           = request.form.get('diet') or patient.diet

        # Medicamentos
        patient.medications    = request.form.getlist('medications') or []

        # Sinais vitais
        weight = request.form.get('weight')
        if weight:
            try:
                patient.weight = float(weight)
            except ValueError:
                pass
        height = request.form.get('height')
        if height:
            try:
                patient.height = float(height)
            except ValueError:
                pass

        # Sintomas e eventos prévios
        patient.cardiac_symptoms         = request.form.getlist('cardiac_symptoms') or []
        patient.cardiac_symptoms_others  = request.form.get('cardiac_symptoms_others') or patient.cardiac_symptoms_others
        patient.previous_events          = request.form.getlist('previous_events') or []

        # Observações gerais
        patient.observations = request.form.get('observations') or patient.observations

        db.session.commit()
        flash('Paciente atualizado!', 'success')
        return redirect(url_for('patients.dashboard'))

    current_date = datetime.utcnow().strftime('%Y-%m-%d')
    return render_template('edit.patient.html', patient=patient, current_date=current_date)

@bp.route('/<int:patient_id>/delete', methods=['POST'])
@login_required

def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if patient.user_id != current_user.id and not current_user.is_admin:
        flash('Sem permissão.', 'danger')
        return redirect(url_for('patients.dashboard'))

    db.session.delete(patient)
    db.session.commit()
    flash('Paciente excluído com sucesso!', 'success')
    return redirect(url_for('patients.dashboard'))

@bp.route('/<int:patient_id>')
@login_required

def patient_profile(patient_id):
    # Redireciona para o dashboard
    return redirect(url_for('patients.dashboard'))