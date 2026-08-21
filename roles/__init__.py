from flask import Blueprint

Blueprint_Roles = Blueprint("roles", __name__)

from roles import routes  # noqa: E402, F401
