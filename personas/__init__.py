from flask import Blueprint

Blueprint_Personas = Blueprint("personas", __name__)

from personas import routes  # noqa: E402, F401
