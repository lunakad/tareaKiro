import pytest
from app import create_app, db as _db


@pytest.fixture(scope="function")
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def persona_data():
    """Diccionario con datos válidos por defecto para una Persona."""
    return {
        "nombre": "Juan",
        "apellido": "Pérez",
        "documento": "12345678",
        "fecha_nacimiento": "1990-06-15",
        "email": "juan.perez@example.com",
    }


@pytest.fixture
def usuario_data():
    """Diccionario con datos válidos por defecto para un Usuario.

    Nota: persona_id debe ajustarse a una Persona creada previamente en el test.
    """
    return {
        "persona_id": 1,
        "username": "juanperez",
        "password": "Secreto123",
    }
