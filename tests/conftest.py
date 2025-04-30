import os, sys
# Insere o diretório raiz do projeto no início do path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from extensions import db as _db

@pytest.fixture(scope='session')
def app():
    """Cria app Flask em modo TESTING com banco em memória."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False
    })
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture(scope='session')
def client(app):
    """Cliente HTTP para testes de rotas."""
    return app.test_client()

@pytest.fixture(scope='session')
def runner(app):
    """Runner para comandos CLI (flask CLI)."""
    return app.test_cli_runner()

from models import User
from werkzeug.security import generate_password_hash
from flask_login import login_user

@pytest.fixture(scope='function')
def authenticated_client(app):
    """Cliente autenticado com usuário fictício."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com',
                    password=generate_password_hash('123456'))
        _db.session.add(user)
        _db.session.commit()

    client = app.test_client()
    client.post('/auth/login', data={'email': 'test@example.com', 'password': '123456'})
    return client

@pytest.fixture(scope='function')
def db_session(app):
    """Fornece uma sessão de banco de dados limpa para cada teste."""
    with app.app_context():
        _db.session.begin_nested()
        yield _db.session
        _db.session.rollback()