import re
from datetime import date
from validators_base import check_required, check_str_len

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

CAMPOS_REQUERIDOS = ["nombre", "apellido", "documento", "fecha_nacimiento", "email"]


def validar_persona(data: dict, partial: bool = False) -> list[str]:
    errores: list[str] = []
    if not partial:
        check_required(data, CAMPOS_REQUERIDOS, errores)
    check_str_len(data, "nombre", 1, 100, errores)
    check_str_len(data, "apellido", 1, 100, errores)
    check_str_len(data, "documento", 1, 20, errores)
    email = data.get("email")
    if email is not None:
        if not EMAIL_RE.match(email):
            errores.append("El 'email' tiene formato inválido.")
    fecha_str = data.get("fecha_nacimiento")
    if fecha_str is not None:
        try:
            fecha = date.fromisoformat(fecha_str)
            if fecha > date.today():
                errores.append("'fecha_nacimiento' no puede ser una fecha futura.")
        except ValueError:
            errores.append("'fecha_nacimiento' debe tener formato YYYY-MM-DD.")
    return errores
