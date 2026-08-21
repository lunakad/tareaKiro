from flask import request, jsonify

from sistemas import Blueprint_Sistemas
from sistemas.repository import SistemaRepository
from sistemas.validators import validar_sistema
from exceptions import DatabaseError, DuplicateError
from utils import parse_id

_repo = SistemaRepository()


@Blueprint_Sistemas.route("", methods=["POST"])
def crear_sistema():
    data = request.get_json(silent=True) or {}
    errores = validar_sistema(data)
    if errores:
        return jsonify({"error": "Datos de entrada inválidos.", "details": errores}), 400
    try:
        sistema = _repo.crear(data)
    except DuplicateError as exc:
        return jsonify({"error": str(exc)}), 409
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500
    return jsonify(sistema.to_dict()), 201


@Blueprint_Sistemas.route("", methods=["GET"])
def listar_sistemas():
    try:
        sistemas = _repo.listar_todos()
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500
    return jsonify([s.to_dict() for s in sistemas]), 200


@Blueprint_Sistemas.route("/<id>", methods=["GET"])
def obtener_sistema(id):
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp
    try:
        sistema = _repo.obtener_por_id(parsed_id)
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500
    if sistema is None:
        return jsonify({"error": f"Sistema con id={parsed_id} no encontrado."}), 404
    return jsonify(sistema.to_dict()), 200


@Blueprint_Sistemas.route("/<id>", methods=["PUT"])
def actualizar_sistema(id):
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp
    data = request.get_json(silent=True) or {}
    campos_modificables = {"nombre", "descripcion"}
    campos_recibidos = {k: v for k, v in data.items() if k in campos_modificables}
    if not campos_recibidos:
        return jsonify({"error": "El cuerpo está vacío o no contiene campos modificables reconocidos."}), 400
    errores = validar_sistema(campos_recibidos, partial=True)
    if errores:
        return jsonify({"error": "Datos de entrada inválidos.", "details": errores}), 400
    try:
        sistema = _repo.actualizar(parsed_id, campos_recibidos)
    except DuplicateError as exc:
        return jsonify({"error": str(exc)}), 409
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500
    if sistema is None:
        return jsonify({"error": f"Sistema con id={parsed_id} no encontrado."}), 404
    return jsonify(sistema.to_dict()), 200


@Blueprint_Sistemas.route("/<id>", methods=["DELETE"])
def eliminar_sistema(id):
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp
    try:
        eliminado = _repo.eliminar(parsed_id)
    except DuplicateError as exc:
        return jsonify({"error": str(exc)}), 409
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500
    if not eliminado:
        return jsonify({"error": f"Sistema con id={parsed_id} no encontrado."}), 404
    return "", 204
