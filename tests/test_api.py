import pytest


def test_api_patients_requires_login(client):
    resp = client.get('/api/patients')
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']


def test_api_ecgs_requires_login(client):
    resp = client.get('/api/ecgs')
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']


def test_api_patients_authenticated(authenticated_client):
    resp = authenticated_client.get('/api/patients')
    assert resp.status_code in [200, 204]  # 204 se nenhum paciente
    assert resp.is_json


def test_api_ecgs_authenticated(authenticated_client):
    resp = authenticated_client.get('/api/ecgs')
    assert resp.status_code in [200, 204]
    assert resp.is_json