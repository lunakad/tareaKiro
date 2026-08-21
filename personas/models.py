from app import db
from datetime import datetime, timezone


class Persona(db.Model):
    __tablename__ = "personas"

    id               = db.Column(db.Integer, primary_key=True)
    nombre           = db.Column(db.String(100), nullable=False)
    apellido         = db.Column(db.String(100), nullable=False)
    documento        = db.Column(db.String(20),  nullable=False, unique=True)
    fecha_nacimiento = db.Column(db.Date,        nullable=False)
    email            = db.Column(db.String(254), nullable=False, unique=True)
    activo           = db.Column(db.Boolean,     nullable=False, default=True)
    created_at       = db.Column(db.DateTime,    nullable=False,
                                 default=lambda: datetime.now(timezone.utc))
    updated_at       = db.Column(db.DateTime,    nullable=False,
                                 default=lambda: datetime.now(timezone.utc),
                                 onupdate=lambda: datetime.now(timezone.utc))

    usuarios = db.relationship("Usuario", back_populates="persona", lazy="select")

    def to_dict(self):
        return {
            "id":               self.id,
            "nombre":           self.nombre,
            "apellido":         self.apellido,
            "documento":        self.documento,
            "fecha_nacimiento": self.fecha_nacimiento.isoformat(),
            "email":            self.email,
            "activo":           self.activo,
            "created_at":       self.created_at.isoformat(),
            "updated_at":       self.updated_at.isoformat(),
        }
