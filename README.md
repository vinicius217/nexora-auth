# Nexora — Secure Identity

Sistema full-stack de autenticação criado com FastAPI, SQLAlchemy, JWT e uma interface híbrida em HTML, JavaScript e React. O projeto reúne cadastro, login, recuperação de senha, edição de perfil e um dashboard responsivo com identidade visual própria.

**Deploy:** [nexora-auth-fs7qppwad-vinciius.vercel.app](https://nexora-auth-fs7qppwad-vinciius.vercel.app)

## Funcionalidades

- Cadastro direto com indicador de força da senha.
- Login com limite básico de tentativas.
- Access token e refresh token armazenados em cookies `HttpOnly`.
- Renovação automática da sessão e logout seguro.
- Recuperação e redefinição de senha por token.
- Edição de nome, avatar e senha.
- Dashboard responsivo com navegação mobile.
- Botão de login animado construído como componente React + TypeScript.
- Tailwind CSS isolado ao componente React para não interferir nas páginas existentes.
- Identidade visual em grafite, marfim e verde-musgo, com símbolo próprio da Nexora.
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
| Frontend | HTML5, CSS3, JavaScript, React, TypeScript e Tailwind CSS |
| Build frontend | Vite |

## Estrutura do projeto

```text
nexora-auth/
|-- backend/
|   |-- app/                # API, modelos, rotas e serviços
|   |-- migrations/         # Migrações Alembic
|   |-- tests/              # Testes Python
|   `-- requirements.txt
|-- frontend/
|   |-- public/             # HTML, CSS, JavaScript e assets React
|   |-- src/                # React e TypeScript
|   |-- package.json
|   |-- tsconfig.json
|   `-- vite.config.ts
|-- app/main.py             # Entrada de compatibilidade
|-- public/                 # Gerado pelo build, ignorado no Git
|-- package.json            # Comandos e workspace npm
|-- package-lock.json
|-- requirements.txt        # Dependências Python para deploy
|-- alembic.ini
|-- .env.example
|-- Dockerfile
|-- vercel.json
`-- README.md
```

## Como o código funciona

### Inicialização

`backend/app/main.py` cria as tabelas e registra as rotas. Localmente, o FastAPI monta a pasta `frontend/public`; na Vercel, essa pasta é entregue separadamente pela CDN e `/` é direcionado para `index.html`.

```python
app.include_router(auth.router)
if os.getenv("VERCEL") == "1":
    # A Vercel entrega public/ pela CDN.
    ...
else:
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="public")
```

### Configuração e banco

`backend/app/core/config.py` carrega o `.env` com `pydantic-settings`. `backend/app/core/database.py` cria a conexão SQLAlchemy. O SQLite funciona localmente, enquanto `DATABASE_URL` pode apontar para PostgreSQL em produção.

### Cadastro e login

As rotas recebem dados validados pelos schemas Pydantic. O serviço aplica as regras de negócio e o repositório acessa o banco. Senhas nunca são salvas diretamente: `security.py` gera hashes com bcrypt.

No login, o servidor cria:

- `access_token`: token curto usado nas requisições autenticadas.
- `refresh_token`: token longo usado para renovar a sessão.

Os tokens são enviados em cookies `HttpOnly`, reduzindo a exposição ao JavaScript do navegador.

### Frontend

`frontend/public/js/api.js` centraliza as chamadas `fetch`, envia os cookies com `credentials: "include"` e padroniza mensagens, carregamento e logout. Cada HTML mantém apenas a lógica específica da tela.

`frontend/public/css/style.css` contém o design system, os componentes, o dashboard, os breakpoints responsivos e o suporte a movimento reduzido.

O React é usado somente no botão animado de login, montado em `#login-button-root`. O componente fica em `frontend/src/components/ui/3d-button.tsx`; Vite e Tailwind geram os arquivos de `frontend/public/assets/`, que são servidos pelo mesmo FastAPI.

## Como executar

### Pré-requisitos

- Python 3.11 ou superior.
- Node.js 20 ou superior.
- Git para clonar o repositório.

### Windows — PowerShell

```powershell
git clone https://github.com/vinicius217/nexora-auth.git
cd nexora-auth
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
npm install
npm run build
Copy-Item .env.example .env
python -m uvicorn backend.app.main:app --reload
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
npm install
npm run build
cp .env.example .env
python -m uvicorn backend.app.main:app --reload
```

Acesse:

- Aplicação: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Comandos na raiz

```bash
npm run build
npm run typecheck
npm run dev:backend
npm run test:backend
python -m alembic upgrade head
```

A aplicação completa é acessada em `http://localhost:8000`. Após editar componentes React, execute `npm run build`. HTML, CSS e JavaScript em `frontend/public/` são servidos diretamente pelo FastAPI local. `npm run dev` inicia o Vite para desenvolvimento do componente.

O `.env` do backend e o banco SQLite continuam na raiz; execute os comandos Python a partir dela. O `.env.local` existente foi preservado na raiz e não é carregado pelo Vite, cuja raiz agora é `frontend/`. Para variáveis públicas do frontend, use `frontend/.env.local` com prefixo `VITE_`, sem segredos.

Antes de construir a imagem Docker, execute `npm ci` e `npm run build` para atualizar os assets React.

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

### Envio de recuperação de senha

O cadastro e o login não exigem confirmação de e-mail. Para enviar links reais de recuperação de senha, configure no `.env`:

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

No Gmail, use uma senha de app, não a senha normal da conta. Enquanto `EMAIL_DEV_MODE=true`, nenhuma mensagem real será enviada.

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
| `GET` | `/health` | Verifica a disponibilidade do serviço |

## Publicar na Vercel

O arquivo `app/main.py` exporta o FastAPI de `backend/app/main.py`. O build copia `frontend/public/` para `public/`, servido pela CDN, conforme a [documentação FastAPI da Vercel](https://vercel.com/docs/frameworks/backend/fastapi).

### 1. Importar o projeto

1. Acesse `https://vercel.com/new` e conecte sua conta do GitHub.
2. Importe o repositório `vinicius217/nexora-auth`.
3. Mantenha o diretório raiz. O `vercel.json` define `npm run build` para gerar os assets e preparar a pasta pública em cada deploy.

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
4. Envie tokens de recuperação por e-mail; não os devolva na API em produção.
5. Troque o rate limit em memória por Redis ou middleware dedicado.
6. Restrinja CORS, use migrações com Alembic e adicione testes automatizados.

## Licença

Projeto criado para estudo e portfólio. Sinta-se livre para estudar e adaptar o código.
