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
from app.services.demo_service import ensure_demo_user, is_demo_user
from app.services.email_service import EmailConfigurationError, enviar_email_recuperacao, enviar_email_verificacao
from collections import defaultdict
from typing import Optional
import smtplib
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
def cookie(response: Response, name: str, value: str, max_age: Optional[int] = None):
    response.set_cookie(name, value, max_age=max_age, httponly=True, secure=settings.SECURE_COOKIES, samesite="lax", path="/")

def clear(response: Response):
    response.delete_cookie("access_token", path="/"); response.delete_cookie("refresh_token", path="/")

@router.post("/registrar", response_model=RegistroResponse, status_code=201)
def registrar(data: UsuarioCreate, service: AuthService = Depends(get_service)):
    usuario, token = service.registrar(data)
    try:
        enviado = enviar_email_verificacao(usuario.email, usuario.nome, token)
    except (EmailConfigurationError, OSError, smtplib.SMTPException):
        enviado = False
    return {"usuario": usuario, "dev_verification_token": token if settings.EMAIL_DEV_MODE else None, "email_enviado": enviado}

@router.post("/login", response_model=Token)
def login(data: LoginRequest, request: Request, response: Response, service: AuthService = Depends(get_service)):
    check_login_rate_limit(request)
    token, refresh = service.login(data)
    access_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60 if data.lembrar_me else None
    refresh_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400 if data.lembrar_me else None
    cookie(response,"access_token",token.access_token,access_age)
    cookie(response,"refresh_token",refresh,refresh_age)
    return token


@router.get("/demo")
def demo_status():
    return {"enabled": settings.DEMO_MODE}


@router.post("/demo", response_model=Token)
def demo_login(response: Response, db: Session = Depends(get_db)):
    usuario = ensure_demo_user(db)
    if usuario is None:
        raise HTTPException(404, "A demonstração não está disponível neste ambiente.")

    access = criar_access_token({"sub": usuario.email})
    refresh = criar_refresh_token({"sub": usuario.email})
    cookie(response, "access_token", access, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    cookie(response, "refresh_token", refresh, settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)
    return Token(access_token=access)


@router.post("/verificar-email")
def verificar_email(token: str, db: Session = Depends(get_db)):
    usuario=db.query(Usuario).filter(Usuario.verificacao_token_hash==hash_token(token)).first()
    if not usuario or not usuario.verificacao_token_expira_em or usuario.verificacao_token_expira_em < datetime.now(timezone.utc).replace(tzinfo=None):
        raise HTTPException(400, "Token de verificação inválido ou expirado.")
    usuario.email_verificado=True; usuario.verificacao_token_hash=None; usuario.verificacao_token_expira_em=None; db.commit()
    return {"message":"E-mail verificado com sucesso."}

@router.post("/reenviar-verificacao")
def reenviar_verificacao(data: ResendVerificationRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == data.email).first()
    resposta = {"message": "Se a conta existir e ainda estiver pendente, enviaremos um novo link."}
    if not usuario or usuario.email_verificado:
        return resposta
    token = gerar_token_aleatorio()
    usuario.verificacao_token_hash = hash_token(token)
    usuario.verificacao_token_expira_em = (datetime.now(timezone.utc) + timedelta(hours=24)).replace(tzinfo=None)
    db.commit()
    try:
        enviado = enviar_email_verificacao(usuario.email, usuario.nome, token)
    except EmailConfigurationError as exc:
        raise HTTPException(503, str(exc)) from exc
    except (OSError, smtplib.SMTPException) as exc:
        raise HTTPException(502, "Não foi possível enviar o e-mail. Tente novamente em instantes.") from exc
    if not enviado:
        resposta["dev_verification_token"] = token
    return resposta

@router.post("/refresh", response_model=Token)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    payload = decodificar_token(request.cookies.get("refresh_token", ""))
    if not payload or payload.get("type") != "refresh": raise HTTPException(401,"Sessão expirada. Entre novamente.")
    user = db.query(Usuario).filter(Usuario.email == payload.get("sub")).first()
    if not user or not user.ativo: raise HTTPException(401,"Usuário inválido.")
    access=criar_access_token({"sub":user.email}); cookie(response,"access_token",access,settings.ACCESS_TOKEN_EXPIRE_MINUTES*60)
    return Token(access_token=access)

@router.post("/logout", status_code=204)
def logout(response: Response):
    clear(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response

@router.get("/me", response_model=UsuarioResponse)
def eu(usuario_atual: Usuario = Depends(get_current_user)): return usuario_atual

@router.patch("/me", response_model=UsuarioResponse)
def atualizar_perfil(data: ProfileUpdate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if is_demo_user(usuario):
        raise HTTPException(403, "O perfil da demonstração é somente leitura.")
    usuario.nome = " ".join(data.nome.strip().split()); usuario.avatar_url = str(data.avatar_url) if data.avatar_url else None; db.commit(); db.refresh(usuario); return usuario

@router.post("/alterar-senha")
def alterar_senha(data: ChangePasswordRequest, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if is_demo_user(usuario):
        raise HTTPException(403, "A senha da demonstração não pode ser alterada.")
    if not verificar_senha(data.senha_atual, usuario.senha_hash): raise HTTPException(400,"Senha atual incorreta.")
    usuario.senha_hash=hash_senha(data.nova_senha); db.commit(); return {"message":"Senha alterada com sucesso."}

@router.post("/esqueci-senha")
def esqueci_senha(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    usuario=db.query(Usuario).filter(Usuario.email==data.email).first()
    if not usuario: return {"message":"Se o e-mail estiver cadastrado, enviaremos as instruções."}
    if is_demo_user(usuario):
        return {"message":"A conta de demonstração é restaurada automaticamente e não possui senha pública."}
    token=gerar_token_aleatorio(); usuario.reset_token_hash=hash_token(token); usuario.reset_token_expira_em=(datetime.now(timezone.utc)+timedelta(minutes=30)).replace(tzinfo=None); db.commit()
    resposta = {"message":"Se o e-mail estiver cadastrado, enviaremos as instruções de recuperação."}
    if settings.EMAIL_DEV_MODE:
        resposta["message"] = "Solicitação criada. Use o código de desenvolvimento retornado abaixo."
        resposta["dev_token"] = token
    else:
        try:
            enviar_email_recuperacao(usuario.email, usuario.nome, token)
        except (EmailConfigurationError, OSError, smtplib.SMTPException):
            # Mantém uma resposta neutra para não revelar contas cadastradas.
            pass
    return resposta

@router.post("/resetar-senha")
def resetar_senha(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash=hash_token(data.token); usuario=db.query(Usuario).filter(Usuario.reset_token_hash==token_hash).first()
    agora = datetime.now(timezone.utc).replace(tzinfo=None)
    if not usuario or not usuario.reset_token_expira_em or usuario.reset_token_expira_em < agora:
        raise HTTPException(400,"Token inválido ou expirado.")
    if is_demo_user(usuario): raise HTTPException(403,"A senha da demonstração não pode ser alterada.")
    usuario.senha_hash=hash_senha(data.nova_senha); usuario.reset_token_hash=None; usuario.reset_token_expira_em=None; db.commit(); return {"message":"Senha redefinida com sucesso."}
