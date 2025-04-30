import pytest

def test_auth_home(client):
    response = client.get('/auth/')
    assert response.status_code == 200

@pytest.mark.parametrize('path', [
    '/auth/login',
    '/auth/register',
    '/auth/faq',
    '/auth/sobre-nos',
    '/auth/termos-de-uso'
])
def test_auth_public_get_pages(client, path):
    resp = client.get(path)
    assert resp.status_code == 200

def test_auth_logout_redirects_to_login(client):
    # Sem estar logado, logout deve redirecionar para /auth/login
    resp = client.get('/auth/logout')
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']


# Testes adicionais
def test_auth_admin_requires_login(client):
    resp = client.get('/auth/admin')
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']

def test_index_redirects_to_auth_home(client):
    resp = client.get('/')
    assert resp.status_code == 302
    assert '/auth/' in resp.headers['Location']

def test_auth_post_login_invalid(client):
    resp = client.post('/auth/login', data={'email': 'x@x', 'password': 'wrong'})
    assert resp.status_code == 200
    assert b'Email ou senha' in resp.data or b'login' in resp.data

def test_auth_post_register_invalid(client):
    resp = client.post('/auth/register', data={'username': '', 'email': '', 'password': '', 'confirm': ''})
    assert resp.status_code == 200
    assert b'register' in resp.data or b'Preencha todos os campos' in resp.data

def test_auth_admin_access_denied(authenticated_client, app):
    with app.app_context():
        from extensions import db
        from models import User
        user = User.query.first()
        user.is_admin = False
        db.session.commit()

    resp = authenticated_client.get('/auth/admin')
    assert resp.status_code == 302
    assert '/patients/dashboard' in resp.headers['Location']

def test_auth_admin_access_granted_with_admin(authenticated_client, app):
    with app.app_context():
        from extensions import db
        from models import User
        user = User.query.first()
        user.is_admin = True
        db.session.commit()

    resp = authenticated_client.get('/auth/admin')
    assert resp.status_code == 200
    assert 'Usuários' in resp.get_data(as_text=True)