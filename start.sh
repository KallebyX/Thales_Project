#!/usr/bin/env bash
# start.sh – inicializa o ambiente, opcionalmente limpa o DB e sobe o Flask

set -e

echo "🔵 Ativando ambiente virtual..."
if [[ -z "$VIRTUAL_ENV" ]]; then
  source venv/bin/activate
else
  echo "✅ Ambiente virtual já ativo."
fi

echo "🟡 Exportando variáveis de ambiente do Flask..."
export FLASK_APP=app.py
export FLASK_ENV=development

if [[ "$1" == "fresh" ]]; then
  echo "⚠️  Limpando banco existente..."
  rm -f meu_site_ecg.db

  echo "🛠️  Recriando todas as tabelas via db.create_all()..."
  python - <<PYCODE
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print("✅ Tabelas recriadas com sucesso!")
PYCODE

  echo "🚀 Iniciando servidor (modo FRESH: sem migrações Alembic)..."
  flask run --host=0.0.0.0 --port=5001 --reload
  exit 0
fi

echo "🟢 Aplicando migrações ao banco de dados (Alembic)..."
flask db upgrade

echo "🚀 Iniciando servidor em http://0.0.0.0:5001  (reload ativo)…"
flask run --host=0.0.0.0 --port=5001 --reload