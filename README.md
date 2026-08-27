# Nexora — Secure Identity

Sistema full-stack de autenticação criado com FastAPI, SQLAlchemy, JWT e JavaScript puro. O projeto reúne cadastro, login, recuperação de senha, edição de perfil e um dashboard responsivo em uma interface moderna.

## Funcionalidades

- Cadastro com confirmação e indicador de força da senha.
- Login com limite básico de tentativas.
- Access token e refresh token armazenados em cookies `HttpOnly`.
- Renovação automática da sessão e logout seguro.
- Verificação de e-mail simulada em desenvolvimento.
- Recuperação e redefinição de senha por token.
- Edição de nome, avatar e senha.
- Dashboard responsivo com navegação mobile.
- Modo de demonstração somente leitura para recrutadores.
- Health check para monitoramento da aplicação.
- Documentação interativa da API com Swagger.

## Tecnologias

| Camada | Tecnologias |
| --- | --- |
| Backend | Python, FastAPI e Uvicorn |
| Banco de dados | SQLite, PostgreSQL e SQLAlchemy |
| Validação | Pydantic |
| Segurança | JWT, bcrypt e cookies HttpOnly |
| Frontend | HTML5, CSS3 e JavaScript puro |

## Estrutura do projeto

```text
nexora-auth/
├── app/
│   ├── core/
│   │   ├── config.py          # Variáveis de ambiente
│   │   ├── database.py        # Engine e sessão do banco
│   │   ├── dependencies.py    # Usuário autenticado
│   │   └── security.py        # Senhas e tokens JWT
│   ├── models/usuario.py      # Tabela de usuários
│   ├── repositories/          # Consultas ao banco
│   ├── routers/auth.py        # Rotas HTTP
│   ├── schemas/usuario.py     # Entradas e respostas
│   ├── services/              # Regras de negócio
│   └── main.py                # Inicialização do FastAPI
├── static/
│   ├── css/style.css          # Design e responsividade
│   ├── js/api.js              # Cliente HTTP da interface
│   ├── index.html             # Login
│   ├── cadastro.html          # Cadastro
│   ├── recuperar.html         # Recuperação de senha
│   └── dashboard.html         # Área autenticada
├── .env.example
├── Dockerfile
├── requirements.txt
└── README.md
```

## Como o código funciona

### Inicialização

`app/main.py` cria as tabelas, registra as rotas e monta a pasta `static`. Assim, o mesmo servidor entrega a API e o frontend.

