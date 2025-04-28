from extensions import db, login_manager
from sqlalchemy import Index
from flask_login import UserMixin
from sqlalchemy.ext.mutable import MutableList

# ============================ #
# MODELO DE USUÁRIO (MÉDICO)   #
# ============================ #

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(150), nullable=False, unique=True)
    email         = db.Column(db.String(150), nullable=False, unique=True)
    password      = db.Column(db.String(200), nullable=False)
    is_admin      = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, server_default=db.func.now())
    last_login    = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.String(45), nullable=True)

    # Alterando o backref de 'uploader' para 'uploaded_by' para evitar o conflito
    ecgs          = db.relationship('UploadedECG', back_populates='uploader', lazy='selectin', cascade="all, delete-orphan")
    patients      = db.relationship('Patient', backref='creator', lazy='selectin', cascade="all, delete-orphan")
    logs          = db.relationship('LoginLog', backref='user', lazy='selectin', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def last_ip(self):
        return self.last_login_ip

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ============================ #
# MODELO DE PACIENTE           #
# ============================ #

class Patient(db.Model):
    __table_args__ = (
        Index('ix_patient_user_cpf', 'user_id', 'cpf'),
    )
    __tablename__ = 'patient'

    id                          = db.Column(db.Integer, primary_key=True)
    name                        = db.Column(db.String(150), nullable=False)
    birth_date                  = db.Column(db.Date, nullable=True)
    gender                      = db.Column(db.String(20), nullable=True)   # Masculino/Feminino/Outro
    race                        = db.Column(db.String(20), nullable=True)   # Branca/Negra/…
    cpf                         = db.Column(db.String(14), nullable=True)
    email                       = db.Column(db.String(150), nullable=True)
    phone                       = db.Column(db.String(20), nullable=True)
    address                     = db.Column(db.String(300), nullable=True)   # rua, cidade, estado, CEP
    socioeconomic               = db.Column(db.String(20), nullable=True)   # Baixo/Médio/Alto

    # Histórico e Hábitos
    history_personal            = db.Column(MutableList.as_mutable(db.JSON), nullable=True, default=list)         # lista de histórico pessoal
    history_personal_others     = db.Column(db.String(300), nullable=True)  # campo para outros históricos pessoais
    history_family              = db.Column(MutableList.as_mutable(db.JSON), nullable=True, default=list)         # lista de doenças familiares
    history_family_others       = db.Column(db.String(300), nullable=True)  # campo para outras doenças
    comorbidities               = db.Column(MutableList.as_mutable(db.JSON), nullable=True, default=list)         # lista de comorbidades
    previous_events             = db.Column(MutableList.as_mutable(db.JSON), nullable=True, default=list)         # lista de eventos prévios
    medications                 = db.Column(MutableList.as_mutable(db.JSON), nullable=True, default=list)  # lista de medicamentos
    smoking_status              = db.Column(db.String(50), nullable=True)   # Nunca fumou/Ex-fumante/Fumante atual
    alcohol                     = db.Column(db.String(20), nullable=True)   # Nunca/Social/Regular
    exercise                    = db.Column(db.String(100), nullable=True)   # tipo e frequência
    sleep_duration              = db.Column(db.String(50), nullable=True)   # Ex: "7 a 8 horas"
    sleep_quality               = db.Column(db.String(20), nullable=True)   # Ex: "Boa", "Regular", "Ruim"
    diet                        = db.Column(db.String(20), nullable=True)   # Saudável/Regular/Ruim

    observations                = db.Column(db.Text, nullable=True)         # Observações adicionais
    weight                      = db.Column(db.Float, nullable=True)   # peso em kg
    height                      = db.Column(db.Float, nullable=True)   # altura em metros
    cardiac_symptoms            = db.Column(MutableList.as_mutable(db.JSON), nullable=True, default=list)    # lista de sintomas
    cardiac_symptoms_others     = db.Column(db.String(300), nullable=True)  # campo para outros sintomas
    # Removidos: previous_infarction, previous_avc, previous_angioplasty, previous_cardiac_surgery
    risk_level                  = db.Column(db.String(50), nullable=True)  # Armazena classificação automática de risco

    created_at                  = db.Column(db.DateTime, server_default=db.func.now())
    user_id                     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    ecgs                        = db.relationship('UploadedECG', back_populates='patient', lazy='selectin', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient {self.name}>"


# ============================ #
# MODELO DE EXAME / CONSULTA   #
# ============================ #

class Consultation(db.Model):
    __tablename__ = 'consultation'

    id                        = db.Column(db.Integer, primary_key=True)
    patient_id                = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    user_id                   = db.Column(db.Integer, db.ForeignKey('user.id'),    nullable=False)
    consultation_date         = db.Column(db.Date,    nullable=False)
    blood_pressure            = db.Column(db.String(20), nullable=True)   # ex. “120x80 mmHg”
    heart_rate                = db.Column(db.Integer,      nullable=True)  # bpm
    weight                    = db.Column(db.Float,        nullable=True)  # kg
    height                    = db.Column(db.Float,        nullable=True)  # m
    bmi                       = db.Column(db.Float,        nullable=True)
    diagnosis                 = db.Column(db.String(200),  nullable=True)
    comorbidities             = db.Column(db.String(200),  nullable=True)  # ex. DPOC, IR…
    prior_surgery             = db.Column(db.String(200),  nullable=True)  # Sim/Não + detalhes
    medications               = db.Column(db.JSON,         nullable=True, default=list)  # Nome + dose
    allergies                 = db.Column(db.Text,         nullable=True)
    stress_level              = db.Column(db.Boolean,      default=False)  # Sim/Não
    regular_care              = db.Column(db.Boolean,      default=False)  # Acesso a cuidados?
    technical_observations    = db.Column(db.Text,         nullable=True)
    created_at                = db.Column(db.DateTime,     server_default=db.func.now())

    patient                   = db.relationship('Patient',      backref=db.backref('consultations', lazy='selectin'))
    user                      = db.relationship('User',         backref=db.backref('consultations', lazy='selectin'))

    def __repr__(self):
        return f"<Consultation {self.consultation_date} – Patient {self.patient_id}>"


# ============================ #
# MODELO DE ECG ENVIADO        #
# ============================ #

class UploadedECG(db.Model):
    __table_args__ = (
        Index('ix_ecg_user_patient', 'user_id', 'patient_id'),
    )
    __tablename__ = 'uploaded_ecg'

    id          = db.Column(db.Integer, primary_key=True)
    filename    = db.Column(db.String(255), nullable=False)
    upload_time = db.Column(db.DateTime, server_default=db.func.now())
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_id  = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)  # Certifique-se de que esta linha está presente!

    uploader    = db.relationship('User', back_populates='ecgs', lazy='selectin')
    patient     = db.relationship('Patient', back_populates='ecgs', lazy='selectin')

    def __repr__(self):
        return f"<UploadedECG {self.filename} for Patient {self.patient_id}>"


# ============================ #
# MODELO DE LOG DE ACESSO      #
# ============================ #

class LoginLog(db.Model):
    __tablename__ = 'login_log'

    id          = db.Column(db.Integer,   primary_key=True)
    user_id     = db.Column(db.Integer,   db.ForeignKey('user.id'), nullable=False)
    timestamp   = db.Column(db.DateTime,  server_default=db.func.now())
    ip_address  = db.Column(db.String(45), nullable=True)

    def __repr__(self):
        return f"<LoginLog user={self.user_id} at={self.timestamp}>"