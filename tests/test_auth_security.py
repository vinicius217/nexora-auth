import unittest

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.schemas.usuario import LoginRequest, ProfileUpdate, UsuarioCreate
from app.services.auth_service import AuthService


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
        usuario, _ = self.service.registrar(
            UsuarioCreate(
                nome="Pessoa Teste",
                email="pessoa@example.com",
                senha="Senha@123",
                confirmar_senha="Senha@123",
            )
        )
        with self.assertRaises(HTTPException) as error:
            self.service.login(LoginRequest(email=usuario.email, senha="Senha@123"))
        self.assertEqual(error.exception.status_code, 403)

        usuario.email_verificado = True
        self.session.commit()
        token, refresh = self.service.login(LoginRequest(email=usuario.email, senha="Senha@123"))
        self.assertTrue(token.access_token)
        self.assertTrue(refresh)

    def test_avatar_accepts_only_http_urls(self):
        with self.assertRaises(ValidationError):
            ProfileUpdate(nome="Pessoa Teste", avatar_url="javascript:alert(1)")

        perfil = ProfileUpdate(nome="Pessoa Teste", avatar_url="https://example.com/avatar.png")
        self.assertEqual(perfil.avatar_url.scheme, "https")


if __name__ == "__main__":
    unittest.main()
