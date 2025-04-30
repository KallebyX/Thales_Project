from flask import Flask, redirect, url_for
from config import Config
from extensions import db, login_manager, migrate, mail

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializa extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    # Redirect unauthorized users to the login page
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Você precisa estar logado para acessar esta página.'
    mail.init_app(app)

    # Rota raiz redireciona para a home do módulo de autenticação
    @app.route('/')
    def index():
        return redirect(url_for('auth.home'))

    from routes import register_blueprints
    register_blueprints(app)

    return app

# Rodar a aplicação localmente
if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5001, debug=True)