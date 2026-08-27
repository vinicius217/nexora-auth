import secrets

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_senha
from app.models.usuario import Usuario


def ensure_demo_user(db: Session) -> Usuario | None:
    """Create and restore the shared recruiter demo account when enabled."""
    if not settings.DEMO_MODE:
        return None

    email = settings.DEMO_USER_EMAIL.strip().lower()
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if usuario is None:
        usuario = Usuario(
            nome=settings.DEMO_USER_NAME,
            email=email,
            senha_hash=hash_senha(secrets.token_urlsafe(32)),
        )
        db.add(usuario)

    usuario.nome = settings.DEMO_USER_NAME
    usuario.ativo = True
    usuario.email_verificado = True
    usuario.avatar_url = None
    usuario.reset_token_hash = None
    usuario.reset_token_expira_em = None
    usuario.verificacao_token_hash = None
    usuario.verificacao_token_expira_em = None
    db.commit()
    db.refresh(usuario)
    return usuario


def is_demo_user(usuario: Usuario) -> bool:
    return settings.DEMO_MODE and usuario.email.lower() == settings.DEMO_USER_EMAIL.lower()
