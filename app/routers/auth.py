from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.core.security import decodificar_token, criar_access_token, criar_refresh_token, hash_senha, verificar_senha, gerar_token_aleatorio, hash_token
from app.models.usuario import Usuario
from app.schemas.usuario import *
from app.services.auth_service import AuthService
from collections import defaultdict
import time

_login_attempts = defaultdict(list)
def check_login_rate_limit(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time.time(); window = 60
    _login_attempts[ip] = [t for t in _login_attempts[ip] if now-t < window]
    if len(_login_attempts[ip]) >= 10: raise HTTPException(429, "Muitas tentativas. Aguarde um minuto e tente novamente.")
    _login_attempts[ip].append(now)

router = APIRouter(prefix="/auth", tags=["Autenticação"])
def get_service(db: Session = Depends(get_db)): return AuthService(db)
def cookie(response: Response, name: str, value: str, max_age: int):
    response.set_cookie(name, value, max_age=max_age, httponly=True, secure=settings.SECURE_COOKIES, samesite="lax", path="/")

def clear(response: Response):
    response.delete_cookie("access_token", path="/"); response.delete_cookie("refresh_token", path="/")

@router.post("/registrar", response_model=RegistroResponse, status_code=201)
def registrar(data: UsuarioCreate, service: AuthService = Depends(get_service)):
    usuario, token = service.registrar(data)
    return {"usuario": usuario, "dev_verification_token": token}

@router.post("/login", response_model=Token)
def login(data: LoginRequest, request: Request, response: Response, service: AuthService = Depends(get_service)):
    check_login_rate_limit(request)
    token, refresh = service.login(data); days = settings.REFRESH_TOKEN_EXPIRE_DAYS if data.lembrar_me else 0
    cookie(response,"access_token",token.access_token, settings.ACCESS_TOKEN_EXPIRE_MINUTES*60 if days else 0)
    cookie(response,"refresh_token",refresh, days*86400 if days else settings.REFRESH_TOKEN_EXPIRE_DAYS*86400)
    return token


@router.post("/verificar-email")
def verificar_email(token: str, db: Session = Depends(get_db)):
    usuario=db.query(Usuario).filter(Usuario.verificacao_token_hash==hash_token(token)).first()
    if not usuario or not usuario.verificacao_token_expira_em or usuario.verificacao_token_expira_em < datetime.now(timezone.utc).replace(tzinfo=None):
        raise HTTPException(400, "Token de verificação inválido ou expirado.")
    usuario.email_verificado=True; usuario.verificacao_token_hash=None; usuario.verificacao_token_expira_em=None; db.commit()
    return {"message":"E-mail verificado com sucesso."}

@router.post("/refresh", response_model=Token)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    payload = decodificar_token(request.cookies.get("refresh_token", ""))
    if not payload or payload.get("type") != "refresh": raise HTTPException(401,"Sessão expirada. Entre novamente.")
    user = db.query(Usuario).filter(Usuario.email == payload.get("sub")).first()
    if not user or not user.ativo: raise HTTPException(401,"Usuário inválido.")
    access=criar_access_token({"sub":user.email}); cookie(response,"access_token",access,settings.ACCESS_TOKEN_EXPIRE_MINUTES*60)
    return Token(access_token=access)

@router.post("/logout", status_code=204)
def logout(response: Response): clear(response); return Response(status_code=204)

@router.get("/me", response_model=UsuarioResponse)
def eu(usuario_atual: Usuario = Depends(get_current_user)): return usuario_atual

@router.patch("/me", response_model=UsuarioResponse)
def atualizar_perfil(data: ProfileUpdate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    usuario.nome = " ".join(data.nome.strip().split()); usuario.avatar_url = data.avatar_url; db.commit(); db.refresh(usuario); return usuario

@router.post("/alterar-senha")
def alterar_senha(data: ChangePasswordRequest, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verificar_senha(data.senha_atual, usuario.senha_hash): raise HTTPException(400,"Senha atual incorreta.")
    usuario.senha_hash=hash_senha(data.nova_senha); db.commit(); return {"message":"Senha alterada com sucesso."}

@router.post("/esqueci-senha")
def esqueci_senha(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    usuario=db.query(Usuario).filter(Usuario.email==data.email).first()
    if not usuario: return {"message":"Se o e-mail estiver cadastrado, enviaremos as instruções."}
    token=gerar_token_aleatorio(); usuario.reset_token_hash=hash_token(token); usuario.reset_token_expira_em=(datetime.now(timezone.utc)+timedelta(minutes=30)).replace(tzinfo=None); db.commit()
    # Em produção, este token deve ser enviado por e-mail e nunca devolvido na API.
    return {"message":"Solicitação criada. Em ambiente de desenvolvimento, use o token retornado abaixo.", "dev_token":token}

@router.post("/resetar-senha")
def resetar_senha(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash=hash_token(data.token); usuario=db.query(Usuario).filter(Usuario.reset_token_hash==token_hash).first()
    if not usuario: raise HTTPException(400,"Token inválido.")
    usuario.senha_hash=hash_senha(data.nova_senha); usuario.reset_token_hash=None; usuario.reset_token_expira_em=None; db.commit(); return {"message":"Senha redefinida com sucesso."}
