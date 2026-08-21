from flask import Blueprint

Blueprint_Sistemas = Blueprint("sistemas", __name__)

from sistemas import routes  # noqa: E402, F401
