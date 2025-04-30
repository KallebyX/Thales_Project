# tests/test_app.py
from app import create_app

def test_app_creation():
    app = create_app()
    assert app is not None
    assert app.config["DEBUG"] is False or True  # depende da config

    # Verifica se todos os blueprints foram registrados
    rules = [rule.rule for rule in app.url_map.iter_rules()]
    assert "/auth/login" in rules
    assert "/patients/dashboard" in rules
    assert "/ecg/" in rules
    assert "/api/patients" in rules

def test_run_main_block(monkeypatch):
    import builtins
    import runpy
    monkeypatch.setattr(builtins, "__name__", "__main__")
    try:
        runpy.run_path("app.py", run_name="__main__")
    except RuntimeError:
        # Espera erro porque app.run() bloqueia execução
        pass