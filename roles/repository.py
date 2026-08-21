from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError

from app import db
from roles.models import Rol
from exceptions import DatabaseError, DuplicateError, NotFoundError
from repo_base import commit_or_raise


class RolRepository:

    def crear(self, data: dict) -> Rol:
        rol = Rol(
            nombre=data["nombre"],
            descripcion=data.get("descripcion"),
        )
        db.session.add(rol)
        commit_or_raise(f"Ya existe un Rol con el nombre '{data['nombre']}'.")
        return rol

    def listar_todos(self) -> list:
        try:
            return Rol.query.order_by(Rol.id).all()
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

    def obtener_por_id(self, id: int):
        try:
            return db.session.get(Rol, id)
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

    def actualizar(self, id: int, data: dict):
        rol = self.obtener_por_id(id)
        if rol is None:
            return None

        if "nombre" in data:
            rol.nombre = data["nombre"]
        if "descripcion" in data:
            rol.descripcion = data["descripcion"]

        rol.updated_at = datetime.now(timezone.utc)
        commit_or_raise(f"Ya existe un Rol con el nombre '{data.get('nombre')}'.")
        return rol

    def eliminar(self, id: int) -> bool:
        rol = self.obtener_por_id(id)
        if rol is None:
            return False

        if rol.usuarios:
            raise DuplicateError(
                f"El Rol con id={id} tiene usuarios asignados y no puede eliminarse."
            )

        db.session.delete(rol)
        commit_or_raise()
        return True

    def asignar_a_usuario(self, usuario_id: int, rol_id: int):
        from usuarios.models import Usuario

        usuario = db.session.get(Usuario, usuario_id)
        if usuario is None:
            raise NotFoundError(f"No existe un Usuario con id={usuario_id}.")

        rol = self.obtener_por_id(rol_id)
        if rol is None:
            raise NotFoundError(f"No existe un Rol con id={rol_id}.")

        if rol in usuario.roles:
            raise DuplicateError(
                f"El Rol '{rol.nombre}' ya está asignado al Usuario con id={usuario_id}."
            )

        usuario.roles.append(rol)
        commit_or_raise()
        return usuario

    def desasignar_de_usuario(self, usuario_id: int, rol_id: int) -> bool:
        from usuarios.models import Usuario

        usuario = db.session.get(Usuario, usuario_id)
        if usuario is None:
            raise NotFoundError(f"No existe un Usuario con id={usuario_id}.")

        rol = self.obtener_por_id(rol_id)
        if rol is None:
            raise NotFoundError(f"No existe un Rol con id={rol_id}.")

        if rol not in usuario.roles:
            return False

        usuario.roles.remove(rol)
        commit_or_raise()
        return True

    def listar_roles_de_usuario(self, usuario_id: int) -> list:
        from usuarios.models import Usuario

        try:
            usuario = db.session.get(Usuario, usuario_id)
        except SQLAlchemyError as e:
            raise DatabaseError(str(e)) from e

        if usuario is None:
            raise NotFoundError(f"No existe un Usuario con id={usuario_id}.")

        return usuario.roles
