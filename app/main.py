from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
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


public_dir = Path(__file__).resolve().parent.parent / "public"

if os.getenv("VERCEL") == "1" or not public_dir.is_dir():
    # A Vercel publica public/ separadamente pela CDN.
    @app.get("/", include_in_schema=False)
    def index():
        return RedirectResponse("/index.html")
else:
    # No desenvolvimento local, o próprio FastAPI entrega o frontend.
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="public")
