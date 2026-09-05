from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.core.dependencies import get_current_user
from backend.app.core.security import decodificar_token, criar_access_token, criar_refresh_token, hash_senha, verificar_senha, gerar_token_aleatorio, hash_token
from backend.app.models.usuario import Usuario, Sessao
from backend.app.schemas.usuario import *
from backend.app.services.auth_service import AuthService
from backend.app.services.demo_service import ensure_demo_user, is_demo_user
from backend.app.services.email_service import EmailConfigurationError, enviar_email_recuperacao, enviar_email_verificacao
from collections import defaultdict
from typing import Optional
import smtplib
import time
import secrets
from backend.app.core.rate_limit import limiter

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

def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    return forwarded or (request.client.host if request.client else "unknown")

def create_session(db: Session, usuario: Usuario, request: Request) -> tuple[str, Sessao]:
    jti = secrets.token_hex(16)
    agora = datetime.now(timezone.utc).replace(tzinfo=None)
    sessao = Sessao(
        usuario_id=usuario.id,
        refresh_jti_hash=hash_token(jti),
        user_agent=request.headers.get("user-agent", "")[:300],
        ip_address=client_ip(request)[:64],
        ultima_atividade_em=agora,
        expira_em=agora + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(sessao); db.commit(); db.refresh(sessao)
    return criar_refresh_token({"sub": usuario.email, "sid": sessao.id}, jti), sessao

@router.post("/registrar", response_model=RegistroResponse, status_code=201)
def registrar(data: UsuarioCreate, request: Request, service: AuthService = Depends(get_service)):
    limiter.check(f"register:{client_ip(request)}", 5, 3600)
    usuario, token = service.registrar(data)
    enviado = False
    try:
        enviado = enviar_email_verificacao(usuario.email, usuario.nome, token)
    except (EmailConfigurationError, OSError, smtplib.SMTPException):
        pass
    return {"usuario": usuario, "dev_verification_token": token if settings.EMAIL_DEV_MODE else None, "email_enviado": enviado}

@router.post("/login", response_model=Token)
def login(data: LoginRequest, request: Request, response: Response, service: AuthService = Depends(get_service)):
    limiter.check(f"login:{client_ip(request)}:{data.email.lower()}", 10, 60)
    token, _ = service.login(data)
    usuario = service.repository.get_by_email(data.email)
    refresh, _ = create_session(service.db, usuario, request)
    access_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60 if data.lembrar_me else None
    refresh_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400 if data.lembrar_me else None
    cookie(response,"access_token",token.access_token,access_age)
    cookie(response,"refresh_token",refresh,refresh_age)
    return token


@router.get("/demo")
def demo_status():
    return {"enabled": settings.DEMO_MODE}


@router.post("/demo", response_model=Token)
def demo_login(request: Request, response: Response, db: Session = Depends(get_db)):
    usuario = ensure_demo_user(db)
    if usuario is None:
        raise HTTPException(404, "A demonstração não está disponível neste ambiente.")

    access = criar_access_token({"sub": usuario.email})
    refresh, _ = create_session(db, usuario, request)
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
def reenviar_verificacao(data: ResendVerificationRequest, request: Request, db: Session = Depends(get_db)):
    limiter.check(f"verify:{client_ip(request)}:{data.email.lower()}", 3, 900)
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
    sessao = db.query(Sessao).filter(Sessao.id == payload.get("sid"), Sessao.refresh_jti_hash == hash_token(payload.get("jti", "")), Sessao.revogada_em.is_(None)).first()
    agora = datetime.now(timezone.utc).replace(tzinfo=None)
    if not sessao or sessao.expira_em < agora: raise HTTPException(401,"Sessão expirada. Entre novamente.")
    user = db.query(Usuario).filter(Usuario.email == payload.get("sub"), Usuario.id == sessao.usuario_id).first()
    if not user or not user.ativo: raise HTTPException(401,"Usuário inválido.")
    sessao.revogada_em = agora; db.commit()
    refresh_token, _ = create_session(db, user, request)
    access=criar_access_token({"sub":user.email}); cookie(response,"access_token",access,settings.ACCESS_TOKEN_EXPIRE_MINUTES*60); cookie(response,"refresh_token",refresh_token,settings.REFRESH_TOKEN_EXPIRE_DAYS*86400)
    return Token(access_token=access)

@router.post("/logout", status_code=204)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    payload = decodificar_token(request.cookies.get("refresh_token", ""))
    if payload and payload.get("sid"):
        sessao = db.query(Sessao).filter(Sessao.id == payload["sid"]).first()
        if sessao: sessao.revogada_em = datetime.now(timezone.utc).replace(tzinfo=None); db.commit()
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
    usuario.senha_hash=hash_senha(data.nova_senha)
    db.query(Sessao).filter(Sessao.usuario_id == usuario.id, Sessao.revogada_em.is_(None)).update({"revogada_em": datetime.now(timezone.utc).replace(tzinfo=None)})
    db.commit(); return {"message":"Senha alterada com sucesso. Entre novamente nos seus dispositivos."}

@router.get("/sessoes", response_model=list[SessionResponse])
def listar_sessoes(request: Request, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    payload = decodificar_token(request.cookies.get("refresh_token", "")) or {}
    atual = payload.get("sid")
    agora = datetime.now(timezone.utc).replace(tzinfo=None)
    sessoes = db.query(Sessao).filter(Sessao.usuario_id == usuario.id, Sessao.revogada_em.is_(None), Sessao.expira_em > agora).order_by(Sessao.ultima_atividade_em.desc()).all()
    return [SessionResponse(id=s.id, user_agent=s.user_agent, ip_address=s.ip_address, criada_em=s.criada_em, ultima_atividade_em=s.ultima_atividade_em, expira_em=s.expira_em, atual=s.id == atual) for s in sessoes]

@router.delete("/sessoes/{sessao_id}", status_code=204)
def revogar_sessao(sessao_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    sessao = db.query(Sessao).filter(Sessao.id == sessao_id, Sessao.usuario_id == usuario.id, Sessao.revogada_em.is_(None)).first()
    if not sessao: raise HTTPException(404, "Sessão não encontrada.")
    sessao.revogada_em = datetime.now(timezone.utc).replace(tzinfo=None); db.commit()

@router.post("/esqueci-senha")
def esqueci_senha(data: ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)):
    limiter.check(f"recovery:{client_ip(request)}:{data.email.lower()}", 3, 900)
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
