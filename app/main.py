from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.database import Base, SessionLocal, engine
from app.routers import auth
from app.services.demo_service import ensure_demo_user


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        ensure_demo_user(db)
    yield

app = FastAPI(
    title="Sistema de Login",
    description="API de autenticação (JWT) com telas de login/cadastro em HTML.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth.router)


@app.get("/health", tags=["Infraestrutura"])
def health_check():
    return {"status": "ok"}


# Serve os arquivos de static/ (html, css, js). html=True faz o "/" abrir o index.html.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
