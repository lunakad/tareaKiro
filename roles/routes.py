from flask import request, jsonify

from roles import Blueprint_Roles
from roles.repository import RolRepository
from roles.validators import validar_rol
from exceptions import DatabaseError, DuplicateError
from utils import parse_id

_repo = RolRepository()


@Blueprint_Roles.route("", methods=["POST"])
def crear_rol():
    data = request.get_json(silent=True) or {}

    errores = validar_rol(data)
    if errores:
        return jsonify({"error": "Datos de entrada inválidos.", "details": errores}), 400

    try:
        rol = _repo.crear(data)
    except DuplicateError as exc:
        return jsonify({"error": str(exc)}), 409
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    return jsonify(rol.to_dict()), 201


@Blueprint_Roles.route("", methods=["GET"])
def listar_roles():
    try:
        roles = _repo.listar_todos()
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    return jsonify([r.to_dict() for r in roles]), 200


@Blueprint_Roles.route("/<id>", methods=["GET"])
def obtener_rol(id):
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp

    try:
        rol = _repo.obtener_por_id(parsed_id)
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    if rol is None:
        return jsonify({"error": f"Rol con id={parsed_id} no encontrado."}), 404

    return jsonify(rol.to_dict()), 200


@Blueprint_Roles.route("/<id>", methods=["PUT"])
def actualizar_rol(id):
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp

    data = request.get_json(silent=True) or {}

    campos_modificables = {"nombre", "descripcion"}
    campos_recibidos = {k: v for k, v in data.items() if k in campos_modificables}

    if not campos_recibidos:
        return jsonify({
            "error": "El cuerpo de la solicitud está vacío o no contiene campos modificables reconocidos."
        }), 400

    errores = validar_rol(campos_recibidos, partial=True)
    if errores:
        return jsonify({"error": "Datos de entrada inválidos.", "details": errores}), 400

    try:
        rol = _repo.actualizar(parsed_id, campos_recibidos)
    except DuplicateError as exc:
        return jsonify({"error": str(exc)}), 409
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    if rol is None:
        return jsonify({"error": f"Rol con id={parsed_id} no encontrado."}), 404

    return jsonify(rol.to_dict()), 200


@Blueprint_Roles.route("/<id>", methods=["DELETE"])
def eliminar_rol(id):
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
        return jsonify({"error": f"Rol con id={parsed_id} no encontrado."}), 404

    return "", 204


@Blueprint_Roles.route("/<id>/permisos", methods=["GET"])
def listar_permisos_de_rol(id):
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp

    from permisos.repository import PermisoRepository
    from exceptions import NotFoundError

    permiso_repo = PermisoRepository()
    try:
        permisos = permiso_repo.listar_permisos_de_rol(parsed_id)
    except NotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    return jsonify([p.to_dict() for p in permisos]), 200


@Blueprint_Roles.route("/<id>/permisos", methods=["POST"])
def asignar_permiso_a_rol(id):
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp

    data = request.get_json(silent=True) or {}
    permiso_id_raw = data.get("permiso_id")

    if permiso_id_raw is None:
        return jsonify({"error": "El campo 'permiso_id' es obligatorio."}), 400

    if not isinstance(permiso_id_raw, int) or permiso_id_raw <= 0:
        return jsonify({"error": "'permiso_id' debe ser un entero positivo."}), 400

    from permisos.repository import PermisoRepository
    from exceptions import NotFoundError

    permiso_repo = PermisoRepository()
    try:
        rol = permiso_repo.asignar_a_rol(parsed_id, permiso_id_raw)
    except NotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except DuplicateError as exc:
        return jsonify({"error": str(exc)}), 409
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    return jsonify([p.to_dict() for p in rol.permisos]), 200


@Blueprint_Roles.route("/<id>/permisos/<permiso_id>", methods=["DELETE"])
def desasignar_permiso_de_rol(id, permiso_id):
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp

    parsed_permiso_id, err_resp = parse_id(permiso_id)
    if err_resp:
        return err_resp

    from permisos.repository import PermisoRepository
    from exceptions import NotFoundError

    permiso_repo = PermisoRepository()
    try:
        desasignado = permiso_repo.desasignar_de_rol(parsed_id, parsed_permiso_id)
    except NotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    if not desasignado:
        return jsonify({"error": f"El Permiso con id={parsed_permiso_id} no está asignado al Rol con id={parsed_id}."}), 404

    return "", 204
