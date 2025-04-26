# utils.py

import secrets
import string
from flask_mail import Message
from extensions import mail

def gerar_senha_segura(length: int = 12) -> str:
    """
    Gera uma senha aleatória com letras, dígitos e caracteres especiais.
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def enviar_email_reset(to_email: str, new_password: str) -> None:
    """
    Envia um e-mail com a nova senha ao usuário.
    Requer configuração de Flask-Mail em `extensions.mail`.
    """
    msg = Message(
        subject="Redefinição de Senha – ECG IA Primário",
        recipients=[to_email],
        body=(
            f"Sua senha foi redefinida com sucesso!\n\n"
            f"Senha temporária: {new_password}\n\n"
            "Por favor, altere-a após o primeiro login."
        )
    )
    mail.send(msg)