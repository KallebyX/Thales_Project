# Variáveis
APP_NAME=thales_project
PORT=5000

# Comando para construir a imagem Docker
build:
	docker build -t $(APP_NAME) .

# Comando para rodar o container Docker
up:
	docker run -it --rm -p $(PORT):5000 --name $(APP_NAME) $(APP_NAME)

# Build + Run
start: build up

# Remove containers parados e imagens dangling
clean:
	docker system prune -af

# Testes com pytest
test:
	pytest --maxfail=1 --disable-warnings -q

# Testes com cobertura e HTML
coverage:
	coverage run -m pytest && coverage report -m

# Abre o relatório HTML no navegador
coverage-html:
	coverage html && open htmlcov/index.html

# Testes com docker (assume que requirements estão no container)
docker-test:
	docker run --rm $(APP_NAME) pytest

# Entra no bash do container
bash:
	docker run -it --rm $(APP_NAME) /bin/bash

# Executa o seed do banco
seed:
	python seed.py

# Gera uma nova migration
migrate:
	flask db migrate -m "migration automática"

# Aplica a migration ao banco
upgrade:
	flask db upgrade

# Apaga o banco e recria do zero
reset-db:
	rm -f instance/*.db
	flask db downgrade base
	flask db upgrade
	python seed.py