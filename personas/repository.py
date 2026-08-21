from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError

from app import db
from personas.models import Persona
from exceptions import DatabaseError, DuplicateError
from repo_base import commit_or_raise


class PersonaRepository:

    def crear(self, data: dict) -> Persona:
        from datetime import date

        persona = Persona(
            nombre=data["nombre"],
            apellido=data["apellido"],
            documento=data["documento"],
            fecha_nacimiento=(
                date.fromisoformat(data["fecha_nacimiento"])
                if isinstance(data["fecha_nacimiento"], str)
                else data["fecha_nacimiento"]
            ),
            email=data["email"],
            activo=data.get("activo", True),
        )
        db.session.add(persona)
        commit_or_raise("Ya existe una Persona con el mismo documento o email.")
        return persona

    def listar_activos(self) -> list:
        try:
            return Persona.query.filter_by(activo=True).all()
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

    def obtener_por_id(self, id: int):
        try:
            return db.session.get(Persona, id)
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

    def actualizar(self, id: int, data: dict):
        from datetime import date

        persona = self.obtener_por_id(id)
        if persona is None:
            return None

        campos_modificables = {
            "nombre",
            "apellido",
            "documento",
            "fecha_nacimiento",
            "email",
            "activo",
        }

        for campo in campos_modificables:
            if campo in data:
                valor = data[campo]
                if campo == "fecha_nacimiento" and isinstance(valor, str):
                    valor = date.fromisoformat(valor)
                setattr(persona, campo, valor)

        persona.updated_at = datetime.now(timezone.utc)
        commit_or_raise("Ya existe una Persona con el mismo documento o email.")
        return persona

    def eliminar(self, id: int) -> bool:
        persona = self.obtener_por_id(id)
        if persona is None:
            return False

        if persona.usuarios:
            raise DuplicateError(
                f"No se puede eliminar la Persona con id={id} porque tiene "
                f"{len(persona.usuarios)} Usuario(s) asociado(s)."
            )

        db.session.delete(persona)
        commit_or_raise()
        return True
