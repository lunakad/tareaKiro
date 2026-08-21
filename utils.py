from flask import jsonify


def parse_id(raw: str, status: int = 422):
    try:
        value = int(raw)
        if value <= 0:
            raise ValueError
        return value, None
    except (ValueError, TypeError):
        resp = jsonify({"error": f"El id '{raw}' no es un entero positivo válido."})
        resp.status_code = status
        return None, resp