```python
app.include_router(auth.router)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

### Configuração e banco

`app/core/config.py` carrega o `.env` com `pydantic-settings`. `app/core/database.py` cria a conexão SQLAlchemy. O SQLite funciona localmente, enquanto `DATABASE_URL` pode apontar para PostgreSQL em produção.

### Cadastro e login

As rotas recebem dados validados pelos schemas Pydantic. O serviço aplica as regras de negócio e o repositório acessa o banco. Senhas nunca são salvas diretamente: `security.py` gera hashes com bcrypt.

No login, o servidor cria:

- `access_token`: token curto usado nas requisições autenticadas.
- `refresh_token`: token longo usado para renovar a sessão.

Os tokens são enviados em cookies `HttpOnly`, reduzindo a exposição ao JavaScript do navegador.

### Frontend

`static/js/api.js` centraliza as chamadas `fetch`, envia os cookies com `credentials: "include"` e padroniza mensagens, carregamento e logout. Cada HTML mantém apenas a lógica específica da tela.

`static/css/style.css` contém o design system, os componentes, o dashboard, os breakpoints responsivos e o suporte a movimento reduzido.

## Como executar

### Pré-requisitos

- Python 3.11 ou superior.
- Git para clonar o repositório.

### Windows — PowerShell

```powershell
git clone https://github.com/vinicius217/nexora-auth.git
cd nexora-auth
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload
```

Se o PowerShell bloquear a ativação:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Linux e macOS

```bash
git clone https://github.com/vinicius217/nexora-auth.git
cd nexora-auth
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload
```

Acesse:

- Aplicação: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Variáveis de ambiente

Copie `.env.example` para `.env`:

```env
APP_NAME=Nexora
ENVIRONMENT=development
DATABASE_URL=sqlite:///./login.db
SECRET_KEY=gere-uma-chave-longa-e-aleatoria
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
SECURE_COOKIES=false
DEMO_MODE=false
DEMO_USER_EMAIL=demo@nexora.dev
DEMO_USER_NAME=Nexora Demo
```

| Variável | Finalidade |
| --- | --- |
| `APP_NAME` | Nome da aplicação |
| `ENVIRONMENT` | Ambiente atual (`development` ou `production`) |
| `DATABASE_URL` | Endereço do banco |
| `SECRET_KEY` | Assinatura dos tokens |
| `ALGORITHM` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duração do acesso |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Duração da renovação |
| `SECURE_COOKIES` | Restringe cookies a HTTPS |
| `DEMO_MODE` | Ativa o acesso de demonstração sem cadastro |
| `DEMO_USER_EMAIL` | E-mail interno da conta demonstrativa |
| `DEMO_USER_NAME` | Nome exibido na conta demonstrativa |

## Endpoints principais

| Método | Rota | Descrição |
| --- | --- | --- |
| `POST` | `/auth/registrar` | Cria uma conta |
| `POST` | `/auth/login` | Autentica e cria a sessão |
| `GET` | `/auth/demo` | Informa se o modo demonstrativo está ativo |
| `POST` | `/auth/demo` | Inicia uma sessão demonstrativa |
| `POST` | `/auth/refresh` | Renova o access token |
| `POST` | `/auth/logout` | Encerra a sessão |
| `GET` | `/auth/me` | Retorna o usuário atual |
| `PATCH` | `/auth/me` | Atualiza nome e avatar |
| `POST` | `/auth/alterar-senha` | Altera a senha autenticada |
| `POST` | `/auth/esqueci-senha` | Cria um token de recuperação |
| `POST` | `/auth/resetar-senha` | Redefine a senha pelo token |
| `POST` | `/auth/verificar-email` | Confirma o e-mail pelo token |
| `GET` | `/health` | Verifica a disponibilidade do serviço |

## Publicar no Koyeb

O projeto inclui um `Dockerfile`, aceita PostgreSQL por `DATABASE_URL` e respeita a porta fornecida pela hospedagem.

### 1. Criar o banco

1. No painel do Koyeb, crie um **Database Service** PostgreSQL.
2. Copie a connection string fornecida pelo serviço.

### 2. Criar o serviço web

1. Clique em **Create Web Service** e escolha o repositório `vinicius217/nexora-auth`.
2. Selecione a branch `main` e o método de build por `Dockerfile`.
3. Escolha a instância gratuita e configure `/health` como health check.
4. Adicione as variáveis abaixo:

```env
APP_NAME=Nexora
ENVIRONMENT=production
DATABASE_URL=<connection-string-do-postgresql>
SECRET_KEY=<chave-aleatoria-longa>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
SECURE_COOKIES=true
DEMO_MODE=true
DEMO_USER_EMAIL=demo@nexora.dev
DEMO_USER_NAME=Nexora Demo
```

Gere uma `SECRET_KEY` localmente com:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Após o deploy, abra a URL terminada em `.koyeb.app`. O botão **Acessar demonstração** será exibido automaticamente na tela de login.

### 3. Atualizar o portfólio

Use a URL pública no botão principal do projeto e mantenha o GitHub como ação secundária:

```html
<a href="https://SEU-SERVICO.koyeb.app" target="_blank" rel="noopener noreferrer">
  Abrir demonstração →
</a>
```

## Segurança em produção

Antes de publicar em produção:

1. Use uma `SECRET_KEY` longa, aleatória e exclusiva.
2. Troque SQLite por PostgreSQL ou outro banco de produção.
3. Ative `SECURE_COOKIES=true` sob HTTPS.
4. Envie tokens de verificação e recuperação por e-mail; não os devolva na API.
5. Troque o rate limit em memória por Redis ou middleware dedicado.
6. Restrinja CORS, use migrações com Alembic e adicione testes automatizados.

## Licença

Projeto criado para estudo e portfólio. Sinta-se livre para estudar e adaptar o código.
