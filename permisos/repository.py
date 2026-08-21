from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError

from app import db
from permisos.models import Permiso
from exceptions import DatabaseError, DuplicateError, NotFoundError
from repo_base import commit_or_raise


class PermisoRepository:

    def crear(self, data: dict) -> Permiso:
        from sistemas.models import Sistema

        sistema = db.session.get(Sistema, int(data["sistema_id"]))
        if sistema is None:
            raise NotFoundError(
                f"No existe un Sistema con id={data['sistema_id']}."
            )

        permiso = Permiso(
            sistema_id=int(data["sistema_id"]),
            nombre=data["nombre"],
            descripcion=data.get("descripcion"),
        )
        db.session.add(permiso)
        commit_or_raise(
            f"Ya existe un Permiso con nombre '{data['nombre']}' "
            f"en el Sistema con id={data['sistema_id']}."
        )
        return permiso

    def listar_todos(self) -> list:
        try:
            return Permiso.query.order_by(Permiso.sistema_id, Permiso.id).all()
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

    def obtener_por_id(self, id: int):
        try:
            return db.session.get(Permiso, id)
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

    def actualizar(self, id: int, data: dict):
        permiso = self.obtener_por_id(id)
        if permiso is None:
            return None

        if "nombre" in data:
            permiso.nombre = data["nombre"]
        if "descripcion" in data:
            permiso.descripcion = data["descripcion"]

        permiso.updated_at = datetime.now(timezone.utc)
        commit_or_raise("Ya existe un Permiso con ese nombre en el mismo Sistema.")
        return permiso

    def eliminar(self, id: int) -> bool:
        permiso = self.obtener_por_id(id)
        if permiso is None:
            return False
        db.session.delete(permiso)
        commit_or_raise()
        return True

    def asignar_a_rol(self, rol_id: int, permiso_id: int):
        from roles.models import Rol

        rol = db.session.get(Rol, rol_id)
        if rol is None:
            raise NotFoundError(f"No existe un Rol con id={rol_id}.")

        permiso = self.obtener_por_id(permiso_id)
        if permiso is None:
            raise NotFoundError(f"No existe un Permiso con id={permiso_id}.")

        if permiso in rol.permisos:
            raise DuplicateError(
                f"El Permiso '{permiso.nombre}' ya está asignado al Rol con id={rol_id}."
            )

        rol.permisos.append(permiso)
        commit_or_raise()
        return rol

    def desasignar_de_rol(self, rol_id: int, permiso_id: int) -> bool:
        from roles.models import Rol

        rol = db.session.get(Rol, rol_id)
        if rol is None:
            raise NotFoundError(f"No existe un Rol con id={rol_id}.")

        permiso = self.obtener_por_id(permiso_id)
        if permiso is None:
            raise NotFoundError(f"No existe un Permiso con id={permiso_id}.")

        if permiso not in rol.permisos:
            return False

        rol.permisos.remove(permiso)
        commit_or_raise()
        return True

    def listar_permisos_de_rol(self, rol_id: int) -> list:
        from roles.models import Rol

        try:
            rol = db.session.get(Rol, rol_id)
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

        if rol is None:
            raise NotFoundError(f"No existe un Rol con id={rol_id}.")

        return rol.permisos
