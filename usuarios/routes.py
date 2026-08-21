from flask import request, jsonify

from usuarios import Blueprint_Usuarios
from usuarios.repository import UsuarioRepository
from usuarios.validators import validar_usuario
from exceptions import DatabaseError, DuplicateError, NotFoundError
from utils import parse_id

_repo = UsuarioRepository()


@Blueprint_Usuarios.route("", methods=["POST"])
def crear_usuario():
    data = request.get_json(silent=True) or {}

    errores = validar_usuario(data)
    if errores:
        return jsonify({"error": "Datos de entrada inválidos.", "details": errores}), 400

    try:
        usuario = _repo.crear(data)
    except NotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except DuplicateError as exc:
        return jsonify({"error": str(exc)}), 409
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    return jsonify(usuario.to_dict()), 201


@Blueprint_Usuarios.route("", methods=["GET"])
def listar_usuarios():
    try:
        usuarios = _repo.listar_todos()
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    return jsonify([u.to_dict() for u in usuarios]), 200


@Blueprint_Usuarios.route("/<id>", methods=["GET"])
def obtener_usuario(id):
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp

    try:
        usuario = _repo.obtener_por_id(parsed_id)
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    if usuario is None:
        return jsonify({"error": f"Usuario con id={parsed_id} no encontrado."}), 404

    return jsonify(usuario.to_dict()), 200


@Blueprint_Usuarios.route("/<id>", methods=["PUT"])
def actualizar_usuario(id):
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp

    data = request.get_json(silent=True) or {}

    campos_modificables = {"username", "password"}
    campos_recibidos = {k: v for k, v in data.items() if k in campos_modificables}

    if not campos_recibidos:
        return jsonify({"error": "El cuerpo de la solicitud está vacío o no contiene campos modificables reconocidos."}), 400

    errores = validar_usuario(campos_recibidos, partial=True)
    if errores:
        return jsonify({"error": "Datos de entrada inválidos.", "details": errores}), 400

    try:
        usuario = _repo.actualizar(parsed_id, campos_recibidos)
    except DuplicateError as exc:
        return jsonify({"error": str(exc)}), 409
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    if usuario is None:
        return jsonify({"error": f"Usuario con id={parsed_id} no encontrado."}), 404

    return jsonify(usuario.to_dict()), 200


@Blueprint_Usuarios.route("/<id>", methods=["DELETE"])
def eliminar_usuario(id):
    parsed_id, err_resp = parse_id(id, status=400)
    if err_resp:
        return err_resp

    try:
        eliminado = _repo.eliminar(parsed_id)
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    if not eliminado:
        return jsonify({"error": f"Usuario con id={parsed_id} no encontrado."}), 404

    return "", 204


@Blueprint_Usuarios.route("/<id>/roles", methods=["GET"])
def listar_roles_usuario(id):
    from roles.repository import RolRepository
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp

    try:
        roles = RolRepository().listar_roles_de_usuario(parsed_id)
    except NotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    return jsonify([r.to_dict() for r in roles]), 200


@Blueprint_Usuarios.route("/<id>/roles", methods=["POST"])
def asignar_rol_usuario(id):
    from roles.repository import RolRepository
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp

    data = request.get_json(silent=True) or {}
    rol_id_raw = data.get("rol_id")

    if rol_id_raw is None:
        return jsonify({"error": "El campo 'rol_id' es obligatorio."}), 400

    try:
        rol_id = int(rol_id_raw)
        if rol_id <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "'rol_id' debe ser un entero positivo válido."}), 400

    try:
        usuario = RolRepository().asignar_a_usuario(parsed_id, rol_id)
    except NotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except DuplicateError as exc:
        return jsonify({"error": str(exc)}), 409
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    return jsonify([r.to_dict() for r in usuario.roles]), 200


@Blueprint_Usuarios.route("/<id>/roles/<rol_id>", methods=["DELETE"])
def desasignar_rol_usuario(id, rol_id):
    from roles.repository import RolRepository
    parsed_id, err_resp = parse_id(id)
    if err_resp:
        return err_resp

    parsed_rol_id, err_resp = parse_id(rol_id)
    if err_resp:
        return err_resp

    try:
        eliminado = RolRepository().desasignar_de_usuario(parsed_id, parsed_rol_id)
    except NotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except DatabaseError as exc:
        return jsonify({"error": "Error interno de base de datos.", "details": [str(exc)]}), 500

    if not eliminado:
        return jsonify({
            "error": f"El Rol con id={parsed_rol_id} no está asignado al Usuario con id={parsed_id}."
        }), 404

    return "", 204
