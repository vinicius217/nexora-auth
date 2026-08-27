from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.database import Base, engine
from app.routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Login",
    description="API de autenticação (JWT) com telas de login/cadastro em HTML.",
    version="0.1.0",
)

app.include_router(auth.router)

# Serve os arquivos de static/ (html, css, js). html=True faz o "/" abrir o index.html.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
