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
- Documentação interativa da API com Swagger.

## Tecnologias

| Camada | Tecnologias |
| --- | --- |
| Backend | Python, FastAPI e Uvicorn |
| Banco de dados | SQLite e SQLAlchemy |
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
git clone https://github.com/SEU-USUARIO/nexora-auth.git
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
git clone https://github.com/SEU-USUARIO/nexora-auth.git
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
DATABASE_URL=sqlite:///./login.db
SECRET_KEY=gere-uma-chave-longa-e-aleatoria
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
SECURE_COOKIES=false
```

| Variável | Finalidade |
| --- | --- |
| `APP_NAME` | Nome da aplicação |
| `DATABASE_URL` | Endereço do banco |
| `SECRET_KEY` | Assinatura dos tokens |
| `ALGORITHM` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duração do acesso |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Duração da renovação |
| `SECURE_COOKIES` | Restringe cookies a HTTPS |

## Endpoints principais

| Método | Rota | Descrição |
| --- | --- | --- |
| `POST` | `/auth/registrar` | Cria uma conta |
| `POST` | `/auth/login` | Autentica e cria a sessão |
| `POST` | `/auth/refresh` | Renova o access token |
| `POST` | `/auth/logout` | Encerra a sessão |
| `GET` | `/auth/me` | Retorna o usuário atual |
| `PATCH` | `/auth/me` | Atualiza nome e avatar |
| `POST` | `/auth/alterar-senha` | Altera a senha autenticada |
| `POST` | `/auth/esqueci-senha` | Cria um token de recuperação |
| `POST` | `/auth/resetar-senha` | Redefine a senha pelo token |
| `POST` | `/auth/verificar-email` | Confirma o e-mail pelo token |

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
