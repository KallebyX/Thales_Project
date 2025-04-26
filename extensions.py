from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate  # ✅ Adicionado!
from flask_mail import Mail

mail = Mail()
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()  # ✅ Adicionado!