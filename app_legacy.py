from flask import Flask
from config import Config
from extensions import db, login_manager, migrate, mail

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializa extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    # Registrar blueprints
    from auth.routes     import bp as auth_bp
    from patients.routes import bp as patients_bp
    from ecg.routes      import bp as ecg_bp
    from api.routes      import api as api_bp

    app.register_blueprint(auth_bp,    url_prefix='')
    app.register_blueprint(patients_bp, url_prefix='/patients')
    app.register_blueprint(ecg_bp,      url_prefix='/ecg')
    app.register_blueprint(api_bp,      url_prefix='/api')

    return app

# Rodar a aplicação localmente
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)