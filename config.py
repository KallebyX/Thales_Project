import os
import time
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Chave secreta para proteção do Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua_chave_secreta_aqui'  # Defina uma chave secreta forte para produção!

    # Configuração do banco de dados (SQLite local)
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'instance', 'database.db')}"  # Banco de dados local SQLite

    # Desabilita o rastreamento de modificações no banco de dados (para melhorar performance)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pasta de upload de arquivos
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "instance", "uploads")

    # Tipos de arquivo permitidos para upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    # Controle de versão (gera uma versão única baseada no timestamp)
    VERSION = str(int(time.time()))  # 🚀 Adiciona o controle automático de versão!