from flask import Blueprint

Blueprint_Usuarios = Blueprint("usuarios", __name__)

from usuarios import routes  # noqa: E402, F401
