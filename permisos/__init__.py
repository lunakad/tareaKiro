from flask import Blueprint

Blueprint_Permisos = Blueprint("permisos", __name__)

from permisos import routes  # noqa: E402, F401
