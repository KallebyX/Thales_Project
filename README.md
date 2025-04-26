# Meu Site ECG

Uma aplicação web para gerenciamento de dados de pacientes e exames de ECG, permitindo aos médicos e administradores cadastrar usuários, pacientes, registrar consultas e fazer upload e visualização de ECGs.

## Tecnologias Utilizadas

- **Python & Flask**: Framework web leve e extensível.
- **SQLite**: Banco de dados relacional simples, armazenado em arquivo.
- **SQLAlchemy**: ORM para manipulação de dados.
- **Alembic**: Gerenciamento de migrações de esquema de banco de dados.
- **Flask-Login**: Autenticação e controle de sessão de usuários.
- **Bootstrap & Chart.js**: Interface responsiva e gráficos interativos.
- **Werkzeug**: Utils para segurança, uploads e roteamento.

## Instalação

1. **Clone o repositório**

   ```bash
   git clone https://github.com/seu_usuario/meu_site_ecg.git
   cd meu_site_ecg
   ```

2. **Ative o ambiente virtual e instale dependências**

   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate       # Windows
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Configure variáveis de ambiente**

   Crie um arquivo `.env` na raiz com as chaves mínimas:
   ```ini
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=uma_chave_secreta_aqui
   UPLOAD_FOLDER=uploads/
   ALLOWED_EXTENSIONS=png,jpg,jpeg
   ```

4. **Prepare o banco de dados**

   ```bash
   flask db upgrade
   ```

5. **Execute a aplicação**

   ```bash
   flask run --host=0.0.0.0 --port=5001
   ```

   Acesse em `http://localhost:5001`.

## Funcionalidades

- **Cadastro de Usuários**: Registro e login de médicos e administradores.
- **Gerenciamento de Pacientes**: CRUD completo de informações de pacientes e histórico clínico.
- **Envio de ECGs**: Upload e associação de imagens de ECG a pacientes.
- **Registro de Consultas**: Formulário com dados vitais, diagnóstico e observações.
- **Painel Administrativo**: Visualização geral de usuários, pacientes e estatísticas de uso.
- **Relatórios e Gráficos**: Gráficos de uploads de ECG ao longo do tempo.

## Estrutura de Diretórios

```
meu_site_ecg/
├── app.py                   # Inicializador da aplicação
├── config.py                # Configurações e variáveis de ambiente
├── extensions.py            # Instância de extensões (db, login_manager, migrate)
├── models.py                # Definição de modelos SQLAlchemy
├── routes.py                # Definição de rotas e lógica de views
├── utils.py                 # Funções utilitárias (senha, email)
├── migrations/              # Scripts de migração Alembic
├── templates/               # Templates Jinja2 (HTML)
│   ├── base.html
│   ├── dashboard.html
│   └── ...
├── static/                  # Arquivos CSS, JS, imagens estáticas
├── uploads/                 # Armazena arquivos de ECG enviados
├── requirements.txt         # Dependências do Python
└── README.md                # (este arquivo)
```

## Contribuição

1. Faça um **fork** do projeto.
2. Crie uma **branch** para sua feature:  
   ```bash
   git checkout -b minha-feature
   ```
3. Realize seus commits:  
   ```bash
   git commit -m "Adiciona feature X"
   ```
4. Envie para o repositório remoto:  
   ```bash
   git push origin minha-feature
   ```
5. Abra um **Pull Request** no GitHub.

## Licença

Este projeto está licenciado sob a **Licença MIT**. Consulte o arquivo `LICENSE` para termos completos.

## Exemplo de Uso

1. Acesse `http://localhost:5001` e cadastre um novo usuário.
2. Faça login com suas credenciais.
3. No **Dashboard**, clique em **Cadastrar Paciente** e preencha os dados.
4. Selecione o paciente na lista e clique em **Enviar ECG** para associar um exame.
5. Visualize o gráfico de uploads ou edite/exclua pacientes diretamente.

---

Para mais detalhes, consulte a [documentação oficial do Flask](https://flask.palletsprojects.com/) e dos pacotes utilizados.

