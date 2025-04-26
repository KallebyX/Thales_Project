import os
import time

class Config:
    # Chave secreta para proteção do Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua_chave_secreta_aqui'  # Defina uma chave secreta forte para produção!

    # Configuração do banco de dados (SQLite para desenvolvimento)
    if os.environ.get('FLASK_ENV') == 'production':
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  # Para produção, use uma variável de ambiente com o URL do banco de dados
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'  # Para desenvolvimento, usa um banco SQLite local

    # Desabilita o rastreamento de modificações no banco de dados (para melhorar performance)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pasta de upload de arquivos
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')

    # Tipos de arquivo permitidos para upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    # Controle de versão (gera uma versão única baseada no timestamp)
    VERSION = str(int(time.time()))  # 🚀 Adiciona o controle automático de versão!