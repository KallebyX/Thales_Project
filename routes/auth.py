from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User, LoginLog
from utils import gerar_senha_segura, enviar_email_reset
from datetime import datetime
from collections import Counter

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/')
def home():
    return render_template('home.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if not all([username, email, password]):
            flash('Preencha todos os campos.', 'warning')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.', 'warning')
            return redirect(url_for('auth.login'))
        hashed = generate_password_hash(password, method='pbkdf2:sha256')
        is_admin = (User.query.count() == 0)
        user = User(username=username, email=email, password=hashed, is_admin=is_admin)
        db.session.add(user)
        db.session.commit()
        flash('Cadastro ok, faça login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            user.last_login = datetime.utcnow()
            user.last_login_ip = request.remote_addr
            db.session.commit()
            log = LoginLog(user_id=user.id, ip_address=request.remote_addr)
            db.session.add(log)
            db.session.commit()
            flash('Bem-vindo!', 'success')
            return redirect(url_for('patients.dashboard'))
        flash('Email ou senha inválidos.', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('auth.home'))

@auth_bp.route('/sobre-nos')
def sobre_nos():
    return render_template('sobre_nos.html')

@auth_bp.route('/termos-de-uso')
def termos_de_uso():
    return render_template('termos_uso.html')

@auth_bp.route('/faq')
def faq():
    return render_template('faq.html')

@auth_bp.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('patients.dashboard'))
    users = User.query.order_by(User.created_at.desc()).all()
    created_dates = [u.created_at.date() for u in users]
    counts = Counter(created_dates)
    sorted_dates = sorted(counts.keys())
    labels = [d.strftime('%d/%m/%Y') for d in sorted_dates]
    data = [counts[d] for d in sorted_dates]
    user_growth = {'labels': labels, 'data': data}
    return render_template('admin_dashboard.html', users=users, user_growth=user_growth)