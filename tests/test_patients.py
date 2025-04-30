import pytest

@pytest.mark.parametrize('path', [
    '/patients/dashboard',
    '/patients/1',
    '/patients/1/edit'
])
def test_patients_requires_login(client, path):
    """Qualquer acesso a /patients/* deve redirecionar para login se não autenticado."""
    resp = client.get(path)
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']

def test_dashboard_authenticated(authenticated_client):
    resp = authenticated_client.get('/patients/dashboard')
    assert resp.status_code == 200

def test_create_patient_missing_name(authenticated_client):
    resp = authenticated_client.post('/patients/new', data={'cpf': '123'})
    assert resp.status_code == 302
    assert '/patients/dashboard' in resp.headers['Location']

def test_edit_patient_requires_authentication(client):
    resp = client.post('/patients/1/edit', data={'name': 'Novo Nome'})
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']

def test_delete_patient_requires_authentication(client):
    resp = client.post('/patients/1/delete')
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']


# Novos testes adicionados:
from models import Patient
import io

def test_create_patient_invalid_birth(authenticated_client):
    resp = authenticated_client.post('/patients/new', data={
        'name': 'Paciente Teste',
        'birth_date': 'data-invalida',
        'cpf': '000'
    })
    assert resp.status_code == 302
    assert '/patients/dashboard' in resp.headers['Location']

def test_patient_profile_redirects(authenticated_client, app):
    with app.app_context():
        patient = Patient(name='Teste', user_id=1)
        from extensions import db
        db.session.add(patient)
        db.session.commit()
        pid = patient.id

    resp = authenticated_client.get(f'/patients/{pid}')
    assert resp.status_code == 302
    assert '/patients/dashboard' in resp.headers['Location']

def test_delete_patient_valid(authenticated_client, app):
    with app.app_context():
        patient = Patient(name='Teste Del', user_id=1)
        from extensions import db
        db.session.add(patient)
        db.session.commit()
        pid = patient.id

    resp = authenticated_client.post(f'/patients/{pid}/delete')
    assert resp.status_code == 302
    assert '/patients/dashboard' in resp.headers['Location']

def test_edit_patient_valid_post(authenticated_client, app):
    with app.app_context():
        patient = Patient(name='Editar', user_id=1)
        from extensions import db
        db.session.add(patient)
        db.session.commit()
        pid = patient.id

    resp = authenticated_client.post(f'/patients/{pid}/edit', data={'name': 'Editado'})
    assert resp.status_code == 302
    assert '/patients/dashboard' in resp.headers['Location']


# Novos testes conforme solicitado:
def test_dashboard_upload_valid(authenticated_client, app):
    with app.app_context():
        from extensions import db
        db.create_all()
    data = {
        'file': (io.BytesIO(b'fake image data'), 'teste.png')
    }
    resp = authenticated_client.post('/patients/dashboard', data=data, content_type='multipart/form-data')
    assert resp.status_code == 302
    assert '/patients/dashboard' in resp.headers['Location']

def test_dashboard_upload_invalid_file(authenticated_client):
    data = {
        'file': (io.BytesIO(b'data'), 'teste.txt')  # extensão inválida
    }
    resp = authenticated_client.post('/patients/dashboard', data=data, content_type='multipart/form-data')
    assert resp.status_code == 302
    assert '/patients/dashboard' in resp.headers['Location']

def test_create_patient_valid(authenticated_client):
    data = {
        'name': 'Paciente OK',
        'birth_date': '2001-01-01',
        'cpf': '12345678900'
    }
    resp = authenticated_client.post('/patients/new', data=data)
    assert resp.status_code == 302
    assert '/patients/dashboard' in resp.headers['Location']


# Teste para edição de paciente com dados complexos
def test_edit_patient_complex_post(authenticated_client, app):
    with app.app_context():
        from models import Patient
        from extensions import db
        patient = Patient(name='Paciente Complexo', user_id=1)
        db.session.add(patient)
        db.session.commit()
        pid = patient.id

    data = {
        'name': 'Novo Nome',
        'birth_date': '1990-05-10',
        'gender': 'M',
        'race': 'Pardo',
        'email': 'email@teste.com',
        'phone': '55999999999',
        'address': 'Rua Exemplo',
        'socioeconomic': 'Alta',
        'comorbidities': ['hipertensao'],
        'history_personal': ['infarto'],
        'history_personal_others': 'asma',
        'history_family': ['diabetes'],
        'history_family_others': 'câncer',
        'smoking_status': 'nao',
        'alcohol': 'ocasional',
        'exercise': 'regular',
        'sleep_duration': '7',
        'sleep_quality': 'boa',
        'diet': 'equilibrada',
        'medications': ['enalapril'],
        'weight': '70.5',
        'height': '1.75',
        'cardiac_symptoms': ['dor_peito'],
        'cardiac_symptoms_others': 'taquicardia',
        'previous_events': ['avc'],
        'observations': 'Paciente sob tratamento.'
    }

    resp = authenticated_client.post(f'/patients/{pid}/edit', data=data)
    assert resp.status_code == 302
    assert '/patients/dashboard' in resp.headers['Location']

def test_edit_patient_invalid_weight_and_height(authenticated_client, app):
    with app.app_context():
        from models import Patient
        from extensions import db
        patient = Patient(name='Paciente Inválido', user_id=1)
        db.session.add(patient)
        db.session.commit()
        pid = patient.id

    data = {
        'name': 'Nome Atualizado',
        'weight': 'abc',  # inválido
        'height': 'xyz',  # inválido
    }
    resp = authenticated_client.post(f'/patients/{pid}/edit', data=data)
    assert resp.status_code == 302
    assert '/patients/dashboard' in resp.headers['Location']

def test_create_patient_missing_birth(authenticated_client):
    data = {
        'name': 'Sem Data',
        'cpf': '12345678900'
        # birth_date omitido
    }
    resp = authenticated_client.post('/patients/new', data=data)
    assert resp.status_code == 302
    assert '/patients/dashboard' in resp.headers['Location']

def test_dashboard_upload_missing_file(authenticated_client):
    data = {}  # sem 'file'
    resp = authenticated_client.post('/patients/dashboard', data=data)
    assert resp.status_code == 302
    assert '/patients/dashboard' in resp.headers['Location']

def test_delete_patient_without_permission(client, app):
    with app.app_context():
        from models import Patient
        from extensions import db
        patient = Patient(name='Outro Usuário', user_id=9999)
        db.session.add(patient)
        db.session.commit()
        pid = patient.id

    resp = client.post(f'/patients/{pid}/delete')
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location'] or '/patients/dashboard' in resp.headers['Location']