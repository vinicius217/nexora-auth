from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, HttpUrl, ConfigDict, Field, field_validator

class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=72)
    confirmar_senha: str = Field(min_length=8, max_length=72)
    @field_validator("nome")
    @classmethod
    def nome_valido(cls, v):
        v = " ".join(v.strip().split())
        if len(v) < 2: raise ValueError("Informe seu nome completo.")
        return v

class UsuarioResponse(BaseModel):
    id: int; nome: str; email: EmailStr; ativo: bool; email_verificado: bool
    avatar_url: Optional[str] = None; criado_em: datetime; ultimo_login: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str
    lembrar_me: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ForgotPasswordRequest(BaseModel): email: EmailStr
class ResendVerificationRequest(BaseModel): email: EmailStr
class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20)
    nova_senha: str = Field(min_length=8, max_length=72)
class ChangePasswordRequest(BaseModel):
    senha_atual: str
    nova_senha: str = Field(min_length=8, max_length=72)
class ProfileUpdate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    avatar_url: Optional[HttpUrl] = Field(default=None, max_length=500)

class RegistroResponse(BaseModel):
    usuario: UsuarioResponse
    dev_verification_token: Optional[str] = None
    email_enviado: bool = False
