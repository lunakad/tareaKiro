from app import db
from datetime import datetime, timezone
import bcrypt


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id            = db.Column(db.Integer,     primary_key=True)
    persona_id    = db.Column(db.Integer,     db.ForeignKey("personas.id"),
                              nullable=False)
    username      = db.Column(db.String(50),  nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime,    nullable=False,
                              default=lambda: datetime.now(timezone.utc))
    updated_at    = db.Column(db.DateTime,    nullable=False,
                              default=lambda: datetime.now(timezone.utc),
                              onupdate=lambda: datetime.now(timezone.utc))

    persona = db.relationship("Persona", back_populates="usuarios")

    roles = db.relationship(
        "Rol",
        secondary="usuario_roles",
        back_populates="usuarios",
        lazy="select",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self.password_hash.encode("utf-8")
        )

    def to_dict(self):
        return {
            "id":         self.id,
            "persona_id": self.persona_id,
            "username":   self.username,
            "roles":      [r.to_dict() for r in self.roles],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
