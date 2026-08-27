from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decodificar_token
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)
def get_current_user(request: Request, token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    token = token or request.cookies.get("access_token")
    invalid = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida ou expirada.", headers={"WWW-Authenticate":"Bearer"})
    if not token: raise invalid
    payload = decodificar_token(token)
    if not payload or payload.get("type") != "access" or not payload.get("sub"): raise invalid
    usuario = UsuarioRepository(db).get_by_email(payload["sub"])
    if not usuario or not usuario.ativo: raise invalid
    return usuario
