from flask import request, jsonify

from permisos import Blueprint_Permisos
from permisos.repository import PermisoRepository
from permisos.validators import validar_permiso
from exceptions import DatabaseError, DuplicateError, NotFoundError
from utils import parse_id

_repo = PermisoRepository()


@Blueprint_Permisos.route("", methods=["POST"])
def crear_permiso():
    data = request.get_json(silent=True) or {}
    errores = validar_permiso(data)
    if errores:
        return jsonify({"error": "Datos de entrada inválidos.", "details": errores}), 400
    try:
        permiso = _repo.crear(data)
    except NotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except DuplicateError as exc:
        return jsonify({"error": str(exc)}), 409
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500
    return jsonify(permiso.to_dict()), 201


@Blueprint_Permisos.route("", methods=["GET"])
def listar_permisos():
    try:
        permisos = _repo.listar_todos()
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500
    return jsonify([p.to_dict() for p in permisos]), 200


@Blueprint_Permisos.route("/<id>", methods=["GET"])
def obtener_permiso(id):
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp
    try:
        permiso = _repo.obtener_por_id(parsed_id)
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500
    if permiso is None:
        return jsonify({"error": f"Permiso con id={parsed_id} no encontrado."}), 404
    return jsonify(permiso.to_dict()), 200


@Blueprint_Permisos.route("/<id>", methods=["PUT"])
def actualizar_permiso(id):
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp
    data = request.get_json(silent=True) or {}
    campos_modificables = {"nombre", "descripcion"}
    campos_recibidos = {k: v for k, v in data.items() if k in campos_modificables}
    if not campos_recibidos:
        return jsonify({"error": "El cuerpo está vacío o no contiene campos modificables reconocidos."}), 400
    errores = validar_permiso(campos_recibidos, partial=True)
    if errores:
        return jsonify({"error": "Datos de entrada inválidos.", "details": errores}), 400
    try:
        permiso = _repo.actualizar(parsed_id, campos_recibidos)
    except DuplicateError as exc:
        return jsonify({"error": str(exc)}), 409
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500
    if permiso is None:
        return jsonify({"error": f"Permiso con id={parsed_id} no encontrado."}), 404
    return jsonify(permiso.to_dict()), 200


@Blueprint_Permisos.route("/<id>", methods=["DELETE"])
def eliminar_permiso(id):
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp
    try:
        eliminado = _repo.eliminar(parsed_id)
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500
    if not eliminado:
        return jsonify({"error": f"Permiso con id={parsed_id} no encontrado."}), 404
    return "", 204
