from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError

from app import db
from sistemas.models import Sistema
from exceptions import DatabaseError, DuplicateError
from repo_base import commit_or_raise


class SistemaRepository:

    def crear(self, data: dict) -> Sistema:
        sistema = Sistema(
            nombre=data["nombre"],
            descripcion=data.get("descripcion"),
        )
        db.session.add(sistema)
        commit_or_raise(f"Ya existe un Sistema con el nombre '{data['nombre']}'.")
        return sistema

    def listar_todos(self) -> list:
        try:
            return Sistema.query.order_by(Sistema.id).all()
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

    def obtener_por_id(self, id: int):
        try:
            return db.session.get(Sistema, id)
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

    def actualizar(self, id: int, data: dict):
        sistema = self.obtener_por_id(id)
        if sistema is None:
            return None

        if "nombre" in data:
            sistema.nombre = data["nombre"]
        if "descripcion" in data:
            sistema.descripcion = data["descripcion"]

        sistema.updated_at = datetime.now(timezone.utc)
        commit_or_raise(f"Ya existe un Sistema con el nombre '{data.get('nombre')}'.")
        return sistema

    def eliminar(self, id: int) -> bool:
        sistema = self.obtener_por_id(id)
        if sistema is None:
            return False

        if sistema.permisos:
            raise DuplicateError(
                f"El Sistema con id={id} tiene permisos asociados y no puede eliminarse."
            )

        db.session.delete(sistema)
        commit_or_raise()
        return True
