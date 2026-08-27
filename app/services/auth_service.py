from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import hash_senha, verificar_senha, criar_access_token, criar_refresh_token, gerar_token_aleatorio, hash_token
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import UsuarioCreate, LoginRequest, Token

class AuthService:
    def __init__(self, db: Session): self.repository = UsuarioRepository(db); self.db = db
    def registrar(self, data: UsuarioCreate) -> tuple[Usuario, str]:
        if data.senha != data.confirmar_senha: raise HTTPException(400, "As senhas não coincidem.")
        if len(set(data.senha)) < 4: raise HTTPException(400, "Escolha uma senha mais forte.")
        if self.repository.get_by_email(data.email): raise HTTPException(400, "Já existe um usuário cadastrado com esse e-mail.")
        usuario = self.repository.create(data, hash_senha(data.senha))
        token = gerar_token_aleatorio(); usuario.verificacao_token_hash = hash_token(token); usuario.verificacao_token_expira_em = datetime.now(timezone.utc)+timedelta(hours=24); self.db.commit(); self.db.refresh(usuario)
        return usuario, token
    def login(self, data: LoginRequest) -> tuple[Token, str]:
        usuario = self.repository.get_by_email(data.email)
        invalid = HTTPException(401, "E-mail ou senha inválidos.", headers={"WWW-Authenticate":"Bearer"})
        if not usuario or not verificar_senha(data.senha, usuario.senha_hash): raise invalid
        if not usuario.ativo: raise HTTPException(403, "Usuário desativado.")
        usuario.ultimo_login = datetime.now(timezone.utc); self.db.commit()
        access = criar_access_token({"sub":usuario.email}); refresh = criar_refresh_token({"sub":usuario.email})
        return Token(access_token=access), refresh
