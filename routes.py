from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from utils import gerar_senha_segura, enviar_email_reset
from models import User, UploadedECG, Patient, LoginLog
from datetime import datetime
from collections import Counter
import os

main = Blueprint('main', __name__)

def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_EXTENSIONS', set())
    )

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email    = request.form['email']
        password = request.form['password']
        if not all([username, email, password]):
            flash('Preencha todos os campos.', 'warning')
            return redirect(url_for('main.register'))
        if User.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.', 'warning')
            return redirect(url_for('main.login'))
        hashed = generate_password_hash(password, method='pbkdf2:sha256')
        is_admin = (User.query.count() == 0)
        u = User(username=username, email=email, password=hashed, is_admin=is_admin)
        db.session.add(u)
        db.session.commit()
        flash('Cadastro ok, faça login.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']
        user     = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            user.last_login    = datetime.utcnow()
            user.last_login_ip = request.remote_addr
            db.session.commit()
            log = LoginLog(user_id=user.id, ip_address=request.remote_addr)
            db.session.add(log)
            db.session.commit()
            flash('Bem-vindo!', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Email ou senha inválidos.', 'danger')
    return render_template('login.html')

@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    # Upload de ECG vinculado a paciente
    if request.method == 'POST':
        pid = request.form.get('patient_id')
        file = request.files.get('file')
        if not pid or not file or not allowed_file(file.filename):
            flash('Selecione paciente e arquivo válido.', 'warning')
            return redirect(url_for('main.dashboard'))
        patient = Patient.query.get(pid)
        if not patient or patient.user_id != current_user.id:
            flash('Paciente inválido.', 'danger')
            return redirect(url_for('main.dashboard'))
        fn = secure_filename(file.filename)
        fp = os.path.join(current_app.config['UPLOAD_FOLDER'], fn)
        file.save(fp)
        ecg = UploadedECG(filename=fn, user_id=current_user.id, patient_id=pid)
        db.session.add(ecg)
        db.session.commit()
        flash('ECG enviado!', 'success')
        return redirect(url_for('main.dashboard'))

    # Dados para exibição
    patients = Patient.query.filter_by(user_id=current_user.id).order_by(Patient.created_at.desc()).all()
    ecgs     = UploadedECG.query.filter_by(user_id=current_user.id).order_by(UploadedECG.upload_time.desc()).all()

    # Serializa pacientes para uso em JSON no template
    patients_data = [
        {
            'id': p.id,
            'name': p.name,
            'cpf': p.cpf,
            'birth_date': p.birth_date.strftime('%Y-%m-%d') if p.birth_date else None,
            'gender': p.gender or '',
            'race': p.race or '',
            'phone': p.phone or '',
            'email': p.email or '',
            'address': p.address or '',
            'socioeconomic': p.socioeconomic or ''
        }
        for p in patients
    ]

    total_pacientes = len(patients)
    total_ecgs       = len(ecgs)
    last_ecg         = ecgs[0] if ecgs else None

    # Monta dados do gráfico
    dates = [e.upload_time.date() for e in ecgs]
    counts = Counter(dates)
    sorted_dates = sorted(counts.keys())
    chart_labels = [d.strftime('%d/%m/%Y') for d in sorted_dates]
    chart_data   = [counts[d] for d in sorted_dates]

    return render_template('dashboard.html',
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

@main.route('/cadastro-paciente', methods=['POST'])
@login_required
def cadastro_paciente():
    name = request.form.get('name')
    birth = request.form.get('birth_date')
    cpf   = request.form.get('cpf')
    email = request.form.get('email')
    phone = request.form.get('phone')
    if not name:
        flash('Nome é obrigatório.', 'warning')
        return redirect(url_for('main.dashboard'))
    if cpf and Patient.query.filter_by(cpf=cpf).first():
        flash('CPF já cadastrado.', 'warning')
        return redirect(url_for('main.dashboard'))
    bd = None
    if birth:
        try:
            bd = datetime.strptime(birth, '%Y-%m-%d').date()
        except ValueError:
            flash('Data inválida.', 'warning')
            return redirect(url_for('main.dashboard'))
    p = Patient(name=name, birth_date=bd, cpf=cpf, email=email, phone=phone, user_id=current_user.id)
    db.session.add(p);
    db.session.commit()
    flash('Paciente criado!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/edit-patient/<int:patient_id>', methods=['GET','POST'])
@login_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if patient.user_id != current_user.id and not current_user.is_admin:
        flash('Sem permissão.', 'danger')
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        patient.name  = request.form.get('name') or patient.name
        bd = request.form.get('birth_date')
        if bd:
            try:
                patient.birth_date = datetime.strptime(bd, '%Y-%m-%d').date()
            except ValueError:
                flash('Data inválida.', 'warning')
                return redirect(url_for('main.edit_patient', patient_id=patient.id))
        for field in ['gender','race','cpf','email','phone','address','socioeconomic',
                      'history_personal','history_family','smoking','alcohol','exercise','sleep','diet']:
            setattr(patient, field, request.form.get(field))
        patient.hypertension = bool(request.form.get('hypertension'))
        patient.diabetes     = bool(request.form.get('diabetes'))
        patient.dyslipidemia = bool(request.form.get('dyslipidemia'))
        patient.obesity      = bool(request.form.get('obesity'))
        patient.observations = request.form.get('observations')
        db.session.commit()
        flash('Paciente atualizado!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('edit_patient.html', patient=patient)

@main.route('/pacientes')
@login_required
def pacientes():
    patients = Patient.query.filter_by(user_id=current_user.id).order_by(Patient.created_at.desc()).all()
    return render_template('pacientes.html', patients=patients)

@main.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('main.login'))
    # Dados de usuários
    users = User.query.order_by(User.created_at.desc()).all()
    # Estatísticas de crescimento de usuários
    created_dates = [u.created_at.date() for u in users]
    counts = Counter(created_dates)
    sorted_dates = sorted(counts.keys())
    labels = [d.strftime('%d/%m/%Y') for d in sorted_dates]
    data = [counts[d] for d in sorted_dates]
    user_growth = {'labels': labels, 'data': data}
    return render_template('admin_dashboard.html', users=users, user_growth=user_growth)

@main.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.admin_dashboard'))
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Não é possível deletar um administrador.', 'warning')
        return redirect(url_for('main.admin_dashboard'))
    db.session.delete(user)
    db.session.commit()
    flash(f'Usuário "{user.username}" excluído.', 'success')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/promote-user/<int:user_id>', methods=['POST'])
@login_required
def promote_user(user_id):
    if not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.admin_dashboard'))
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        user.is_admin = True
        db.session.commit()
        flash(f'Usuário "{user.username}" promovido.', 'success')
    else:
        flash('Usuário já é administrador.', 'info')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/demote-user/<int:user_id>', methods=['POST'])
@login_required
def demote_user(user_id):
    if not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.admin_dashboard'))
    user = User.query.get_or_404(user_id)
    if user.is_admin and user.id != current_user.id:
        user.is_admin = False
        db.session.commit()
        flash(f'Usuário "{user.username}" despromovido.', 'success')
    elif user.id == current_user.id:
        flash('Não é possível despromover a si mesmo.', 'warning')
    else:
        flash('Usuário já não é administrador.', 'info')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/reset-password/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    if not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.dashboard'))
    user = User.query.get_or_404(user_id)
    nova_senha = gerar_senha_segura()
    user.password = generate_password_hash(nova_senha, method='pbkdf2:sha256')
    db.session.commit()
    enviar_email_reset(user.email, nova_senha)
    flash(f'Senha de "{user.username}" redefinida e enviada.', 'success')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/sobre-nos')
def sobre_nos():
    return render_template('sobre_nos.html')

@main.route('/termos-de-uso')
def termos_de_uso():
    return render_template('termos_uso.html')

@main.route('/faq')
def faq():
    return render_template('faq.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('main.home'))

@main.route('/delete-patient/<int:patient_id>', methods=['POST'])
@login_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    # Only allow owner or admin to delete
    if patient.user_id != current_user.id and not current_user.is_admin:
        flash('Sem permissão para excluir este paciente.', 'danger')
        return redirect(url_for('main.dashboard'))
    db.session.delete(patient)
    db.session.commit()
    flash('Paciente excluído com sucesso!', 'success')
    return redirect(url_for('main.dashboard'))