from flask import request, jsonify

from personas import Blueprint_Personas
from personas.repository import PersonaRepository
from personas.validators import validar_persona
from exceptions import DatabaseError, DuplicateError, NotFoundError
from utils import parse_id

_repo = PersonaRepository()


@Blueprint_Personas.route("", methods=["POST"])
def crear_persona():
    data = request.get_json(silent=True) or {}

    errores = validar_persona(data)
    if errores:
        return jsonify({"error": "Datos de entrada inválidos.", "details": errores}), 400

    try:
        persona = _repo.crear(data)
    except DuplicateError:
        return jsonify({"error": "Ya existe una Persona con el mismo documento o email."}), 409
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    return jsonify(persona.to_dict()), 201


@Blueprint_Personas.route("", methods=["GET"])
def listar_personas():
    try:
        personas = _repo.listar_activos()
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    return jsonify([p.to_dict() for p in personas]), 200


@Blueprint_Personas.route("/<id>", methods=["GET"])
def obtener_persona(id):
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp

    try:
        persona = _repo.obtener_por_id(parsed_id)
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    if persona is None:
        return jsonify({"error": f"Persona con id={parsed_id} no encontrada."}), 404

    return jsonify(persona.to_dict()), 200


@Blueprint_Personas.route("/<id>", methods=["PUT"])
def actualizar_persona(id):
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp

    data = request.get_json(silent=True) or {}

    campos_modificables = {"nombre", "apellido", "documento", "fecha_nacimiento", "email"}
    campos_recibidos = {k: v for k, v in data.items() if k in campos_modificables}

    if not campos_recibidos:
        return jsonify({"error": "El cuerpo de la solicitud está vacío o no contiene campos modificables reconocidos."}), 400

    errores = validar_persona(campos_recibidos, partial=True)
    if errores:
        return jsonify({"error": "Datos de entrada inválidos.", "details": errores}), 400

    try:
        persona = _repo.actualizar(parsed_id, campos_recibidos)
    except DuplicateError:
        return jsonify({"error": "Ya existe una Persona con el mismo documento o email."}), 409
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    if persona is None:
        return jsonify({"error": f"Persona con id={parsed_id} no encontrada."}), 404

    return jsonify(persona.to_dict()), 200


@Blueprint_Personas.route("/<id>", methods=["DELETE"])
def eliminar_persona(id):
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp

    try:
        eliminada = _repo.eliminar(parsed_id)
    except DuplicateError as exc:
        return jsonify({"error": str(exc)}), 409
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    if not eliminada:
        return jsonify({"error": f"Persona con id={parsed_id} no encontrada."}), 404

    return "", 204
