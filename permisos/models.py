from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint

from app import db

rol_permisos = db.Table(
    "rol_permisos",
    db.Column(
        "rol_id",
        db.Integer,
        db.ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    db.Column(
        "permiso_id",
        db.Integer,
        db.ForeignKey("permisos.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
)


class Permiso(db.Model):
    __tablename__ = "permisos"
    __table_args__ = (
        UniqueConstraint("sistema_id", "nombre", name="uq_permiso_sistema_nombre"),
    )

    id          = db.Column(db.Integer,     primary_key=True)
    sistema_id  = db.Column(
        db.Integer,
        db.ForeignKey("sistemas.id"),
        nullable=False,
    )
    nombre      = db.Column(db.String(100), nullable=False)
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

    sistema = db.relationship(
        "Sistema",
        back_populates="permisos",
        lazy="select",
    )

    roles = db.relationship(
        "Rol",
        secondary="rol_permisos",
        back_populates="permisos",
        lazy="select",
    )

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "sistema_id":  self.sistema_id,
            "sistema":     self.sistema.to_dict() if self.sistema else None,
            "nombre":      self.nombre,
            "descripcion": self.descripcion,
            "created_at":  self.created_at.isoformat(),
            "updated_at":  self.updated_at.isoformat(),
        }
