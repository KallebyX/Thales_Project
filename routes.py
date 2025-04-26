from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from werkzeug.utils import secure_filename
import os

from extensions import db
from models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

# Função utilitária para checar extensões de arquivos permitidas
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# Página inicial
@main.route('/')
def home():
    return render_template('home.html')

# Cadastro de usuário
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('E-mail já cadastrado. Faça login.', 'warning')
            return redirect(url_for('main.login'))

        total_users = User.query.count()
        is_admin = True if total_users == 0 else False

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, email=email, password=hashed_password, is_admin=is_admin)

        db.session.add(new_user)
        db.session.commit()

        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

# Login de usuário
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login realizado com sucesso! Seja bem-vindo.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('E-mail ou senha incorretos. Tente novamente.', 'danger')
            return redirect(url_for('main.login'))

    return render_template('login.html')

# Dashboard (área do usuário)
@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado.', 'warning')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('Nenhum arquivo selecionado.', 'warning')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            flash('Imagem de ECG enviada com sucesso!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Formato de arquivo inválido. Aceitamos apenas PNG, JPG e JPEG.', 'danger')
            return redirect(request.url)

    return render_template('dashboard.html', user=current_user)

# Painel de administração
@main.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Acesso negado!', 'danger')
        return redirect(url_for('main.dashboard'))

    users = User.query.all()
    return render_template('admin.html', users=users)

# Logout de usuário
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('main.home'))