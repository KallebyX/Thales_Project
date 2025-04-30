from .auth     import auth_bp
from .patients import patients_bp
from .ecg      import ecg_bp
from .admin    import api_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(ecg_bp)
    app.register_blueprint(api_bp)