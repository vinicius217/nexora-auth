import unittest
from fastapi import HTTPException

from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.database import Base
from backend.app.schemas.usuario import LoginRequest, ProfileUpdate, UsuarioCreate
from backend.app.services.auth_service import AuthService
from backend.app.core.rate_limit import RateLimiter


class AuthSecurityTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.service = AuthService(self.session)

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_login_requires_verified_email(self):
        usuario, token_verificacao = self.service.registrar(
            UsuarioCreate(
                nome="Pessoa Teste",
                email="pessoa@example.com",
                senha="Senha@123",
                confirmar_senha="Senha@123",
            )
        )
        self.assertTrue(token_verificacao)
        self.assertFalse(usuario.email_verificado)
        with self.assertRaises(HTTPException) as contexto:
            self.service.login(LoginRequest(email=usuario.email, senha="Senha@123"))
        self.assertEqual(contexto.exception.status_code, 403)

    def test_registration_rejects_repeated_password_pattern(self):
        with self.assertRaises(HTTPException) as contexto:
            self.service.registrar(UsuarioCreate(nome="Pessoa Teste", email="fraca@example.com", senha="aaaaaaaa", confirmar_senha="aaaaaaaa"))
        self.assertEqual(contexto.exception.status_code, 400)

    def test_avatar_accepts_only_http_urls(self):
        with self.assertRaises(ValidationError):
            ProfileUpdate(nome="Pessoa Teste", avatar_url="javascript:alert(1)")

        perfil = ProfileUpdate(nome="Pessoa Teste", avatar_url="https://example.com/avatar.png")
        self.assertEqual(perfil.avatar_url.scheme, "https")

    def test_rate_limiter_rejects_after_limit(self):
        limiter = RateLimiter()
        limiter.check("login:test", 2, 60)
        limiter.check("login:test", 2, 60)
        with self.assertRaises(HTTPException) as contexto:
            limiter.check("login:test", 2, 60)
        self.assertEqual(contexto.exception.status_code, 429)
        self.assertIn("Retry-After", contexto.exception.headers)


if __name__ == "__main__":
    unittest.main()
