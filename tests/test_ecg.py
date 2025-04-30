import pytest
import io

@pytest.mark.parametrize('method,path', [
    ('get', '/ecg/'),
    ('post', '/ecg/upload'),
])
def test_ecg_requires_login(client, method, path):
    """GET /ecg/ e POST /ecg/upload devem exigir autenticação."""
    resp = getattr(client, method)(path)
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']

def test_list_ecgs_authenticated(authenticated_client):
    resp = authenticated_client.get('/ecg/')
    assert resp.status_code in [200, 302]  # se não houver ECGs, ainda deve carregar a página

def test_upload_ecg_missing_fields(authenticated_client):
    resp = authenticated_client.post('/ecg/upload', data={})
    assert resp.status_code == 302
    assert '/ecg/' in resp.headers['Location']

def test_upload_ecg_invalid_patient(authenticated_client):
    resp = authenticated_client.post('/ecg/upload', data={
        'patient_id': '9999'
    }, content_type='multipart/form-data')
    assert resp.status_code == 302
    assert '/ecg/' in resp.headers['Location']

def test_upload_ecg_valid(authenticated_client, app):
    # Primeiro, cria um paciente válido no banco
    from models import Patient
    with app.app_context():
        patient = Patient(name='Teste', user_id=1)
        from extensions import db
        db.session.add(patient)
        db.session.commit()
        pid = patient.id

    data = {
        'patient_id': str(pid),
        'file': (io.BytesIO(b'mock data'), 'teste_ecg.png')
    }
    resp = authenticated_client.post('/ecg/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 302
    assert '/ecg/' in resp.headers['Location']