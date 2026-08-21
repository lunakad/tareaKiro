from datetime import datetime, timezone

from app import db

usuario_roles = db.Table(
    "usuario_roles",
    db.Column(
        "usuario_id",
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    db.Column(
        "rol_id",
        db.Integer,
        db.ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
)


class Rol(db.Model):
    __tablename__ = "roles"

    id          = db.Column(db.Integer,     primary_key=True)
    nombre      = db.Column(db.String(50),  nullable=False, unique=True)
    descripcion = db.Column(db.String(255), nullable=True)
    created_at  = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at  = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    usuarios = db.relationship(
        "Usuario",
        secondary="usuario_roles",
        back_populates="roles",
    )

    permisos = db.relationship(
        "Permiso",
        secondary="rol_permisos",
        back_populates="roles",
        lazy="select",
    )

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "nombre":      self.nombre,
            "descripcion": self.descripcion,
            "permisos":    [p.to_dict() for p in self.permisos],
            "created_at":  self.created_at.isoformat(),
            "updated_at":  self.updated_at.isoformat(),
        }
