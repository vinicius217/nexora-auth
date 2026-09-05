from datetime import datetime, timedelta, timezone
from typing import Optional
import hashlib, secrets
import bcrypt
from jose import JWTError, jwt
from backend.app.core.config import settings

def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")
def verificar_senha(senha_digitada: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha_digitada.encode("utf-8")[:72], senha_hash.encode("utf-8"))
def criar_token(dados: dict, minutos: int, tipo: str, jti: str | None = None) -> str:
    payload = dados.copy(); payload.update({"exp": datetime.now(timezone.utc)+timedelta(minutes=minutos), "type": tipo, "jti": jti or secrets.token_hex(16)})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
def criar_access_token(dados: dict, expires_delta: Optional[timedelta] = None) -> str:
    minutos = int((expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).total_seconds()/60)
    return criar_token(dados, minutos, "access")
def criar_refresh_token(dados: dict, jti: str | None = None) -> str:
    return criar_token(dados, settings.REFRESH_TOKEN_EXPIRE_DAYS*24*60, "refresh", jti)
def decodificar_token(token: str) -> Optional[dict]:
    try: return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError: return None
def gerar_token_aleatorio(): return secrets.token_urlsafe(32)
def hash_token(token: str): return hashlib.sha256(token.encode()).hexdigest()
