# Nexora — Secure Identity

Sistema full-stack de autenticação criado com FastAPI, SQLAlchemy, JWT e JavaScript puro. O projeto reúne cadastro, login, recuperação de senha, edição de perfil e um dashboard responsivo em uma interface moderna.

## Funcionalidades

- Cadastro com confirmação e indicador de força da senha.
- Login com limite básico de tentativas.
- Access token e refresh token armazenados em cookies `HttpOnly`.
- Renovação automática da sessão e logout seguro.
- Verificação de e-mail simulada em desenvolvimento.
- Reenvio de verificação e tela de confirmação com feedback visual.
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
├── public/
│   ├── css/style.css          # Design e responsividade
│   ├── js/api.js              # Cliente HTTP da interface
│   ├── index.html             # Login
│   ├── cadastro.html          # Cadastro
│   ├── recuperar.html         # Recuperação de senha
│   ├── verificar.html         # Confirmação de e-mail
│   └── dashboard.html         # Área autenticada
├── .env.example
├── .python-version
├── Dockerfile
├── requirements.txt
├── vercel.json
└── README.md
```

## Como o código funciona

### Inicialização

`app/main.py` cria as tabelas e registra as rotas. Localmente, o FastAPI monta a pasta `public`; na Vercel, essa pasta é entregue separadamente pela CDN e `/` é direcionado para `index.html`.

```python
app.include_router(auth.router)
if os.getenv("VERCEL") == "1":
    # A Vercel entrega public/ pela CDN.
    ...
else:
    app.mount("/", StaticFiles(directory="public", html=True), name="public")
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

`public/js/api.js` centraliza as chamadas `fetch`, envia os cookies com `credentials: "include"` e padroniza mensagens, carregamento e logout. Cada HTML mantém apenas a lógica específica da tela.

`public/css/style.css` contém o design system, os componentes, o dashboard, os breakpoints responsivos e o suporte a movimento reduzido.

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
| `DATABASE_URL` | Endereço do banco usado localmente ou em outros provedores |
| `NEON_DATABASE_URL` | Endereço com pooler criado pela integração Neon e usado com prioridade |
| `NEON_URL` | Nome alternativo aceito para uma conexão Neon |
| `SECRET_KEY` | Assinatura dos tokens |
| `ALGORITHM` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duração do acesso |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Duração da renovação |
| `SECURE_COOKIES` | Restringe cookies a HTTPS |
| `DEMO_MODE` | Ativa o acesso de demonstração sem cadastro |
| `DEMO_USER_EMAIL` | E-mail interno da conta demonstrativa |
| `DEMO_USER_NAME` | Nome exibido na conta demonstrativa |

### Envio real de e-mail

Para enviar a confirmação ao endereço cadastrado, configure no `.env`:

```env
APP_URL=http://localhost:8000
EMAIL_DEV_MODE=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-app
SMTP_FROM_EMAIL=seu-email@gmail.com
SMTP_FROM_NAME=Nexora
SMTP_USE_TLS=true
```

No Gmail, use uma senha de app, não a senha normal da conta. Enquanto `EMAIL_DEV_MODE=true`, o projeto mantém o atalho local de desenvolvimento e não envia mensagens reais.

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
| `POST` | `/auth/reenviar-verificacao` | Gera um novo token de confirmação |

## Publicar na Vercel

O projeto usa um ponto de entrada FastAPI reconhecido pela Vercel, inclui os arquivos públicos no bundle da função e está preparado para PostgreSQL serverless.

### 1. Importar o projeto

1. Acesse `https://vercel.com/new` e conecte sua conta do GitHub.
2. Importe o repositório `vinicius217/nexora-auth`.
3. Mantenha o diretório raiz e as configurações de build detectadas automaticamente.

### 2. Criar o banco Neon

1. Dentro do projeto na Vercel, abra **Storage** e clique em **Create Database**.
2. Selecione **Neon Postgres** e o plano gratuito.
3. Conecte o banco ao projeto. A integração adicionará as credenciais ao ambiente.
4. Use `NEON` como **Custom Prefix**. A integração criará `NEON_DATABASE_URL`, que tem prioridade sobre uma `DATABASE_URL` já existente e utiliza pooler para execução serverless.

### 3. Configurar o ambiente

Em **Settings → Environment Variables**, adicione as variáveis abaixo para Production, Preview e Development:

```env
APP_NAME=Nexora
ENVIRONMENT=production
NEON_DATABASE_URL=<connection-string-criada-pela-integracao>
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

Depois de salvar as variáveis, faça um novo deploy. A URL terminará em `.vercel.app` e o botão **Acessar demonstração** será exibido automaticamente.

### 4. Atualizar o portfólio

Use a URL pública no botão principal do projeto e mantenha o GitHub como ação secundária:

```html
<a href="https://SEU-PROJETO.vercel.app" target="_blank" rel="noopener noreferrer">
  Abrir demonstração →
</a>
```

## Hospedagem alternativa com Docker

O `Dockerfile` continua disponível para serviços compatíveis com contêineres, como Koyeb, Render ou uma infraestrutura própria.

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
