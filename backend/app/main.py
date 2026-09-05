from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from backend.app.core.database import Base, SessionLocal, engine
from backend.app.routers import auth
from backend.app.services.demo_service import ensure_demo_user


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


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' https: data:; "
        "connect-src 'self'; object-src 'none'; base-uri 'self'; "
        "frame-ancestors 'none'; form-action 'self'"
    )
    return response


@app.get("/health", tags=["Infraestrutura"])
def health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}


public_dir = Path(__file__).resolve().parents[2] / "frontend" / "public"

if os.getenv("VERCEL") == "1" or not public_dir.is_dir():
    # A Vercel publica public/ separadamente pela CDN.
    @app.get("/", include_in_schema=False)
    def index():
        return RedirectResponse("/index.html")
else:
    # No desenvolvimento local, o próprio FastAPI entrega o frontend.
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="public")
