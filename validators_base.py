def check_required(data: dict, fields: list[str], errores: list[str]) -> None:
    for campo in fields:
        if campo not in data or data.get(campo) is None:
            errores.append(f"El campo '{campo}' es obligatorio.")


def check_str_len(data: dict, campo: str, min_len: int, max_len: int, errores: list[str]) -> None:
    value = data.get(campo)
    if value is not None:
        if not isinstance(value, str) or not (min_len <= len(value) <= max_len):
            errores.append(f"'{campo}' debe ser una cadena de entre {min_len} y {max_len} caracteres.")


def check_str_max(data: dict, campo: str, max_len: int, errores: list[str]) -> None:
    value = data.get(campo)
    if value is not None:
        if not isinstance(value, str) or len(value) > max_len:
            errores.append(f"'{campo}' debe ser una cadena de hasta {max_len} caracteres.")
