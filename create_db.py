#!/usr/bin/env python3
# init_db.py

from app import create_app, db

def main():
    # Cria uma instância do app Flask
    app = create_app()

    # Cria as tabelas no banco de dados
    with app.app_context():
        db.create_all()
        print("✅ Banco de dados e tabelas criados com sucesso!")

if __name__ == "__main__":
    main()
    