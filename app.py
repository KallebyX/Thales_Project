from flask import Flask
from config import Config
from extensions import db, login_manager, migrate, mail  # Importa tudo no início corretamente

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mail.init_app(app)
    # Inicializa as extensões
    db.init_app(app)
    login_manager.init_app(app)
    # Redirect unauthenticated users to login page
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'warning'
    migrate.init_app(app, db)

    # Registra Blueprints
    from routes import main
    app.register_blueprint(main)

    return app

# Rodar a aplicação localmente
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)