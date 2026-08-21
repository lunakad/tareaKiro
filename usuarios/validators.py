from validators_base import check_required, check_str_len


def validar_usuario(data: dict, partial: bool = False) -> list[str]:
    errores: list[str] = []
    if not partial:
        check_required(data, ["persona_id", "username", "password"], errores)
    check_str_len(data, "username", 3, 50, errores)
    check_str_len(data, "password", 8, 128, errores)
    return errores
