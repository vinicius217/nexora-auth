from typing import Optional
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate


class UsuarioRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[Usuario]:
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def get_by_id(self, usuario_id: int) -> Optional[Usuario]:
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()

    def create(self, data: UsuarioCreate, senha_hash: str) -> Usuario:
        usuario = Usuario(nome=data.nome, email=data.email, senha_hash=senha_hash)
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
