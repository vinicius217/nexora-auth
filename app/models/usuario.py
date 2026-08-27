from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    email_verificado = Column(Boolean, default=False, nullable=False)
    avatar_url = Column(String(500), nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    ultimo_login = Column(DateTime(timezone=True), nullable=True)
    reset_token_hash = Column(String(255), nullable=True)
    reset_token_expira_em = Column(DateTime(timezone=True), nullable=True)
    verificacao_token_hash = Column(String(255), nullable=True)
    verificacao_token_expira_em = Column(DateTime(timezone=True), nullable=True)
