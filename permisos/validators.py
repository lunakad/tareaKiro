from validators_base import check_required, check_str_len, check_str_max


def validar_permiso(data: dict, partial: bool = False) -> list[str]:
    errores: list[str] = []
    if not partial:
        check_required(data, ["nombre", "sistema_id"], errores)
    check_str_len(data, "nombre", 1, 100, errores)
    check_str_max(data, "descripcion", 255, errores)
    sistema_id = data.get("sistema_id")
    if sistema_id is not None:
        if not isinstance(sistema_id, int) or sistema_id <= 0:
            errores.append("'sistema_id' debe ser un entero positivo.")
    return errores
