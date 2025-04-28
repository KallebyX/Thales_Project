# ECG IA Primário

Uma aplicação web completa para gerenciamento de dados de pacientes, consultas clínicas e exames de ECG, voltada a profissionais de saúde (médicos, enfermeiros, agentes) e administradores.

## Tecnologias Utilizadas

- **Python & Flask**: Framework web leve e extensível.
- **SQLite**: Banco de dados relacional simples, arquivo local em `instance/`.
- **SQLAlchemy**: ORM para modelagem e manipulação de dados.
- **Alembic**: Controle de migrações de esquema de banco.
- **Flask-Login**: Autenticação e controle de sessão de usuários.
- **Flask-Mail**: Envio de e-mails (confirmação, redefinição de senha).
- **Bootstrap & Chart.js**: UI responsiva e gráficos interativos.
- **Werkzeug**: Utilitários de segurança, uploads e roteamento.

## Funcionalidades

- **Cadastro de Usuários**: Registro, login, permissões (admin ou usuário comum).
- **Painel do Usuário**:
  - Dashboard com métricas de pacientes cadastrados, uploads de ECG e gráficos de atividade.
  - CRUD completo de Pacientes, incluindo histórico clínico, comorbidades, hábitos, sinais vitais e medicamentos.
  - Upload de imagens de ECG associadas ao paciente.
  - Modal de relatório clínico com cálculo de risco cardiovascular (segundo diretrizes SBC/ESC) e exportação em PDF.
- **Consultas**: Registro de consultas médicas (data, diagnósticos, prescrições) e associação automática de medicamentos.
- **Painel Administrativo** (apenas para admins):
  - Visualização de todos os usuários, estatísticas de crescimento e ações (promover, banir, editar).
  - Acesso restrito via role admin.

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu_usuario/Thales_Project.git
   cd Thales_Project
   ```

2. Crie e ative o ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\\Scripts\\activate     # Windows
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Configure variáveis de ambiente (`.env` na raiz):
   ```ini
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=sua_chave_secreta
   MAIL_SERVER=smtp.example.com
   MAIL_USERNAME=usuario
   MAIL_PASSWORD=senha
   UPLOAD_FOLDER=uploads/
   ALLOWED_EXTENSIONS=png,jpg,jpeg
   ```

4. Inicialize o banco de dados e aplique migrações:
   ```bash
   flask db init      # só na primeira instalação
   flask db migrate -m "Cria esquema inicial"
   flask db upgrade
   ```

5. Execute a aplicação:
   ```bash
   flask run --host=0.0.0.0 --port=5001
   ```

   Acesse em http://localhost:5001

## Estrutura de Diretórios

```text
Thales_Project/
├── app.py                 # Criação do app e registro de blueprints
├── config.py              # Classes de configuração
├── extensions.py          # Instâncias de db, migrate, login_manager, mail
├── models.py              # Modelos SQLAlchemy (User, Patient, Consultation, ECG)
├── services/              # Lógica de negócio (risco, relatórios)
│   └── patient_service.py
├── utils.py               # Funções auxiliares (cálculo de risco, formatadores)
├── migrations/            # Scripts Alembic
├── templates/             # Templates Jinja2 (HTML)
├── static/                # CSS, JS, imagens estáticas
├── instance/              # Configurações locais e database.db
├── uploads/               # Armazenamento de ECGs enviados
├── requirements.txt       # Dependências Python
└── README.md              # Documentação do projeto
```

## Uso Básico

1. Abra **Início** e cadastre-se como usuário.
2. Faça **login** e acesse seu Dashboard.
3. **Cadastrar Paciente**: preencha dados pessoais e clínicos.
4. **Registrar Consulta**: dentro do perfil, registre sinais vitais, histórico e medicamentos.
5. **Enviar ECG**: no Dashboard, carregue imagens e visualize no painel.
6. **Relatório**: clique no ícone de relatório para abrir modal com dados, cálculo de risco e exportação.

## Contribuição

1. Fork e clone o projeto.
2. Crie uma branch: `git checkout -b feature/minha-feature`
3. Commit e push:
   ```bash
   git commit -m "Descrição da feature"
   git push origin feature/minha-feature
   ```
4. Abra um Pull Request.

## Licença

Este projeto está sob a Licença MIT. Veja `LICENSE` para detalhes.

