from datetime import datetime, timezone

from app import db


class Sistema(db.Model):
    __tablename__ = "sistemas"

    id          = db.Column(db.Integer,      primary_key=True)
    nombre      = db.Column(db.String(100),  nullable=False, unique=True)
    descripcion = db.Column(db.String(255),  nullable=True)
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

    permisos = db.relationship(
        "Permiso",
        back_populates="sistema",
        lazy="select",
    )

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "nombre":      self.nombre,
            "descripcion": self.descripcion,
            "created_at":  self.created_at.isoformat(),
            "updated_at":  self.updated_at.isoformat(),
        }
