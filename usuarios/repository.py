from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError

from app import db
from personas.models import Persona
from usuarios.models import Usuario
from exceptions import DatabaseError, DuplicateError, NotFoundError
from repo_base import commit_or_raise


class UsuarioRepository:

    def crear(self, data: dict) -> Usuario:
        persona = db.session.get(Persona, data["persona_id"])
        if persona is None:
            raise NotFoundError(
                f"No existe una Persona con id={data['persona_id']}."
            )

        if persona.usuarios:
            raise DuplicateError(
                f"La Persona con id={data['persona_id']} ya tiene un Usuario asociado."
            )

        usuario = Usuario(
            persona_id=data["persona_id"],
            username=data["username"],
            password_hash="",
        )
        usuario.set_password(data["password"])

        db.session.add(usuario)
        commit_or_raise()
        return usuario

    def listar_todos(self) -> list:
        try:
            return Usuario.query.all()
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

    def obtener_por_id(self, id: int):
        try:
            return db.session.get(Usuario, id)
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

    def actualizar(self, id: int, data: dict):
        usuario = self.obtener_por_id(id)
        if usuario is None:
            return None

        if "username" in data:
            usuario.username = data["username"]

        if "password" in data:
            usuario.set_password(data["password"])

        usuario.updated_at = datetime.now(timezone.utc)
        commit_or_raise()
        return usuario

    def eliminar(self, id: int) -> bool:
        usuario = self.obtener_por_id(id)
        if usuario is None:
            return False

        db.session.delete(usuario)
        commit_or_raise()
        return True
