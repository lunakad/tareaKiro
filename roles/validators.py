from validators_base import check_required, check_str_len, check_str_max


def validar_rol(data: dict, partial: bool = False) -> list[str]:
    errores: list[str] = []
    if not partial:
        check_required(data, ["nombre"], errores)
    check_str_len(data, "nombre", 1, 50, errores)
    check_str_max(data, "descripcion", 255, errores)
    return errores
